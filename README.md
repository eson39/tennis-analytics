# CourtVision

Full-stack tennis match analytics from single-camera footage.

## Current status

**Phase 1** — upload a match video and play it in the browser (`frontend/` + `backend/`).

The existing `dashboard/` and `data/` folders are separate exploratory analytics work (including heatmaps) and are not part of the Phase 1 app.

## Phase 1 architecture

```text
React (Vite)  →  FastAPI  →  local filesystem storage
```

- Videos are stored under `backend/storage/videos/`
- Match metadata is stored as JSON under `backend/storage/metadata/`
- No Redis, Celery, Postgres, or CV pipeline yet — those come in later phases

## Run locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

The Vite dev server proxies `/matches` and `/health` to the API, so you do not need a separate CORS setup for local development beyond what is already configured.

## Phase 1 checklist

1. Start backend and frontend.
2. Open the app and upload an `.mp4` / `.mov` / `.webm` file.
3. Confirm the API returns a `match_id` and the match appears in the list.
4. Confirm the video plays in the browser player.
