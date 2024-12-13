import threading
from attendance_system.core.face_recognition import FaceRecognitionProcessor
from attendance_system.database.sqlite_manager import SQLiteManager
from attendance_system.utils.logging_utils import get_logger
from attendance_system.config.settings import DEVICE_ID, CAMERA_INDEX, SQLITE_PATH

logger = get_logger(__name__)

class CameraSystem:
    def __init__(self):
        self.running = False
        self.face_recognition = FaceRecognitionProcessor(
            device_id=DEVICE_ID,
            recognition_interval=5
        )
        self.sqlite_manager = SQLiteManager(SQLITE_PATH)
        
    def handle_recognition(self, attendance_record):
        """Handle face recognition events"""
        try:
            attendance_id = self.sqlite_manager.save_attendance(attendance_record)
            if attendance_id:
                logger.info(
                    f"Attendance recorded locally for student "
                    f"{attendance_record.student_id} with ID: {attendance_id}"
                )
        except Exception as e:
            logger.error(f"Error handling recognition: {e}")

    def start(self):
        """Start the camera system"""
        try:
            self.running = True
            self.sqlite_manager.connect()
            
            # Start camera and recognition
            self.face_recognition.start_camera(camera_index=CAMERA_INDEX)
            self.face_recognition.run_recognition(self.handle_recognition)
            
        except Exception as e:
            logger.error(f"Error in camera system: {e}")
            self.stop()
            raise
            
    def stop(self):
        """Stop the camera system"""
        self.running = False
        if self.face_recognition:
            self.face_recognition.stop()
        logger.info("Camera system stopped")

def main():
    try:
        logger.info("Starting Camera System")
        camera_system = CameraSystem()
        camera_system.start()
    except KeyboardInterrupt:
        logger.info("Camera system shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        logger.info("Camera system shutdown complete")

if __name__ == "__main__":
    main()
