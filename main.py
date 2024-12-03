import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import signal
import sys

from attendance_system.database.postgres_manager import PostgresManager
from attendance_system.database.sqlite_manager import SQLiteManager
from attendance_system.core.face_recognition import FaceRecognitionProcessor
from attendance_system.services.external_api_service import ExternalAPIService
from attendance_system.services.sync_service import SyncService
from attendance_system.utils.logging_utils import get_logger
from attendance_system.utils.network_utils import is_connected
from attendance_system.config.settings import (
    POSTGRES_CONFIG,
    SQLITE_PATH,
    EXTERNAL_API_URL,
    EXTERNAL_API_KEY,
    DEVICE_ID,
    CAMERA_INDEX,
    STUDENT_SYNC_INTERVAL,  # in minutes
    ATTENDANCE_SYNC_INTERVAL,  # in minutes
    CLEANUP_DAYS
)

logger = get_logger(__name__)

class AttendanceSystem:
    def __init__(self):
        self.running = False
        self.last_student_sync: Optional[datetime] = None
        self.initialization_lock = threading.Lock()
        self.initialized = False

        # Initialize database connections
        self.postgres_manager = PostgresManager(POSTGRES_CONFIG)
        self.sqlite_manager = SQLiteManager(SQLITE_PATH)
        
        # Initialize services
        self.face_recognition = FaceRecognitionProcessor(
            device_id=DEVICE_ID,
            recognition_interval=5  # seconds between recognitions for same person
        )
        self.external_api_service = ExternalAPIService(
            EXTERNAL_API_URL,
            EXTERNAL_API_KEY
        )
        self.sync_service = SyncService(
            self.postgres_manager,
            self.sqlite_manager,
            self.external_api_service
        )

    async def initialize_system(self):
        """Initialize the system and perform initial synchronization"""
        with self.initialization_lock:
            if self.initialized:
                return

        try:
            logger.info("Starting Attendance System")
            attendance_system = AttendanceSystem()
            face_recognition = FaceRecognitionProcessor(device_id=DEVICE_ID)
            attendance_system.start()
        except KeyboardInterrupt:
            logger.info("System shutdown requested")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)
        finally:
            logger.info("System shutdown complete")

    async def sync_student_data(self) -> bool:
        """Synchronize student data from PostgreSQL to SQLite"""
        try:
            if not is_connected():
                logger.warning("No internet connection. Student sync skipped.")
                return False

            logger.info("Starting student data synchronization...")
            
            # Get all active students from PostgreSQL
            students = self.postgres_manager.get_all_active_students()
            if not students:
                logger.warning("No students found in main database")
                return False

            # Sync to SQLite
            success = self.sqlite_manager.sync_student_data(students)
            if success:
                self.last_student_sync = datetime.now()
                logger.info(f"Successfully synced {len(students)} students to local database")
            else:
                logger.error("Failed to sync students to local database")

            return success

        except Exception as e:
            logger.error(f"Error during student data sync: {e}")
            return False

    def handle_recognition(self, attendance_record):
        """Handle face recognition events"""
        try:
            # Save to local database
            
            attendance_id = self.sqlite_manager.save_attendance(attendance_record)
            if attendance_id:
                logger.info(
                    f"Attendance recorded locally for student "
                    f"{attendance_record.student_id} with ID: {attendance_id}"
                )
                
                # Try immediate sync if online
                if is_connected():
                    asyncio.create_task(self.sync_service.sync_attendance_records())
                
        except Exception as e:
            logger.error(f"Error handling recognition: {e}")

    async def cleanup_old_records(self):
        """Clean up old synced records"""
        try:
            deleted_count = self.sqlite_manager.cleanup_old_records(CLEANUP_DAYS)
            logger.info(f"Cleaned up {deleted_count} old attendance records")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def periodic_tasks(self):
        """Run periodic maintenance tasks"""
        while self.running:
            print("CALLEEECALLEEECALLEEECALLEEECALLEEECALLEEECALLEEECALLEEE")
            try:
                current_time = datetime.now()

                # Check if student sync is needed
                if (not self.last_student_sync or 
                    current_time - self.last_student_sync > 
                    timedelta(minutes=STUDENT_SYNC_INTERVAL)):
                    await self.sync_student_data()

                # Sync attendance records
                await self.sync_service.sync_attendance_records()

                # Cleanup old records daily
                if current_time.hour == 0:  # At midnight
                    await self.cleanup_old_records()

                # Wait for next sync interval
                await asyncio.sleep(60 * ATTENDANCE_SYNC_INTERVAL)

            except Exception as e:
                logger.error(f"Error in periodic tasks: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    def setup_signal_handlers(self):
        """Set up handlers for graceful shutdown"""
        def handle_shutdown(signum, frame):
            logger.info("Shutdown signal received")
            self.running = False
            self.face_recognition.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

    # async def start(self):
    def start(self):
        """Start the attendance system"""
        try:
            # Initialize system synchronously
            self.postgres_manager.connect()
            self.sqlite_manager.connect()
            
            self.running = True
            self.setup_signal_handlers()
            
            # Start the camera and face recognition
            self.face_recognition.start_camera(camera_index=CAMERA_INDEX)
            self.face_recognition.run_recognition(self.handle_recognition)  # main func of module
            
            # Run the periodic tasks if the event loop isn't already running
            if not asyncio.get_event_loop().is_running():
                loop = asyncio.get_event_loop()
                loop.create_task(self.periodic_tasks())  # This schedules periodic_tasks to run asynchronously
                loop.run_forever()
            else:
                asyncio.create_task(self.periodic_tasks())  # In case the loop is already running, just create the task
            
        except Exception as e:
            logger.error(f"Error in attendance system: {e}")
            raise
        finally:
            self.running = False
            self.face_recognition.stop()



def main():
    """Main entry point for the application"""
    try:
        logger.info("Starting Attendance System")
        attendance_system = AttendanceSystem()
        
        # Run initialization asynchronously
        loop = asyncio.get_event_loop()
        loop.run_until_complete(attendance_system.initialize_system())
        
        # Start the system
        attendance_system.start()
        
    except KeyboardInterrupt:
        logger.info("System shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("System shutdown complete")


if __name__ == "__main__":
    main()
