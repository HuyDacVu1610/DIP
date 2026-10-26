"""Single-process export leases, scoped to an app's Engine; never persisted in DB."""
from contextlib import contextmanager
from threading import Lock, RLock
from weakref import WeakKeyDictionary


class SessionBusyError(RuntimeError):
    pass


class _Guards:
    def __init__(self):
        self.mutex = RLock()
        self.exporting = set()


_engines = WeakKeyDictionary()
_registry_mutex = Lock()


def _guards(engine):
    with _registry_mutex:
        if engine not in _engines:
            _engines[engine] = _Guards()
        return _engines[engine]


@contextmanager
def mutation(engine, session_id):
    """Hold only across a short metadata transaction, always before DB access."""
    state = _guards(engine)
    with state.mutex:
        if session_id in state.exporting:
            raise SessionBusyError('Tài liệu đang xuất; chờ hoàn tất rồi thử lại.')
        yield


def require_mutable(engine, session_id):
    """Async routes call via threadpool before entering the occupied CPU queue."""
    with mutation(engine,session_id):
        pass


class ExportLease:
    def __init__(self, state, session_id):
        self._state, self._sid = state, session_id
        self._running = self._released = False

    def start(self):
        with self._state.mutex:
            if self._released:
                return False
            self._running = True
            return True

    def release(self):
        with self._state.mutex:
            if not self._released:
                self._state.exporting.remove(self._sid)
                self._released = True

    def cancel_waiting(self):
        # An HTTP cancellation cannot stop a running worker using snapshot files.
        with self._state.mutex:
            if not self._running:
                self.release()


def reserve_export(engine, session_id):
    state = _guards(engine)
    with state.mutex:
        if session_id in state.exporting:
            raise SessionBusyError('Tài liệu đang xuất; chờ hoàn tất rồi thử lại.')
        state.exporting.add(session_id)
        return ExportLease(state, session_id)
