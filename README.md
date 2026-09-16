# CourtVision

Full-stack tennis match analytics from single-camera footage.

## Current focus

**Court keypoints only** — upload a match video and detect 14 court landmarks with a ResNet50 model (same approach as [Tennis-Analysis-System](https://github.com/ameynarwadkar/Tennis-Analysis-System) / [abdullahtarek/tennis_analysis](https://github.com/abdullahtarek/tennis_analysis)).

Player tracking is intentionally removed for now.

## Setup

### Model weights

```bash
pip install gdown
gdown 1QrTOF1ToQ4plsSZbkBs3zOLkVt3MBlta -O models/keypoints_model.pth
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --reload-dir app --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Verify

1. Upload a tennis clip.
2. Wait for status `completed`.
3. Toggle **Court keypoints** on the video — you should see 14 numbered red points.

## Storage

```text
backend/storage/
  videos/{match_id}.mp4
  metadata/{match_id}.json
  court/{match_id}.json
models/
  keypoints_model.pth
```
