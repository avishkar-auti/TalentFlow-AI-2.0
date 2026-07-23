"""Gaze direction estimation from face landmarks."""
import numpy as np
from typing import Tuple

# MediaPipe Eye Corner Indices:
# Left eye: inner 133, outer 33, iris center 468
# Right eye: inner 362, outer 263, iris center 473

LEFT_EYE_INNER = 133
LEFT_EYE_OUTER = 33
LEFT_IRIS_CENTER = 468

RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263
RIGHT_IRIS_CENTER = 473

# Upper/lower eyelid landmarks for down-gaze checks.
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374

def calculate_gaze_ratio(landmarks: np.ndarray) -> Tuple[float, str]:
    """
    Calculates iris displacement ratio and maps it to an objective gaze state.

    Returns:
        (gaze_offset_ratio, state)

    State values:
        center | looking_left | looking_right | looking_down
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

    avg_horizontal_ratio = (ratio_left + ratio_right) / 2.0

    def _vertical_ratio(top_idx: int, bottom_idx: int, iris_idx: int) -> float:
        eye_top = landmarks[top_idx][:2]
        eye_bottom = landmarks[bottom_idx][:2]
        iris = landmarks[iris_idx][:2]

        eye_height = np.linalg.norm(eye_bottom - eye_top)
        if eye_height == 0:
            return 0.5
        return float(np.linalg.norm(iris - eye_top) / eye_height)

    left_vertical = _vertical_ratio(LEFT_EYE_TOP, LEFT_EYE_BOTTOM, LEFT_IRIS_CENTER)
    right_vertical = _vertical_ratio(RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM, RIGHT_IRIS_CENTER)
    avg_vertical_ratio = (left_vertical + right_vertical) / 2.0

    # Determine gaze direction state
    if avg_horizontal_ratio < 0.38:
        direction = "looking_left"
    elif avg_horizontal_ratio > 0.62:
        direction = "looking_right"
    elif avg_vertical_ratio > 0.70:
        direction = "looking_down"
    else:
        direction = "center"

    gaze_offset = abs(avg_horizontal_ratio - 0.5) * 2.0
    return round(float(gaze_offset), 2), direction
