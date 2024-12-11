import asyncio
import signal
import sys
import os
import base64
from datetime import datetime, timedelta
from typing import Optional

from attendance_system.database.postgres_manager import PostgresManager
from attendance_system.database.sqlite_manager import SQLiteManager
from attendance_system.services.external_api_service import ExternalAPIService
from attendance_system.services.sync_service import SyncService
from attendance_system.utils.logging_utils import get_logger
from attendance_system.utils.network_utils import is_connected
from attendance_system.config.settings import (
    POSTGRES_CONFIG, SQLITE_PATH, EXTERNAL_API_URL, 
    EXTERNAL_API_KEY, STUDENT_SYNC_INTERVAL,
    ATTENDANCE_SYNC_INTERVAL, CLEANUP_DAYS
)

logger = get_logger(__name__)

class SyncSystem:
    def __init__(self):
        self.running = False
        self.last_student_sync: Optional[datetime] = None
        
        # Initialize database connections
        self.postgres_manager = PostgresManager(POSTGRES_CONFIG)
        self.sqlite_manager = SQLiteManager(SQLITE_PATH)
        
        # Initialize services
        self.external_api_service = ExternalAPIService(
            EXTERNAL_API_URL,
            EXTERNAL_API_KEY
        )
        self.sync_service = SyncService(
            self.postgres_manager,
            self.sqlite_manager,
            self.external_api_service
        )

    async def sync_student_data(self) -> bool:
        """Synchronize student data from PostgreSQL to SQLite"""
        try:
            if not is_connected():
                logger.warning("No internet connection. Student sync skipped.")
                return False
                
            logger.info("Starting student data synchronization...")
            students = self.postgres_manager.get_all_active_students()
            
            if not students:
                logger.warning("No students found in main database")
                return False
                
            success = self.sqlite_manager.sync_student_data(students)
            if success:
                self.last_student_sync = datetime.now()
                logger.info(f"Successfully synced {len(students)} students to local database")
            return success
            
        except Exception as e:
            logger.error(f"Error during student data sync: {e}")
            return False

    async def cleanup_old_records(self):
        """Clean up old synced records"""
        try:
            deleted_count = self.sqlite_manager.cleanup_old_records(CLEANUP_DAYS)
            logger.info(f"Cleaned up {deleted_count} old attendance records")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def sync_faces_with_db(self, faces_directory="faces/"):
        """Synchronize the faces directory with the face_encoding column in the database."""
        logger.info("Starting face synchronization with the database.")
        os.makedirs(faces_directory, exist_ok=True)

        try:
            students = self.postgres_manager.get_all_active_students()
            
            for student in students:
                enrollment_code = student.enrollment_code
                face_encoding = student.face_encoding
                
                try:
                    # Decode the base64 face encoding and save it as a .jpg file
                    face_bytes = base64.b64decode(face_encoding)
                    face_path = os.path.join(faces_directory, f"{enrollment_code}.jpg")
                    
                    if not os.path.exists(face_path):
                        with open(face_path, "wb") as face_file:
                            face_file.write(face_bytes)
                        
                        logger.info(f"Face image for enrollment code {enrollment_code} saved successfully.")
                
                except Exception as e:
                    logger.error(f"Error decoding face for {enrollment_code}: {e}")
        
        except Exception as e:
            logger.error(f"Error synchronizing faces with the database: {e}")

    async def periodic_tasks(self):
        """Run periodic maintenance tasks"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Student sync check
                if (not self.last_student_sync or 
                    current_time - self.last_student_sync > 
                    timedelta(minutes=STUDENT_SYNC_INTERVAL)):
                    await self.sync_student_data()
                
                # Attendance sync
                await self.sync_service.sync_attendance_records()
                
                # Daily cleanup
                if current_time.hour == 0:
                    await self.cleanup_old_records()
                
                logger.info("Faces syncked")
                # Sync faces with the database
                await asyncio.to_thread(self.sync_faces_with_db)
                    
                await asyncio.sleep(60 * ATTENDANCE_SYNC_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in periodic tasks: {e}")
                await asyncio.sleep(60)

    def setup_signal_handlers(self):
        """Set up handlers for graceful shutdown"""
        def handle_shutdown(signum, frame):
            logger.info("Shutdown signal received")
            self.running = False
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    async def start(self):
        """Start the sync system"""
        try:
            self.postgres_manager.connect()
            self.sqlite_manager.connect()
            self.running = True
            self.setup_signal_handlers()
            
            await self.periodic_tasks()
            
        except Exception as e:
            logger.error(f"Error in sync system: {e}")
            raise
        finally:
            self.running = False

async def main():
    try:
        logger.info("Starting Sync System")
        sync_system = SyncSystem()
        await sync_system.start()
    except KeyboardInterrupt:
        logger.info("Sync system shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        logger.info("Sync system shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
