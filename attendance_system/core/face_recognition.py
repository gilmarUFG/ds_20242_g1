import face_recognition
import numpy as np
from typing import Optional
import base64
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class FaceRecognitionProcessor:
    def __init__(self):
        self.known_face_encodings = {}
        self.known_face_ids = {}

    def add_face(self, student_id: str, face_image_path: str) -> Optional[str]:
        try:
            image = face_recognition.load_image_file(face_image_path)
            face_encoding = face_recognition.face_encodings(image)[0]
            
            # Convert face encoding to base64 for storage
            encoding_bytes = base64.b64encode(face_encoding.tobytes())
            encoding_str = encoding_bytes.decode('utf-8')
            
            self.known_face_encodings[student_id] = face_encoding
            return encoding_str
        except Exception as e:
            logger.error(f"Error processing face for student {student_id}: {e}")
            return None

    def verify_face(self, image_path: str, student_id: str) -> tuple[bool, float]:
        try:
            if student_id not in self.known_face_encodings:
                return False, 0.0

            unknown_image = face_recognition.load_image_file(image_path)
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

            # Compare faces
            results = face_recognition.face_distance(
                [self.known_face_encodings[student_id]], 
                unknown_encoding
            )
            
            confidence = 1 - results[0]
            is_match = confidence > 0.6  # Threshold can be adjusted

            return is_match, confidence
        except Exception as e:
            logger.error(f"Error verifying face: {e}")
            return False, 0.0