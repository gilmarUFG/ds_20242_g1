import asyncio
from pathlib import Path
from attendance_system.database.postgres_manager import PostgresManager
from attendance_system.database.sqlite_manager import SQLiteManager
from attendance_system.core.face_recognition import FaceRecognitionProcessor
from attendance_system.services.external_api_service import ExternalAPIService
from attendance_system.services.sync_service import SyncService
from attendance_system.utils.logging_utils import get_logger
from attendance_system.config.settings import (
    POSTGRES_CONFIG,
    SQLITE_PATH,
    EXTERNAL_API_URL,
    EXTERNAL_API_KEY
)

logger = get_logger(__name__)

class AttendanceSystem:
    def __init__(self):
        # Initialize database connections
        self.postgres_manager = PostgresManager(POSTGRES_CONFIG)
        self.sqlite_manager = SQLiteManager(SQLITE_PATH)
        
        # Initialize services
        self.face_recognition = FaceRecognitionProcessor()
        self.external_api_service = ExternalAPIService(
            EXTERNAL_API_URL,
            EXTERNAL_API_KEY
        )
        self.sync_service = SyncService(
            self.postgres_manager,
            self.sqlite_manager,
            self.external_api_service
        )

    async def start(self):
        try:
            # Connect to databases
            self.postgres_manager.connect()
            self.sqlite_manager.connect()
            
            # Start periodic sync
            while True:
                await self.sync_service.sync_attendance_records()
                await asyncio.sleep(300)  # Sync every 5 minutes
                
        except Exception as e:
            logger.error(f"Error in attendance system: {e}")
            raise

if __name__ == "__main__":
    attendance_system = AttendanceSystem()
    asyncio.run(attendance_system.start())