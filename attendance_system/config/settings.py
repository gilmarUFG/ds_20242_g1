import os
from pathlib import Path

# Database configurations
POSTGRES_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "attendance_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "changeme"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5435")
}

# SQLite configuration
BASE_DIR = Path(__file__).resolve().parent.parent
SQLITE_PATH = str(BASE_DIR / "attendance.db")

# External API configuration
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "http://localhost:8000/api")
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "your-api-key")

# Face recognition configuration
FACE_RECOGNITION_THRESHOLD = 0.6

# Device configuration
DEVICE_ID = os.getenv("DEVICE_ID", "DEVICE_001")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))

# Sync intervals (in minutes)
STUDENT_SYNC_INTERVAL = int(os.getenv("STUDENT_SYNC_INTERVAL", "60"))  # 1 hour
ATTENDANCE_SYNC_INTERVAL = int(os.getenv("ATTENDANCE_SYNC_INTERVAL", "5"))  # 5 minutes

# Data retention (in days)
CLEANUP_DAYS = int(os.getenv("CLEANUP_DAYS", "30"))

# Face recognition settings
FACE_RECOGNITION_THRESHOLD = float(os.getenv("FACE_RECOGNITION_THRESHOLD", "0.6"))