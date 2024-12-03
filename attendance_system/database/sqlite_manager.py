import sqlite3
from typing import List, Optional
from .models import Student, AttendanceRecord, SyncLog
from ..utils.logging_utils import get_logger
from datetime import datetime

logger = get_logger(__name__)

class SQLiteManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info("Connected to SQLite database")
        except Exception as e:
            logger.error(f"Error connecting to SQLite: {e}")
            raise

    def get_pending_attendance_records(self) -> List[AttendanceRecord]:
        with self.connection:
            cursor = self.connection.execute(
                "SELECT * FROM attendance_records WHERE sync_status = 'pending'"
            )
            return [AttendanceRecord(**dict(row)) for row in cursor.fetchall()]
        
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