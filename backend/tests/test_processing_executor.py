"""Bounded one-worker execution, cancellation and application lifecycle."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Event, get_ident

from fastapi import Request
from fastapi.testclient import TestClient
import pytest

from app.main import create_app
from app.services.processing_executor import ProcessingBusyError, ProcessingExecutor


def test_single_worker_fifo_two_waiters_and_overload():
    async def scenario():
        executor = ProcessingExecutor()
        started,release = Event(),Event()
        calls = []
        loop_thread = get_ident()
        def blocking():
            calls.append(('first',get_ident()))
            started.set()
            assert release.wait(3)
            return 1
        def work(label):
            calls.append((label,get_ident()))
            return label
        try:
            first = executor.submit(blocking)
            assert await asyncio.to_thread(started.wait,2)
            second = executor.submit(work,'second')
            third = executor.submit(work,'third')
            with pytest.raises(ProcessingBusyError):
                executor.submit(work,'overflow')
            await asyncio.sleep(0)  # loop can progress while worker blocks
            assert [c[0] for c in calls]==['first']
            release.set()
            assert await asyncio.gather(first,second,third)==[1,'second','third']
            assert [c[0] for c in calls]==['first','second','third']
            assert len({c[1] for c in calls})==1 and calls[0][1]!=loop_thread
        finally:
            release.set()
            await executor.aclose()
    asyncio.run(scenario())


def test_queued_cancellation_returns_slot_and_never_executes_cancelled_work():
    async def scenario():
        executor = ProcessingExecutor()
        started,release = Event(),Event()
        calls = []
        def blocking():
            started.set()
            assert release.wait(3)
        try:
            first = executor.submit(blocking)
            assert await asyncio.to_thread(started.wait,2)
            cancelled = executor.submit(calls.append,'cancelled')
            third = executor.submit(calls.append,'third')
            cancelled.cancel()
            # Accept immediately, without waiting for a cancellation callback tick.
            replacement = executor.submit(calls.append,'replacement')
            with pytest.raises(ProcessingBusyError):
                executor.submit(calls.append,'overflow')
            release.set()
            await asyncio.gather(first,third,replacement)
            assert calls==['third','replacement'] and cancelled.cancelled()
        finally:
            release.set()
            await executor.aclose()
    asyncio.run(scenario())


def test_cancelled_running_caller_does_not_release_worker_early():
    async def scenario():
        executor = ProcessingExecutor()
        started,release = Event(),Event()
        calls = []
        def blocking():
            started.set()
            assert release.wait(3)
            calls.append('active-finished')
        try:
            caller = asyncio.create_task(executor.run(blocking))
            assert await asyncio.to_thread(started.wait,2)
            caller.cancel()
            with pytest.raises(asyncio.CancelledError):
                await caller
            second = executor.submit(calls.append,'second')
            third = executor.submit(calls.append,'third')
            with pytest.raises(ProcessingBusyError):
                executor.submit(calls.append,'overflow')
            assert not second.done() and calls==[]
            release.set()
            await asyncio.gather(second,third)
            assert calls==['active-finished','second','third']
        finally:
            release.set()
            await executor.aclose()
    asyncio.run(scenario())


def test_exception_releases_slot_and_shutdown_cancels_waiters_waits_active():
    async def scenario():
        executor = ProcessingExecutor()
        def fail():
            raise ValueError('controlled worker error')
        with pytest.raises(ValueError,match='controlled'):
            await executor.run(fail)
        assert await executor.run(pow,2,5)==32
        started,release = Event(),Event()
        calls = []
        def blocking():
            started.set()
            assert release.wait(3)
            calls.append('finished')
        try:
            active = executor.submit(blocking)
            assert await asyncio.to_thread(started.wait,2)
            queued = executor.submit(calls.append,'must-not-run')
            closing = asyncio.create_task(executor.aclose())
            await asyncio.sleep(0)
            assert queued.cancelled() and not closing.done()
            with pytest.raises(ProcessingBusyError):
                executor.submit(pow,2,4)
            release.set()
            await closing
            await active
            await executor.aclose()  # idempotent
            assert calls==['finished']
        finally:
            release.set()
            await executor.aclose()
    asyncio.run(scenario())


def test_app_shared_executor_overload_is_429_and_health_is_responsive(tmp_path):
    app = create_app(tmp_path/'scanner.sqlite3')
    started,release = Event(),Event()
    def blocking():
        started.set()
        assert release.wait(5)
        return {'finished':True}
    @app.post('/test-only/image-work')
    async def image_work(request: Request):
        return await request.app.state.processing.run(blocking)
    with TestClient(app) as client, ThreadPoolExecutor(max_workers=1) as caller:
        active = caller.submit(client.post,'/test-only/image-work')
        try:
            assert started.wait(2)
            pending = client.portal.call(lambda:[app.state.processing.submit(lambda:1) for _ in range(2)])
            response = client.post('/test-only/image-work')
            assert response.status_code==429
            assert response.json()['error']['code']=='PROCESSING_BUSY'
            assert client.get('/api/v1/health').json()=={'status':'ok'}
            client.portal.call(lambda:pending[0].cancel())
        finally:
            release.set()
        assert active.result(timeout=3).status_code==200
    assert app.state.processing.closed
