from datetime import datetime
from typing import List, Optional
from ..database.models import AttendanceRecord, SyncLog
from ..database.postgres_manager import PostgresManager
from ..database.sqlite_manager import SQLiteManager
from ..utils.network_utils import is_connected
from ..utils.logging_utils import get_logger
from .external_api_service import ExternalAPIService

logger = get_logger(__name__)

class SyncService:
    def __init__(
        self, 
        postgres_manager: PostgresManager,
        sqlite_manager: SQLiteManager,
        external_api_service: ExternalAPIService
    ):
        self.postgres_manager = postgres_manager
        self.sqlite_manager = sqlite_manager
        self.external_api_service = external_api_service

    async def sync_attendance_records(self) -> Optional[SyncLog]:
        """Synchronize pending attendance records"""
        if not is_connected():
            logger.warning("No internet connection available for sync")
            return None

        sync_log = SyncLog(sync_start_timestamp=datetime.now())
        
        try:
            pending_records = self.sqlite_manager.get_pending_attendance_records()
            if not pending_records:
                logger.info("No pending records to sync")
                return None

            sync_log.records_processed = len(pending_records)
            
            for record in pending_records:
                try:
                    existing_attendance = self.postgres_manager.get_attendance(
                        student_id=record.student_id,
                        capture_timestamp=record.capture_timestamp,
                        confidence_score=record.confidence_score
                    )

                    if existing_attendance:
                        self.sqlite_manager.update_attendance_sync_status(
                            record.student_id,
                            record.confidence_score,
                            record.capture_timestamp,
                            'synced'
                        )
                        sync_log.records_succeeded += 1
                        logger.info(f"Record already exists in PostgreSQL, updated SQLite status: {record.attendance_id}")
                        continue

                    external_id = self.external_api_service.register_attendance({
                        "student_id": record.student_id,
                        "timestamp": record.capture_timestamp,
                        "confidence": record.confidence_score
                    })
                    
                    if not external_id:
                        sync_log.records_failed += 1
                        continue

                    # Update PostgreSQL
                    record.sync_status = 'synced'
                    record.sync_timestamp = datetime.now()
                    self.postgres_manager.save_attendance(record)
                    
                    # Update SQLite
                    self.sqlite_manager.update_attendance_sync_status(
                        record.student_id,
                        record.confidence_score,
                        record.capture_timestamp,
                        'synced'
                    )
                    
                    sync_log.records_succeeded += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing record {record.attendance_id}: {e}")
                    sync_log.records_failed += 1
                    continue
                    
            sync_log.sync_status = 'completed'
            sync_log.sync_end_timestamp = datetime.now()
            
        except Exception as e:
            logger.error(f"Sync process failed: {e}")
            sync_log.sync_status = 'failed'
            sync_log.error_message = str(e)
            sync_log.sync_end_timestamp = datetime.now()
            return sync_log
        finally:
            # Save sync log to both databases
            self.postgres_manager.save_sync_log(sync_log)
            self.sqlite_manager.save_sync_log(sync_log)
            
        return sync_log