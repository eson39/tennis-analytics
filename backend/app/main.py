from contextlib import asynccontextmanager
import sys
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

# Ensure repo-root packages (`cv`, `workers`) are importable when uvicorn runs
# from the backend directory.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import ensure_storage_dirs
from app.jobs import enqueue_match_processing
from app.schemas import (
    CourtResponse,
    Match,
    MatchCreateResponse,
    MatchStatusResponse,
    TrackingResponse,
)
from app.storage import (
    InvalidVideoError,
    MatchNotFoundError,
    delete_match,
    get_court,
    get_match,
    get_tracking,
    get_video_file,
    list_matches,
    save_uploaded_video,
    update_match_fields,
)
from workers.process_match import process_match


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_storage_dirs()
    yield


app = FastAPI(title="CourtVision API", version="0.2.0", lifespan=lifespan)

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

    enqueue_match_processing(match.match_id, process_match)

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


@app.get("/matches/{match_id}/status", response_model=MatchStatusResponse)
def get_match_status(match_id: str) -> MatchStatusResponse:
    try:
        match = get_match(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return MatchStatusResponse(
        match_id=match.match_id,
        status=match.status,
        progress=match.progress,
        error_message=match.error_message,
        has_tracking=match.has_tracking,
        has_court=match.has_court,
    )


@app.post("/matches/{match_id}/process", response_model=MatchStatusResponse)
def reprocess_match(match_id: str) -> MatchStatusResponse:
    try:
        match = update_match_fields(
            match_id,
            status="queued",
            progress=0.0,
            error_message=None,
            has_tracking=False,
            has_court=False,
        )
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    enqueue_match_processing(match_id, process_match)
    return MatchStatusResponse(
        match_id=match.match_id,
        status=match.status,
        progress=match.progress,
        error_message=match.error_message,
        has_tracking=match.has_tracking,
        has_court=match.has_court,
    )


@app.get("/matches/{match_id}/court", response_model=CourtResponse)
def get_match_court(match_id: str) -> CourtResponse:
    try:
        get_match(match_id)
        court = get_court(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return CourtResponse(match_id=match_id, court=court)


@app.get("/matches/{match_id}/tracking", response_model=TrackingResponse)
def get_match_tracking(match_id: str) -> TrackingResponse:
    try:
        get_match(match_id)
        tracking = get_tracking(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return TrackingResponse(match_id=match_id, tracking=tracking)


@app.delete("/matches/{match_id}", status_code=204)
def remove_match(match_id: str) -> Response:
    try:
        delete_match(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=204)


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
