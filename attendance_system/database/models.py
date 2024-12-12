from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal

@dataclass
class Student:
    student_id: str
    enrollment_code: str
    first_name: str
    last_name: str
    face_encoding: Optional[str] = None
    face_encoding_updated_at: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AttendanceStatus:
    PRESENT = 'present'
    ABSENT = 'absent'
    DISCIPLINE_NOT_FOUND = 'discipline_not_found'
    ALREADY_PRESENT = 'already_present'

@dataclass
class AttendanceRecord:
    student_id: str
    capture_timestamp: datetime
    device_id: str
    confidence_score: float
    attendance_id: Optional[int] = None
    sync_status: str = 'pending'
    sync_timestamp: Optional[datetime] = None
    sync_attempts: int = 0
    attendance_status: Optional[Literal[AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.DISCIPLINE_NOT_FOUND, AttendanceStatus.ALREADY_PRESENT]] = None
    last_sync_error: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class SyncLog:
    sync_start_timestamp: datetime
    log_id: Optional[int] = None
    sync_end_timestamp: Optional[datetime] = None
    records_processed: int = 0
    records_succeeded: int = 0
    records_failed: int = 0
    sync_status: str = 'in_progress'
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None