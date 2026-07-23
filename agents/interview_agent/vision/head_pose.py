"""
3D Head Pose Estimator (Yaw, Pitch, Roll) using OpenCV solvePnP.
"""
import cv2
import numpy as np
from typing import Dict, Any, Tuple

# Key 3D facial landmark indices for head pose:
# Nose tip: 1, Chin: 152, Left Eye Left Corner: 33, Right Eye Right Corner: 263, Left Mouth Corner: 61, Right Mouth Corner: 291
LANDMARK_IDS = [1, 152, 33, 263, 61, 291]

# Generic 3D facial model points (in mm)
MODEL_3D_POINTS = np.array([
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -130.0),     # Left eye left corner
    (225.0, 170.0, -130.0),      # Right eye right corner
    (-150.0, -150.0, -125.0),    # Left Mouth corner
    (150.0, -150.0, -125.0)      # Right mouth corner
], dtype=np.float64)

def estimate_head_pose(landmarks: np.ndarray, image_size: Tuple[int, int]) -> Dict[str, Any]:
    """
    Estimates 3D Head Pose (Yaw, Pitch, Roll) in degrees.
    """
    w, h = image_size
    if len(landmarks) < 300:
        return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_turned_away": False}

    image_points = np.array([
        landmarks[idx][:2] for idx in LANDMARK_IDS
    ], dtype=np.float64)

    # Camera intrinsic matrix estimation
    focal_length = w
    center = (w / 2.0, h / 2.0)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rvec, tvec = cv2.solvePnP(
        MODEL_3D_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    if not success:
        return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_turned_away": False}

    rmat, _ = cv2.Rodrigues(rvec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

    pitch = angles[0]
    yaw = angles[1]
    roll = angles[2]

    # Thresholds for head turned away (yaw > 25 deg or pitch > 20 deg)
    is_turned_away = abs(yaw) > 25.0 or abs(pitch) > 22.0

    return {
        "yaw": round(float(yaw), 1),
        "pitch": round(float(pitch), 1),
        "roll": round(float(roll), 1),
        "is_turned_away": is_turned_away
    }
