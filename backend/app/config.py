from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent
STORAGE_DIR = BASE_DIR / "storage"
VIDEOS_DIR = STORAGE_DIR / "videos"
METADATA_DIR = STORAGE_DIR / "metadata"
COURT_DIR = STORAGE_DIR / "court"

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".avi"}

COURT_MODEL_PATH = REPO_ROOT / "models" / "keypoints_model.pth"


def ensure_storage_dirs() -> None:
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    COURT_DIR.mkdir(parents=True, exist_ok=True)
