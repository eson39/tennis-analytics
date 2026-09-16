from datetime import datetime
from typing import Literal

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
