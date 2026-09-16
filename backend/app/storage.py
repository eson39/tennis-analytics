import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from app.config import (
    ALLOWED_VIDEO_EXTENSIONS,
    METADATA_DIR,
    VIDEOS_DIR,
    ensure_storage_dirs,
)
from app.schemas import Match, MatchStatus


class StorageError(Exception):
    pass


class MatchNotFoundError(StorageError):
    pass


class InvalidVideoError(StorageError):
    pass


def _metadata_path(match_id: str) -> Path:
    return METADATA_DIR / f"{match_id}.json"


def _video_path(match_id: str, extension: str) -> Path:
    return VIDEOS_DIR / f"{match_id}{extension}"


def _to_match(data: dict) -> Match:
    return Match(
        match_id=data["match_id"],
        status=data["status"],
        original_filename=data["original_filename"],
        content_type=data.get("content_type"),
        file_size_bytes=data["file_size_bytes"],
        created_at=datetime.fromisoformat(data["created_at"]),
        video_url=f"/matches/{data['match_id']}/video",
    )


def list_matches() -> list[Match]:
    ensure_storage_dirs()
    matches: list[Match] = []
    for path in METADATA_DIR.glob("*.json"):
        with path.open("r", encoding="utf-8") as file:
            matches.append(_to_match(json.load(file)))
    matches.sort(key=lambda match: match.created_at, reverse=True)
    return matches


def get_match(match_id: str) -> Match:
    ensure_storage_dirs()
    path = _metadata_path(match_id)
    if not path.exists():
        raise MatchNotFoundError(f"Match {match_id} not found")
    with path.open("r", encoding="utf-8") as file:
        return _to_match(json.load(file))


def get_video_file(match_id: str) -> Path:
    match = get_match(match_id)
    extension = Path(match.original_filename).suffix.lower()
    path = _video_path(match_id, extension)
    if not path.exists():
        raise MatchNotFoundError(f"Video for match {match_id} not found")
    return path


def delete_match(match_id: str) -> None:
    match = get_match(match_id)
    extension = Path(match.original_filename).suffix.lower()
    _video_path(match_id, extension).unlink(missing_ok=True)
    _metadata_path(match_id).unlink(missing_ok=True)


async def save_uploaded_video(upload: UploadFile) -> Match:
    ensure_storage_dirs()

    if not upload.filename:
        raise InvalidVideoError("Uploaded file is missing a filename")

    extension = Path(upload.filename).suffix.lower()
    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_VIDEO_EXTENSIONS))
        raise InvalidVideoError(f"Unsupported video format. Allowed: {allowed}")

    match_id = str(uuid.uuid4())
    video_path = _video_path(match_id, extension)

    size = 0
    with video_path.open("wb") as output:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            output.write(chunk)

    if size == 0:
        video_path.unlink(missing_ok=True)
        raise InvalidVideoError("Uploaded file is empty")

    status: MatchStatus = "uploaded"
    created_at = datetime.now(timezone.utc)
    metadata = {
        "match_id": match_id,
        "status": status,
        "original_filename": upload.filename,
        "content_type": upload.content_type,
        "file_size_bytes": size,
        "created_at": created_at.isoformat(),
    }

    with _metadata_path(match_id).open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return _to_match(metadata)
