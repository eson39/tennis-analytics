from __future__ import annotations

import threading
from collections.abc import Callable


_lock = threading.Lock()
_active: set[str] = set()


def enqueue_match_processing(match_id: str, worker: Callable[[str], None]) -> None:
    """
    Run CV work off the request thread.

    This is intentionally simpler than Celery/Redis (Phase 8). It still keeps
    heavy inference out of FastAPI request handlers.
    """

    with _lock:
        if match_id in _active:
            return
        _active.add(match_id)

    def _run() -> None:
        try:
            worker(match_id)
        finally:
            with _lock:
                _active.discard(match_id)

    thread = threading.Thread(
        target=_run,
        name=f"courtvision-process-{match_id[:8]}",
        daemon=True,
    )
    thread.start()
