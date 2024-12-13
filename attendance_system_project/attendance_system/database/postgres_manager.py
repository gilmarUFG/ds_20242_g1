import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Optional
from datetime import datetime, timedelta
from .models import Student, AttendanceRecord, SyncLog
from attendance_system.config.settings import MINUTES_BEFORE_NEXT_CAPTURE
from attendance_system.utils.logging_utils import get_logger

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
        
    def get_all_active_students(self) -> List[Student]:
        """
        Retrieve all active students with their face encodings
        Returns: List of Student objects
        """
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        student_id,
                        enrollment_code,
                        first_name,
                        last_name,
                        face_encoding,
                        face_encoding_updated_at,
                        is_active,
                        created_at,
                        updated_at
                    FROM students 
                    WHERE is_active = true 
                    ORDER BY student_id
                """)
                
                students = []
                for row in cursor.fetchall():
                    student = Student(**dict(row))
                    students.append(student)
                
                logger.info(f"Retrieved {len(students)} active students from database")
                return students
                
        except Exception as e:
            logger.error(f"Error retrieving active students from PostgreSQL: {e}")
            return []

    def get_students_by_ids(self, student_ids: List[str]) -> List[Student]:
        """
        Retrieve specific students by their IDs
        Returns: List of Student objects
        """
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        student_id,
                        enrollment_code,
                        first_name,
                        last_name,
                        face_encoding,
                        face_encoding_updated_at,
                        is_active,
                        created_at,
                        updated_at
                    FROM students 
                    WHERE student_id = ANY(%s)
                    AND is_active = true
                    ORDER BY student_id
                """, (student_ids,))
                
                students = []
                for row in cursor.fetchall():
                    student = Student(**dict(row))
                    students.append(student)
                
                return students
                
        except Exception as e:
            logger.error(f"Error retrieving students by IDs from PostgreSQL: {e}")
            return []

    def update_student_face_encoding(self, student_id: str, face_encoding: str) -> bool:
        """
        Update the face encoding for a specific student
        Returns: Boolean indicating success
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE students 
                    SET face_encoding = %s,
                        face_encoding_updated_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = %s
                    RETURNING student_id
                """, (face_encoding, student_id))
                
                self.connection.commit()
                updated = cursor.fetchone() is not None
                
                if updated:
                    logger.info(f"Updated face encoding for student {student_id}")
                else:
                    logger.warning(f"No student found with ID {student_id}")
                
                return updated
                
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error updating face encoding for student {student_id}: {e}")
            return False

    def add_student(self, student: Student) -> bool:
        """
        Add a new student to the database
        Returns: Boolean indicating success
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO students (
                        student_id,
                        enrollment_code,
                        first_name,
                        last_name,
                        face_encoding,
                        face_encoding_updated_at,
                        is_active,
                        created_at,
                        updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """, (
                    student.student_id,
                    student.enrollment_code,
                    student.first_name,
                    student.last_name,
                    student.face_encoding,
                    student.face_encoding_updated_at,
                    student.is_active
                ))
                
                self.connection.commit()
                logger.info(f"Added new student: {student.student_id}")
                return True
                
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error adding new student: {e}")
            return False

    def deactivate_student(self, student_id: str) -> bool:
        """
        Deactivate a student (soft delete)
        Returns: Boolean indicating success
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE students 
                    SET is_active = false,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = %s
                    RETURNING student_id
                """, (student_id,))
                
                self.connection.commit()
                deactivated = cursor.fetchone() is not None
                
                if deactivated:
                    logger.info(f"Deactivated student {student_id}")
                else:
                    logger.warning(f"No student found with ID {student_id}")
                
                return deactivated
                
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error deactivating student {student_id}: {e}")
            return False
        
    def get_attendance(self, student_id: str, capture_timestamp: str, minutes: int = MINUTES_BEFORE_NEXT_CAPTURE) -> Optional[AttendanceRecord]:
        """Check if an attendance record exists in PostgreSQL within a time window"""
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                # Calculate the start of the time window
                timestamp = datetime.fromisoformat(capture_timestamp)
                start_time = timestamp - timedelta(minutes=minutes)

                cursor.execute("""
                    SELECT *
                    FROM attendance_records
                    WHERE student_id = %s
                    AND capture_timestamp >= %s
                    AND capture_timestamp <= %s
                """, (student_id, start_time.isoformat(), capture_timestamp))

                result = cursor.fetchone()
                if not result:
                    return None
                
                return AttendanceRecord(**dict(result))
                
        except Exception as e:
            logger.error(f"Error checking attendance existence in PostgreSQL: {e}")
            return None