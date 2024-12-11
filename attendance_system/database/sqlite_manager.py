import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
from .models import Student, AttendanceRecord, SyncLog
from attendance_system.utils.logging_utils import get_logger

logger = get_logger(__name__)

class SQLiteManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info("Connected to SQLite database")
            self._create_tables()
        except Exception as e:
            logger.error(f"Error connecting to SQLite: {e}")
            raise

    def _create_tables(self):
        """Ensure all required tables exist"""
        try:
            with self.connection:
                self.connection.executescript('''
                    CREATE TABLE IF NOT EXISTS students (
                        student_id TEXT PRIMARY KEY,
                        enrollment_code TEXT UNIQUE,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        face_encoding TEXT,
                        face_encoding_updated_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS attendance_records (
                        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        capture_timestamp TIMESTAMP NOT NULL,
                        device_id TEXT NOT NULL,
                        confidence_score REAL,
                        sync_status TEXT DEFAULT 'pending',
                        sync_timestamp TIMESTAMP,
                        sync_attempts INTEGER DEFAULT 0,
                        last_sync_error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (student_id) REFERENCES students(student_id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_attendance_student_id 
                        ON attendance_records(student_id);
                    CREATE INDEX IF NOT EXISTS idx_attendance_sync_status 
                        ON attendance_records(sync_status);
                ''')
                logger.info("SQLite tables created/verified")
        except Exception as e:
            logger.error(f"Error creating SQLite tables: {e}")
            raise

    def get_all_active_students(self) -> List[Student]:
        """Retrieve all active students with their face encodings"""
        try:
            with self.connection:
                cursor = self.connection.execute("""
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
                    WHERE is_active = 1 
                    AND face_encoding IS NOT NULL
                    ORDER BY student_id
                """)
                
                students = [Student(**dict(row)) for row in cursor.fetchall()]
                logger.info(f"Retrieved {len(students)} active students from SQLite")
                return students
                
        except Exception as e:
            logger.error(f"Error retrieving active students from SQLite: {e}")
            return []

    def has_recent_attendance(self, student_id: str, capture_timestamp: str, minutes: int = 10) -> bool:
        """
        Check if a student has any attendance record within the specified time window
        """
        try:
            recent_attendance = self.connection.execute("""
                SELECT attendance_id 
                FROM attendance_records 
                WHERE student_id = ? 
                AND capture_timestamp >= datetime(?, ?) 
                AND capture_timestamp <= ?
            """, (
                student_id,
                capture_timestamp,
                f'-{minutes} minutes',
                capture_timestamp
            )).fetchone()
            
            return recent_attendance is not None

        except Exception as e:
            logger.error(f"Error checking recent attendance: {e}")
            return False

    def save_attendance(self, attendance: AttendanceRecord) -> Optional[int]:
        """Save attendance record to SQLite if no recent attendance exists"""
        try:
            cursor = self.connection.execute("""
                SELECT student_id FROM students WHERE enrollment_code = ?
            """, (attendance.student_id,))
            student_row = cursor.fetchone()

            if not student_row:
                logger.error(f"Student with enrollment_code {attendance.student_id} not found")
                return None

            student_id = student_row['student_id']
            
            if self.has_recent_attendance(student_id, attendance.capture_timestamp):
                logger.info(f"Ignored duplicate attendance for student {student_id} within 10 minutes")
                return None

            with self.connection:
                cursor = self.connection.execute("""
                    INSERT INTO attendance_records (
                        student_id,
                        capture_timestamp,
                        device_id,
                        confidence_score,
                        sync_status,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    student_id,
                    attendance.capture_timestamp,
                    attendance.device_id,
                    attendance.confidence_score,
                    attendance.sync_status
                ))
                attendance_id = cursor.lastrowid
                logger.info(f"Saved attendance record {attendance_id} to SQLite")
                return attendance_id

        except Exception as e:
            logger.error(f"Error saving attendance record to SQLite: {e}")
            return None



    def get_pending_attendance_records(self) -> List[AttendanceRecord]:
        """Retrieve all pending attendance records for synchronization"""
        try:
            with self.connection:
                cursor = self.connection.execute("""
                    SELECT * FROM attendance_records 
                    WHERE sync_status = 'pending'
                    ORDER BY capture_timestamp
                """)
                
                records = [AttendanceRecord(**dict(row)) for row in cursor.fetchall()]
                logger.info(f"Retrieved {len(records)} pending attendance records")
                return records
                
        except Exception as e:
            logger.error(f"Error retrieving pending attendance records: {e}")
            return []

    def update_attendance_sync_status(self, student_id: int, confidence_score: float, capture_timestamp: str, 
                                    status: str, error_message: str = None) -> bool:
        """Update sync status of an attendance record"""
        try:
            with self.connection:
                self.connection.execute("""
                    UPDATE attendance_records 
                    SET sync_status = ?,
                        sync_timestamp = CURRENT_TIMESTAMP,
                        sync_attempts = sync_attempts + 1,
                        last_sync_error = ?
                    WHERE student_id = ?
                    AND confidence_score = ?
                    AND capture_timestamp = ?
                """, (status, error_message, student_id, confidence_score, capture_timestamp))
                
                logger.info(f"Updated sync status for attendance {student_id} to {status}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating attendance sync status: {e}")
            return False

    def sync_student_data(self, students: List[Student]) -> bool:
        """Synchronize student data from central database"""
        try:
            with self.connection:
                # Create temporary table for bulk update
                self.connection.execute("""
                    CREATE TEMPORARY TABLE temp_students (
                        student_id TEXT PRIMARY KEY,
                        enrollment_code TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        face_encoding TEXT,
                        face_encoding_updated_at TIMESTAMP,
                        is_active BOOLEAN,
                        updated_at TIMESTAMP
                    )
                """)
                
                # Insert into temporary table
                self.connection.executemany("""
                    INSERT INTO temp_students VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [(
                    s.student_id,
                    s.enrollment_code,
                    s.first_name,
                    s.last_name,
                    s.face_encoding,
                    s.face_encoding_updated_at,
                    s.is_active,
                    datetime.now()
                ) for s in students])
                
                # Update existing records
                self.connection.execute("""
                    UPDATE students
                    SET enrollment_code = temp.enrollment_code,
                        first_name = temp.first_name,
                        last_name = temp.last_name,
                        face_encoding = temp.face_encoding,
                        face_encoding_updated_at = temp.face_encoding_updated_at,
                        is_active = temp.is_active,
                        updated_at = temp.updated_at
                    FROM temp_students temp
                    WHERE students.student_id = temp.student_id
                """)
                
                # Insert new records
                self.connection.execute("""
                    INSERT INTO students
                    SELECT 
                        temp.student_id,
                        temp.enrollment_code,
                        temp.first_name,
                        temp.last_name,
                        temp.face_encoding,
                        temp.face_encoding_updated_at,
                        temp.is_active,
                        CURRENT_TIMESTAMP,
                        temp.updated_at
                    FROM temp_students temp
                    LEFT JOIN students s ON temp.student_id = s.student_id
                    WHERE s.student_id IS NULL
                """)
                
                # Drop temporary table
                self.connection.execute("DROP TABLE temp_students")
                
                logger.info(f"Synchronized {len(students)} students to SQLite")
                return True
                
        except Exception as e:
            logger.error(f"Error synchronizing student data: {e}")
            return False

    def cleanup_old_records(self, days_to_keep: int = 30) -> int:
        """Remove old synced attendance records"""
        try:
            with self.connection:
                cursor = self.connection.execute("""
                    DELETE FROM attendance_records 
                    WHERE sync_status = 'synced'
                    AND capture_timestamp < date('now', ?)
                """, (f'-{days_to_keep} days',))
                
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old attendance records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old records: {e}")
            return 0

    def get_student_attendance_stats(self, student_id: str, 
                                   start_date: datetime, 
                                   end_date: datetime) -> Dict:
        """Get attendance statistics for a student"""
        try:
            with self.connection:
                cursor = self.connection.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        SUM(CASE WHEN sync_status = 'synced' THEN 1 ELSE 0 END) as synced_records,
                        AVG(confidence_score) as avg_confidence
                    FROM attendance_records
                    WHERE student_id = ?
                    AND capture_timestamp BETWEEN ? AND ?
                """, (student_id, start_date, end_date))
                
                return dict(cursor.fetchone())
                
        except Exception as e:
            logger.error(f"Error retrieving attendance stats: {e}")
            return {}
        
    def save_sync_log(self, sync_log: SyncLog) -> Optional[int]:
        """
        Save synchronization log to SQLite database
        Returns the log_id if successful, None otherwise
        """
        try:
            with self.connection:
                cursor = self.connection.execute("""
                    INSERT INTO sync_logs (
                        sync_start_timestamp,
                        sync_end_timestamp,
                        records_processed,
                        records_succeeded,
                        records_failed,
                        sync_status,
                        error_message,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    sync_log.sync_start_timestamp,
                    sync_log.sync_end_timestamp,
                    sync_log.records_processed,
                    sync_log.records_succeeded,
                    sync_log.records_failed,
                    sync_log.sync_status,
                    sync_log.error_message
                ))
                
                log_id = cursor.lastrowid
                logger.info(f"Sync log saved to SQLite with ID: {log_id}")
                return log_id
                
        except Exception as e:
            logger.error(f"Error saving sync log to SQLite: {e}")
            return None

    def get_last_sync_log(self) -> Optional[SyncLog]:
        """
        Retrieve the most recent sync log
        """
        try:
            with self.connection:
                cursor = self.connection.execute("""
                    SELECT * FROM sync_logs 
                    ORDER BY sync_start_timestamp DESC 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                return SyncLog(**dict(result)) if result else None
        except Exception as e:
            logger.error(f"Error retrieving last sync log from SQLite: {e}")
            return None

    def get_sync_logs_by_date_range(self, start_date: datetime, end_date: datetime) -> List[SyncLog]:
        """
        Retrieve sync logs within a specified date range
        """
        try:
            with self.connection:
                cursor = self.connection.execute("""
                    SELECT * FROM sync_logs 
                    WHERE sync_start_timestamp BETWEEN ? AND ?
                    ORDER BY sync_start_timestamp DESC
                """, (start_date, end_date))
                
                return [SyncLog(**dict(row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error retrieving sync logs by date range from SQLite: {e}")
            return []

    def update_sync_log_status(self, log_id: int, status: str, error_message: Optional[str] = None) -> bool:
        """
        Update the status and error message of a sync log
        """
        try:
            with self.connection:
                self.connection.execute("""
                    UPDATE sync_logs 
                    SET sync_status = ?,
                        error_message = ?,
                        sync_end_timestamp = CURRENT_TIMESTAMP
                    WHERE log_id = ?
                """, (status, error_message, log_id))
                
                logger.info(f"Sync log {log_id} status updated to {status}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating sync log status in SQLite: {e}")
            return False

    def cleanup_old_sync_logs(self, days_to_keep: int = 30) -> int:
        """
        Remove sync logs older than the specified number of days
        Returns the number of deleted records
        """
        try:
            with self.connection:
                cursor = self.connection.execute("""
                    DELETE FROM sync_logs 
                    WHERE sync_start_timestamp < date('now', ?)
                """, (f'-{days_to_keep} days',))
                
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old sync logs")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old sync logs from SQLite: {e}")
            return 0