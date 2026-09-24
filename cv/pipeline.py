from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2

from cv.court.detector import CourtLineDetector
from cv.players.tracker import PlayerTracker, PlayerTrackerConfig


ProgressCallback = Callable[[str, float, str | None], None]


@dataclass
class PipelineResult:
    court: dict | None
    tracking: dict | None
    status: str
    error: str | None = None


def run_pipeline(
    video_path: Path,
    *,
    court_model_path: Path,
    yolo_model_path: str = "yolov8x.pt",
    frame_stride: int = 1,
    on_progress: ProgressCallback | None = None,
) -> PipelineResult:
    """
    Court keypoints + player tracking pipeline.

    Player selection follows Tennis-Analysis-System:
    YOLO persist tracking → choose 2 IDs closest to court keypoints → lock them.
    """

    def progress(status: str, pct: float, message: str | None = None) -> None:
        if on_progress:
            on_progress(status, pct, message)

    progress("processing", 0.02, "Opening video")
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return PipelineResult(
            court=None,
            tracking=None,
            status="failed",
            error="Could not open video file",
        )

    fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    progress("processing", 0.08, "Detecting court keypoints")
    court_detector = CourtLineDetector(court_model_path)
    court_source_index = max(frame_count // 2, 0) if frame_count > 0 else 0
    capture.set(cv2.CAP_PROP_POS_FRAMES, court_source_index)
    ok, court_frame = capture.read()
    if not ok:
        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ok, court_frame = capture.read()
        court_source_index = 0
    if not ok:
        capture.release()
        return PipelineResult(
            court=None,
            tracking=None,
            status="failed",
            error="Could not read a frame for court detection",
        )

    try:
        keypoints = court_detector.predict_points(court_frame)
    except Exception as exc:  # noqa: BLE001
        capture.release()
        return PipelineResult(
            court=None,
            tracking=None,
            status="failed",
            error=f"Court keypoint prediction failed: {exc}",
        )

    court_payload = {
        "method": "resnet50_keypoints",
        "num_keypoints": len(keypoints),
        "keypoints": keypoints,
        "frame_index": court_source_index,
        "frame_width": width,
        "frame_height": height,
        "fps": fps,
        "frame_count": frame_count,
    }

    progress("processing", 0.18, "Tracking players with YOLO")
    tracker = PlayerTracker(
        PlayerTrackerConfig(model_path=yolo_model_path, max_players=2)
    )

    # Fresh pass from the start so YOLO persist IDs are consistent.
    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
    raw_detections: list[dict[int, list[float]]] = []
    frame_indices: list[int] = []
    frame_index = 0
    processed = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_index % max(frame_stride, 1) != 0:
            frame_index += 1
            continue

        raw_detections.append(tracker.detect_frame(frame))
        frame_indices.append(frame_index)
        processed += 1
        if frame_count > 0 and processed % 10 == 0:
            pct = 0.18 + 0.65 * min(1.0, frame_index / max(frame_count, 1))
            progress("processing", pct, f"Tracking players ({frame_index}/{frame_count})")
        frame_index += 1

    capture.release()

    if not raw_detections:
        return PipelineResult(
            court=court_payload,
            tracking=None,
            status="completed",
            error="Court detected, but no frames were available for player tracking",
        )

    # Choose players on the sample closest to the court keypoint frame.
    selection_frame_index = min(
        range(len(frame_indices)),
        key=lambda i: abs(frame_indices[i] - court_source_index),
    )

    progress("analyzing", 0.88, "Selecting two players closest to court")
    chosen_ids, filtered = tracker.choose_and_filter_players(
        keypoints,
        raw_detections,
        selection_frame_index=selection_frame_index,
    )

    if len(chosen_ids) < 1:
        return PipelineResult(
            court=court_payload,
            tracking=None,
            status="completed",
            error="Court detected, but no players could be locked for tracking",
        )

    frames_out = []
    for sample_i, frame_dict in enumerate(filtered):
        source_frame_index = frame_indices[sample_i]
        timestamp_ms = int(round((source_frame_index / fps) * 1000.0)) if fps > 0 else 0
        players = tracker.to_display_players(frame_dict, chosen_ids)
        frames_out.append(
            {
                "frame_index": source_frame_index,
                "timestamp_ms": timestamp_ms,
                "players": players,
            }
        )

    tracking_payload = {
        "fps": fps,
        "frame_width": width,
        "frame_height": height,
        "frame_count": frame_count,
        "frame_stride": frame_stride,
        "chosen_source_track_ids": chosen_ids,
        "frames": frames_out,
    }

    progress("analyzing", 1.0, "Player tracking complete")
    warning = None
    if len(chosen_ids) < 2:
        warning = f"Only locked {len(chosen_ids)} player track(s); expected 2"

    return PipelineResult(
        court=court_payload,
        tracking=tracking_payload,
        status="completed",
        error=warning,
    )
