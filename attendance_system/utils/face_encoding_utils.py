import numpy as np
import base64
from typing import Optional, Tuple
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

def numpy_to_base64(arr: np.ndarray) -> str:
    """Convert numpy array to base64 string"""
    return base64.b64encode(arr.tobytes()).decode('utf-8')

def base64_to_numpy(base64_str: str) -> np.ndarray:
    """Convert base64 string back to numpy array"""
    encoded_bytes = base64.b64decode(base64_str)
    return np.frombuffer(encoded_bytes, dtype=np.float64)