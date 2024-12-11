import os
from dotenv import load_dotenv
from pathlib import Path

# Dotenv variables
load_dotenv()

# Database configurations
POSTGRES_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "sslmode": os.getenv("POSTGRES_SSLMODE"),
    "sslrootcert": os.getenv("POSTGRES_SSLROOTCERT")
}

# SQLite configuration
BASE_DIR = Path(__file__).resolve().parent.parent
SQLITE_PATH = str(BASE_DIR / "attendance.db")

# External API configuration
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "http://localhost:8000/api")
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "your-api-key")

# Face recognition configuration
FACE_RECOGNITION_THRESHOLD = 95

# Device configuration
DEVICE_ID = os.getenv("DEVICE_ID", "DEVICE_001")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))

# Sync intervals (in minutes)
STUDENT_SYNC_INTERVAL = int(os.getenv("STUDENT_SYNC_INTERVAL", "1"))  # 1 hour 60
ATTENDANCE_SYNC_INTERVAL = int(os.getenv("ATTENDANCE_SYNC_INTERVAL", "1"))  # 5 minutes 5

# Data retention (in days)
CLEANUP_DAYS = int(os.getenv("CLEANUP_DAYS", "30"))
