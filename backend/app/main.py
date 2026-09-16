from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import ensure_storage_dirs
from app.schemas import Match, MatchCreateResponse
from app.storage import (
    InvalidVideoError,
    MatchNotFoundError,
    delete_match,
    get_match,
    get_video_file,
    list_matches,
    save_uploaded_video,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_storage_dirs()
    yield


app = FastAPI(title="CourtVision API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/matches", response_model=MatchCreateResponse)
async def create_match(file: UploadFile = File(...)) -> MatchCreateResponse:
    try:
        match = await save_uploaded_video(file)
    except InvalidVideoError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return MatchCreateResponse(
        match_id=match.match_id,
        status=match.status,
        original_filename=match.original_filename,
        created_at=match.created_at,
    )


@app.get("/matches", response_model=list[Match])
def get_matches() -> list[Match]:
    return list_matches()


@app.get("/matches/{match_id}", response_model=Match)
def get_match_by_id(match_id: str) -> Match:
    try:
        return get_match(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/matches/{match_id}", status_code=204)
def remove_match(match_id: str) -> None:
    try:
        delete_match(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/matches/{match_id}/video")
def stream_match_video(match_id: str) -> FileResponse:
    try:
        video_path = get_video_file(match_id)
        match = get_match(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    media_type = match.content_type or "video/mp4"
    return FileResponse(
        path=video_path,
        media_type=media_type,
        filename=match.original_filename,
    )
