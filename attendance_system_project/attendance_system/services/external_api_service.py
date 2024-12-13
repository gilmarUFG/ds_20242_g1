import requests
from typing import Dict, Optional
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class ExternalAPIService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def register_attendance(self, attendance_data: Dict) -> Optional[Dict]:
        try:
            response = requests.post(
                f"{self.base_url}/register_attendance",
                json=attendance_data,
                headers=self.headers
            )
            
            # Check for successful response (HTTP 200)
            if response.status_code != 200:
                logger.error(f"API returned status code {response.status_code}. Message: {response.text}")
                return None
                
            # Parse and validate response
            response_data = response.json()
            required_fields = ['student_id', 'timestamp', 'confidence', 'attendance_status']
            
            if not all(field in response_data for field in required_fields):
                logger.error("API response missing required fields")
                return None
                
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling external API: {e}")
            return None
        except ValueError as e:
            logger.error(f"Error parsing API response: {e}")
            return None