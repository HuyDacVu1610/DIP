from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import uuid4
import pytest
from app.services.session_guards import mutation, reserve_export, SessionBusyError
from test_render_service import setup


def test_export_excludes_same_document_mutations_and_second_export_but_not_reads_or_other_document(setup):
    engine,_,sid,_,_=setup
    lease=reserve_export(engine,sid)
    try:
        assert lease.start()
        with pytest.raises(SessionBusyError):reserve_export(engine,sid)
        with pytest.raises(SessionBusyError):
            with mutation(engine,sid):pytest.fail('must not enter')
        with mutation(engine,uuid4()):pass
        lease.cancel_waiting()  # running work must keep the lease
        with pytest.raises(SessionBusyError):reserve_export(engine,sid)
    finally:lease.release()
    with mutation(engine,sid):pass
    reserve_export(engine,sid).release()


def test_cancel_before_worker_claim_prevents_late_start_and_does_not_release_successor(setup):
    engine,_,sid,_,_=setup
    first=reserve_export(engine,sid);first.cancel_waiting();assert not first.start()
    second=reserve_export(engine,sid)
    try:
        first.release()
        with pytest.raises(SessionBusyError):reserve_export(engine,sid)
    finally:second.release()


def test_reservation_waits_for_transaction_already_in_progress(setup):
    engine,_,sid,_,_=setup;started,release=Event(),Event()
    def write():
        with mutation(engine,sid):
            started.set();assert release.wait(5)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(write)
        try:
            assert started.wait(3)
            pending=pool.submit(reserve_export,engine,sid)
            assert not pending.done()
        finally:release.set()
        first.result(timeout=5);pending.result(timeout=5).release()
