import face_recognition
import numpy as np
import cv2
from datetime import datetime
from typing import Optional, Tuple, List
import base64
from threading import Thread
import queue
from ..utils.logging_utils import get_logger
from ..database.models import Student, AttendanceRecord

logger = get_logger(__name__)

class FaceRecognitionProcessor:
    def __init__(self, device_id: str, recognition_interval: int = 5):
        self.device_id = device_id
        self.recognition_interval = recognition_interval  # seconds
        self.known_face_encodings = {}
        self.known_face_names = {}
        self.last_recognition_times = {}  # To prevent duplicate recognitions
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=1)  # For thread-safe frame sharing
        self.camera = None

    def load_student_faces(self, students: List[Student]):
        """Load student face encodings from database"""
        for student in students:
            if student.face_encoding:
                # Decode base64 stored encoding
                encoding_bytes = base64.b64decode(student.face_encoding)
                face_encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                self.known_face_encodings[student.student_id] = face_encoding
                self.known_face_names[student.student_id] = f"{student.first_name} {student.last_name}"
        
        logger.info(f"Loaded {len(students)} student face encodings")

    def start_camera(self, camera_index: int = 0):
        """Start camera capture in a separate thread"""
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            raise RuntimeError("Could not start camera")
        
        self.is_running = True
        Thread(target=self._camera_thread, daemon=True).start()
        logger.info("Camera capture started")

    def _camera_thread(self):
        """Camera capture thread"""
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                # Keep only the most recent frame
                try:
                    self.frame_queue.get_nowait()  # Remove old frame if exists
                except queue.Empty:
                    pass
                self.frame_queue.put(frame)

    def process_frame(self, frame) -> List[Tuple[str, float, tuple]]:
        """
        Process a single frame for face recognition
        Returns: List of (student_id, confidence, face_location)
        """
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find faces in frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        results = []
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = []
            confidence_scores = []
            
            for student_id, known_encoding in self.known_face_encodings.items():
                # Calculate face distance
                face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                confidence = 1 - face_distance
                
                if confidence > 0.6:  # Confidence threshold
                    matches.append(student_id)
                    confidence_scores.append(confidence)

            if matches:
                # Get the match with highest confidence
                best_match_index = np.argmax(confidence_scores)
                student_id = matches[best_match_index]
                confidence = confidence_scores[best_match_index]
                
                # Scale face location back to original size
                scaled_location = tuple(4 * x for x in face_location)
                results.append((student_id, confidence, scaled_location))

        return results

    def run_recognition(self, callback):
        """
        Main recognition loop
        callback: Function to call when a face is recognized
        """
        try:
            while self.is_running:
                try:
                    frame = self.frame_queue.get(timeout=1)  # Get latest frame
                except queue.Empty:
                    continue

                # Process frame
                recognitions = self.process_frame(frame)
                current_time = datetime.now()

                # Handle recognitions
                for student_id, confidence, face_location in recognitions:
                    # Check if enough time has passed since last recognition for this student
                    if (student_id not in self.last_recognition_times or 
                        (current_time - self.last_recognition_times[student_id]).seconds 
                        >= self.recognition_interval):
                        
                        # Create attendance record
                        attendance_record = AttendanceRecord(
                            student_id=student_id,
                            capture_timestamp=current_time,
                            device_id=self.device_id,
                            confidence_score=float(confidence)
                        )

                        # Update last recognition time
                        self.last_recognition_times[student_id] = current_time

                        # Draw rectangle around face
                        top, right, bottom, left = face_location
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                        # Draw name and confidence
                        name = self.known_face_names.get(student_id, "Unknown")
                        text = f"{name} ({confidence:.2f})"
                        cv2.putText(frame, text, (left, top - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Call callback with attendance record
                        callback(attendance_record)

                # Display frame
                cv2.imshow('Face Recognition', frame)

                # Break loop on 'q' press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            logger.error(f"Error in recognition loop: {e}")
            raise
        finally:
            self.stop()

    def stop(self):
        """Stop face recognition and release resources"""
        self.is_running = False
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
        logger.info("Face recognition stopped")
