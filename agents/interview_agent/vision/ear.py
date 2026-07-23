"""
Eye Aspect Ratio (EAR) Calculator.
Measures eye openness to detect extended eyes closed or blinking.
"""
import numpy as np

# Eye landmark indices for EAR:
# Left eye: 362, 385, 387, 263, 373, 380
# Right eye: 33, 160, 158, 133, 153, 144

def calculate_eye_aspect_ratio(landmarks: np.ndarray) -> float:
    """
    Computes Eye Aspect Ratio (EAR).
    Values below 0.18 indicate closed eyes.
    """
    if len(landmarks) < 388:
        return 0.30

    def _ear(pts):
        # Vertical distances
        v1 = np.linalg.norm(pts[1] - pts[5])
        v2 = np.linalg.norm(pts[2] - pts[4])
        # Horizontal distance
        h = np.linalg.norm(pts[0] - pts[3])
        if h == 0:
            return 0.30
        return (v1 + v2) / (2.0 * h)

    left_pts = np.array([landmarks[i][:2] for i in [362, 385, 387, 263, 373, 380]])
    right_pts = np.array([landmarks[i][:2] for i in [33, 160, 158, 133, 153, 144]])

    left_ear = _ear(left_pts)
    right_ear = _ear(right_pts)

    avg_ear = (left_ear + right_ear) / 2.0
    return round(float(avg_ear), 3)
