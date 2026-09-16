from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

MatchStatus = Literal["uploaded", "queued", "processing", "analyzing", "completed", "failed"]


class MatchCreateResponse(BaseModel):
    match_id: str
    status: MatchStatus
    original_filename: str
    created_at: datetime


class Match(BaseModel):
    match_id: str
    status: MatchStatus
    original_filename: str
    content_type: str | None = None
    file_size_bytes: int
    created_at: datetime
    video_url: str = Field(
        description="API path the frontend can use to stream this match video"
    )
    progress: float | None = None
    error_message: str | None = None
    has_tracking: bool = False
    has_court: bool = False


class MatchStatusResponse(BaseModel):
    match_id: str
    status: MatchStatus
    progress: float | None = None
    error_message: str | None = None
    has_tracking: bool = False
    has_court: bool = False


class CourtResponse(BaseModel):
    match_id: str
    court: dict[str, Any]
