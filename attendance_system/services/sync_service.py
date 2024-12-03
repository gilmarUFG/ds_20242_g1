from datetime import datetime
from typing import List
from ..database.models import AttendanceRecord, SyncLog
from ..database.postgres_manager import PostgresManager
from ..database.sqlite_manager import SQLiteManager
from ..utils.network_utils import is_connected
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class SyncService:
    def __init__(
        self, 
        postgres_manager: PostgresManager,
        sqlite_manager: SQLiteManager,
        external_api_service: 'ExternalAPIService'
    ):
        self.postgres_manager = postgres_manager
        self.sqlite_manager = sqlite_manager
        self.external_api_service = external_api_service

    async def sync_attendance_records(self) -> SyncLog:
        if not is_connected():
            logger.warning("No internet connection available for sync")
            return None

        sync_log = SyncLog(sync_start_timestamp=datetime.now())
        
        try:
            # Get pending records from SQLite
            pending_records = self.sqlite_manager.get_pending_attendance_records()
            
            sync_log.records_processed = len(pending_records)
            
            for record in pending_records:
                try:
                    # Send to external API
                    external_id = self.external_api_service.register_attendance({
                        "student_id": record.student_id,
                        "timestamp": record.capture_timestamp.isoformat(),
                        "confidence": record.confidence_score
                    })
                    
                    if external_id:
                        # Update PostgreSQL
                        record.sync_status = 'synced'
                        record.sync_timestamp = datetime.now()
                        self.postgres_manager.save_attendance(record)
                        
                        # Update SQLite
                        self.sqlite_manager.update_attendance_sync_status(
                            record.attendance_id,
                            'synced'
                        )
                        
                        sync_log.records_succeeded += 1
                    else:
                        sync_log.records_failed += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing record {record.attendance_id}: {e}")
                    sync_log.records_failed += 1
                    
            sync_log.sync_status = 'completed'
            sync_log.sync_end_timestamp = datetime.now()
            
        except Exception as e:
            logger.error(f"Sync process failed: {e}")
            sync_log.sync_status = 'failed'
            sync_log.error_message = str(e)
            sync_log.sync_end_timestamp = datetime.now()
            
        finally:
            # Save sync log to both databases
            self.postgres_manager.save_sync_log(sync_log)
            self.sqlite_manager.save_sync_log(sync_log)
            
        return sync_log