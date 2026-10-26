"""One app-local image worker, two queued calls, no persistent jobs/polling."""
import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable


class ProcessingBusyError(RuntimeError):
    code = 'PROCESSING_BUSY'


class ProcessingExecutor:
    """Submit blocking import/detect/render/export use cases from one event loop.

    Cancelling a waiter removes queued work. Once a thread starts, it keeps its
    slot until completion even if its HTTP caller has gone away. Do not submit
    recursively from a worker: one whole use case occupies one slot.
    """
    def __init__(self):
        self._loop = asyncio.get_running_loop()
        self._pool = ThreadPoolExecutor(max_workers=1,thread_name_prefix='scanner-image')
        self._pending = deque()
        self._runner = None
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    def submit(self, function: Callable[...,Any], /, *args, **kwargs) -> asyncio.Future:
        if asyncio.get_running_loop() is not self._loop:
            raise RuntimeError('ProcessingExecutor chỉ dùng trên event loop của ứng dụng.')
        if self._closed:
            raise ProcessingBusyError('Bộ xử lý đang đóng.')
        # Cancelled queued calls must release capacity immediately, before the
        # next event-loop tick, without leaving an unbounded thread-pool queue.
        self._pending = deque(job for job in self._pending if not job[0].cancelled())
        idle = self._runner is None or self._runner.done()
        if not idle and len(self._pending)>=2:
            raise ProcessingBusyError('Bộ xử lý đang bận; tối đa hai tác vụ chờ.')
        future = self._loop.create_future()
        job = future,partial(function,*args,**kwargs)
        if idle:
            self._runner = self._loop.create_task(self._drain(job))
        else:
            self._pending.append(job)
        return future

    async def run(self, function: Callable[...,Any], /, *args, **kwargs):
        return await self.submit(function,*args,**kwargs)

    async def _drain(self, job):
        while job is not None:
            future,call = job
            if not future.cancelled():
                try:
                    result = await self._loop.run_in_executor(self._pool,call)
                except Exception as error:
                    if not future.done():
                        future.set_exception(error)
                else:
                    if not future.done():
                        future.set_result(result)
            job = None
            while self._pending and job is None:
                candidate = self._pending.popleft()
                if not candidate[0].cancelled():
                    job = candidate

    async def aclose(self) -> None:
        """Reject new work, cancel queued calls, finish active work, join thread."""
        self._closed = True
        while self._pending:
            self._pending.popleft()[0].cancel()
        if self._runner is not None:
            await asyncio.shield(self._runner)
        self._pool.shutdown(wait=True,cancel_futures=True)
