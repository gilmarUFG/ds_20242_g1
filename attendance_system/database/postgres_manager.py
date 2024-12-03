import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Optional
from .models import Student, AttendanceRecord, SyncLog
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class PostgresManager:
    def __init__(self, connection_params: dict):
        self.connection_params = connection_params
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def get_student(self, student_id: str) -> Optional[Student]:
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM students WHERE student_id = %s",
                (student_id,)
            )
            result = cursor.fetchone()
            return Student(**dict(result)) if result else None

    def save_attendance(self, attendance: AttendanceRecord) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO attendance_records 
                (student_id, capture_timestamp, device_id, confidence_score, sync_status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING attendance_id
            """, (
                attendance.student_id,
                attendance.capture_timestamp,
                attendance.device_id,
                attendance.confidence_score,
                attendance.sync_status
            ))
            attendance_id = cursor.fetchone()[0]
            self.connection.commit()
            return attendance_id

    def save_sync_log(self, sync_log: SyncLog) -> Optional[int]:
        """
        Save synchronization log to PostgreSQL database
        Returns the log_id if successful, None otherwise
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sync_logs (
                        sync_start_timestamp,
                        sync_end_timestamp,
                        records_processed,
                        records_succeeded,
                        records_failed,
                        sync_status,
                        error_message,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                    ) RETURNING log_id
                """, (
                    sync_log.sync_start_timestamp,
                    sync_log.sync_end_timestamp,
                    sync_log.records_processed,
                    sync_log.records_succeeded,
                    sync_log.records_failed,
                    sync_log.sync_status,
                    sync_log.error_message
                ))
                
                log_id = cursor.fetchone()[0]
                self.connection.commit()
                logger.info(f"Sync log saved to PostgreSQL with ID: {log_id}")
                return log_id
                
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error saving sync log to PostgreSQL: {e}")
            return None

    def get_last_sync_log(self) -> Optional[SyncLog]:
        """
        Retrieve the most recent sync log
        """
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM sync_logs 
                    ORDER BY sync_start_timestamp DESC 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                return SyncLog(**dict(result)) if result else None
        except Exception as e:
            logger.error(f"Error retrieving last sync log from PostgreSQL: {e}")
            return None