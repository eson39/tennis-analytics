from __future__ import annotations

import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
for path in (REPO_ROOT, BACKEND_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from app.config import COURT_MODEL_PATH, FRAME_STRIDE, YOLO_MODEL_NAME  # noqa: E402
from app.storage import (  # noqa: E402
    get_video_file,
    save_court,
    save_tracking,
    update_match_fields,
)
from cv.pipeline import run_pipeline  # noqa: E402


def process_match(match_id: str) -> None:
    """Run court keypoints + locked 2-player tracking for a match."""
    try:
        update_match_fields(
            match_id,
            status="processing",
            progress=0.0,
            error_message=None,
            has_tracking=False,
            has_court=False,
        )

        video_path = get_video_file(match_id)

        def on_progress(status: str, pct: float, message: str | None) -> None:
            update_match_fields(
                match_id,
                status=status,  # type: ignore[arg-type]
                progress=round(pct, 3),
                error_message=message,
            )

        result = run_pipeline(
            video_path,
            court_model_path=COURT_MODEL_PATH,
            yolo_model_path=YOLO_MODEL_NAME,
            frame_stride=FRAME_STRIDE,
            on_progress=on_progress,
        )

        if result.status == "failed" or result.court is None:
            update_match_fields(
                match_id,
                status="failed",
                progress=1.0,
                error_message=result.error or "Processing failed",
                has_tracking=False,
                has_court=False,
            )
            return

        save_court(match_id, result.court)
        has_tracking = result.tracking is not None
        if result.tracking is not None:
            save_tracking(match_id, result.tracking)

        update_match_fields(
            match_id,
            status="completed",
            progress=1.0,
            error_message=result.error,
            has_tracking=has_tracking,
            has_court=True,
        )
    except Exception as exc:  # noqa: BLE001
        update_match_fields(
            match_id,
            status="failed",
            progress=1.0,
            error_message=str(exc),
            has_tracking=False,
            has_court=False,
        )
        debug_path = BACKEND_ROOT / "storage" / "metadata" / f"{match_id}.error.log"
        try:
            debug_path.write_text(
                "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
                encoding="utf-8",
            )
        except OSError:
            pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m workers.process_match <match_id>")
        raise SystemExit(1)
    process_match(sys.argv[1])
