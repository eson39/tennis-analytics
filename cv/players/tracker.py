from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO


def get_center_of_bbox(bbox: list[float] | tuple[float, float, float, float]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def get_foot_position(bbox: list[float] | tuple[float, float, float, float]) -> tuple[float, float]:
    x1, _, x2, y2 = bbox
    return ((x1 + x2) / 2.0, y2)


def measure_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


@dataclass
class PlayerTrackerConfig:
    model_path: str = "yolov8x.pt"
    max_players: int = 2
    # Keep showing last known box briefly when YOLO misses a locked ID.
    hold_missing_frames: int = 90
    person_class_name: str = "person"
    confidence: float = 0.25


class PlayerTracker:
    """
    Player tracking modeled on Tennis-Analysis-System:

    1. YOLO `.track(..., persist=True)` for stable track IDs
    2. Choose the 2 people closest to court keypoints
    3. Keep only those IDs for the rest of the video
    4. Hold last-known boxes briefly so locked players don't "disappear"
    """

    def __init__(self, config: PlayerTrackerConfig | None = None) -> None:
        self.config = config or PlayerTrackerConfig()
        self.model = YOLO(self.config.model_path)

    def detect_frame(self, frame: np.ndarray) -> dict[int, list[float]]:
        results = self.model.track(
            frame,
            persist=True,
            conf=self.config.confidence,
            verbose=False,
        )[0]
        names = results.names
        player_dict: dict[int, list[float]] = {}

        if results.boxes is None:
            return player_dict

        for box in results.boxes:
            if box.id is None:
                continue
            cls_id = int(box.cls.tolist()[0])
            cls_name = names.get(cls_id, str(cls_id))
            if cls_name != self.config.person_class_name:
                continue
            track_id = int(box.id.tolist()[0])
            player_dict[track_id] = [float(v) for v in box.xyxy.tolist()[0]]

        return player_dict

    def detect_frames(
        self,
        frames: list[np.ndarray],
        *,
        on_progress=None,
    ) -> list[dict[int, list[float]]]:
        detections: list[dict[int, list[float]]] = []
        total = max(len(frames), 1)
        for index, frame in enumerate(frames):
            detections.append(self.detect_frame(frame))
            if on_progress and index % 10 == 0:
                on_progress(index / total)
        return detections

    def choose_players(
        self,
        court_keypoints: list[list[float]],
        player_dict: dict[int, list[float]],
    ) -> list[int]:
        """Pick up to 2 track IDs closest to any court keypoint (same idea as the reference repo)."""
        if not player_dict:
            return []

        distances: list[tuple[int, float]] = []
        for track_id, bbox in player_dict.items():
            # Foot is usually closer to the court surface than bbox center.
            player_point = get_foot_position(bbox)
            min_distance = float("inf")
            for point in court_keypoints:
                dist = measure_distance(player_point, (float(point[0]), float(point[1])))
                if dist < min_distance:
                    min_distance = dist
            distances.append((track_id, min_distance))

        distances.sort(key=lambda item: item[1])
        return [track_id for track_id, _ in distances[: self.config.max_players]]

    def choose_and_filter_players(
        self,
        court_keypoints: list[list[float]],
        player_detections: list[dict[int, list[float]]],
        *,
        selection_frame_index: int = 0,
    ) -> tuple[list[int], list[dict[int, list[float]]]]:
        """
        Lock 2 player IDs from a selection frame, then keep only those IDs.

        Also holds the last seen box for locked IDs across short gaps so tracking
        does not visually drop when YOLO briefly misses a player.
        """
        chosen: list[int] = []
        # Prefer the provided selection frame; otherwise first frame with enough people.
        candidate_indices = [selection_frame_index] + list(range(len(player_detections)))
        seen: set[int] = set()
        for idx in candidate_indices:
            if idx < 0 or idx >= len(player_detections) or idx in seen:
                continue
            seen.add(idx)
            chosen = self.choose_players(court_keypoints, player_detections[idx])
            if len(chosen) >= min(self.config.max_players, 1):
                break

        if not chosen:
            return [], [{} for _ in player_detections]

        last_known: dict[int, list[float]] = {}
        missing_count: dict[int, int] = {track_id: 0 for track_id in chosen}
        filtered: list[dict[int, list[float]]] = []

        for frame_dict in player_detections:
            output: dict[int, list[float]] = {}
            for track_id in chosen:
                if track_id in frame_dict:
                    bbox = frame_dict[track_id]
                    last_known[track_id] = bbox
                    missing_count[track_id] = 0
                    output[track_id] = bbox
                elif (
                    track_id in last_known
                    and missing_count[track_id] < self.config.hold_missing_frames
                ):
                    missing_count[track_id] += 1
                    output[track_id] = last_known[track_id]
                else:
                    missing_count[track_id] += 1
            filtered.append(output)

        return chosen, filtered

    @staticmethod
    def to_display_players(
        frame_dict: dict[int, list[float]],
        chosen_ids: list[int],
    ) -> list[dict]:
        """
        Map locked YOLO IDs to stable Player 1 / Player 2 labels.
        Player 1 = nearer camera (larger foot y), Player 2 = farther.
        """
        ordered = sorted(
            ((track_id, bbox) for track_id, bbox in frame_dict.items() if track_id in chosen_ids),
            key=lambda item: get_foot_position(item[1])[1],
            reverse=True,
        )
        players = []
        for display_id, (track_id, bbox) in enumerate(ordered, start=1):
            foot = get_foot_position(bbox)
            center = get_center_of_bbox(bbox)
            players.append(
                {
                    "track_id": display_id,
                    "source_track_id": track_id,
                    "bbox": [round(v, 2) for v in bbox],
                    "center": [round(center[0], 2), round(center[1], 2)],
                    "foot": [round(foot[0], 2), round(foot[1], 2)],
                }
            )
        return players
