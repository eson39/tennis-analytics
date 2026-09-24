# CourtVision

Full-stack tennis match analytics from single-camera footage.

## Current focus

- ResNet50 court keypoints (14 landmarks)
- YOLOv8x player tracking with persistent IDs
- Lock exactly 2 players closest to the court keypoints (same strategy as [Tennis-Analysis-System](https://github.com/ameynarwadkar/Tennis-Analysis-System))

## Setup

### Model weights

```bash
pip install gdown
gdown 1QrTOF1ToQ4plsSZbkBs3zOLkVt3MBlta -O models/keypoints_model.pth
```

YOLOv8x weights download automatically on first run.

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
2. Wait for `completed`.
3. Toggle court keypoints / player boxes / foot markers.
4. Confirm at most two player boxes (P1 near, P2 far) stay locked through the rally.
