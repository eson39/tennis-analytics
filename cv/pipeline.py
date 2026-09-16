from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2

from cv.court.detector import CourtLineDetector


ProgressCallback = Callable[[str, float, str | None], None]


@dataclass
class PipelineResult:
    court: dict | None
    status: str
    error: str | None = None


def run_pipeline(
    video_path: Path,
    *,
    court_model_path: Path,
    on_progress: ProgressCallback | None = None,
) -> PipelineResult:
    """Court-only pipeline: sample frames → ResNet50 keypoints → save artifact."""

    def progress(status: str, pct: float, message: str | None = None) -> None:
        if on_progress:
            on_progress(status, pct, message)

    progress("processing", 0.05, "Opening video")
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return PipelineResult(
            court=None,
            status="failed",
            error="Could not open video file",
        )

    fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    # Prefer a mid-rally frame; fall back to the start.
    sample_indices: list[int]
    if frame_count > 1:
        mid = frame_count // 2
        sample_indices = sorted(
            {
                0,
                mid,
                min(frame_count - 1, mid + int(max(fps, 1))),
            }
        )
    else:
        sample_indices = [0]

    progress("processing", 0.2, "Loading court keypoint model")
    detector = CourtLineDetector(court_model_path)

    progress("processing", 0.45, "Predicting court keypoints")
    best_points: list[list[float]] | None = None
    best_frame_index = 0
    last_error: str | None = None

    for idx in sample_indices:
        capture.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = capture.read()
        if not ok:
            continue
        try:
            points = detector.predict_points(frame)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            continue
        # Keep the first successful prediction; mid-frame is preferred by order.
        best_points = points
        best_frame_index = idx
        break

    capture.release()

    if best_points is None:
        return PipelineResult(
            court=None,
            status="failed",
            error=last_error or "Court keypoint prediction failed",
        )

    progress("analyzing", 0.9, "Saving court keypoints")
    court_payload = {
        "method": "resnet50_keypoints",
        "num_keypoints": len(best_points),
        "keypoints": best_points,
        "frame_index": best_frame_index,
        "frame_width": width,
        "frame_height": height,
        "fps": fps,
        "frame_count": frame_count,
    }

    progress("analyzing", 1.0, "Court detection complete")
    return PipelineResult(court=court_payload, status="completed", error=None)
