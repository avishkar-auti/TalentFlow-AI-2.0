"""
Gaze Direction Estimator.
Estimates iris ratio relative to eye corner landmarks to detect gaze direction.
"""
import numpy as np
from typing import Dict, Any, Tuple

# MediaPipe Eye Corner Indices:
# Left eye: inner 133, outer 33, iris center 468
# Right eye: inner 362, outer 263, iris center 473

LEFT_EYE_INNER = 133
LEFT_EYE_OUTER = 33
LEFT_IRIS_CENTER = 468

RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263
RIGHT_IRIS_CENTER = 473

def calculate_gaze_ratio(landmarks: np.ndarray) -> Tuple[float, str]:
    """
    Calculates horizontal and vertical iris displacement ratio.
    Returns (gaze_offset_ratio, direction_label).
    """
    if len(landmarks) < 474:
        return 0.0, "center"

    # Left eye ratio
    left_inner = landmarks[LEFT_EYE_INNER][:2]
    left_outer = landmarks[LEFT_EYE_OUTER][:2]
    left_iris = landmarks[LEFT_IRIS_CENTER][:2]

    left_width = np.linalg.norm(left_inner - left_outer)
    if left_width == 0:
        return 0.0, "center"

    left_dist = np.linalg.norm(left_iris - left_outer)
    ratio_left = left_dist / left_width

    # Right eye ratio
    right_inner = landmarks[RIGHT_EYE_INNER][:2]
    right_outer = landmarks[RIGHT_EYE_OUTER][:2]
    right_iris = landmarks[RIGHT_IRIS_CENTER][:2]

    right_width = np.linalg.norm(right_inner - right_outer)
    if right_width == 0:
        return 0.0, "center"

    right_dist = np.linalg.norm(right_iris - right_outer)
    ratio_right = right_dist / right_width

    avg_ratio = (ratio_left + ratio_right) / 2.0

    # Determine gaze direction state
    if avg_ratio < 0.38:
        direction = "looking_left"
    elif avg_ratio > 0.62:
        direction = "looking_right"
    else:
        direction = "center"

    gaze_offset = abs(avg_ratio - 0.5) * 2.0
    return round(float(gaze_offset), 2), direction
