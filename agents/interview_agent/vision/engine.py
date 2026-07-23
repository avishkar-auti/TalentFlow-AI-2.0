"""
OpenCV & MediaPipe Vision Proctoring Engine.
Analyzes frame images for face count, gaze direction, 3D head pose, eye aspect ratio, and emits objective flags.
"""
import base64
import cv2
import numpy as np
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from .landmarks import FaceMeshExtractor
from .gaze import calculate_gaze_ratio
from .head_pose import estimate_head_pose
from .ear import calculate_eye_aspect_ratio
from .flags import ProctoringFlagTracker

logger = logging.getLogger(__name__)

class VisionProctoring:
    """Production OpenCV + MediaPipe Vision Proctoring Engine."""

    def __init__(self):
        self.extractor = FaceMeshExtractor()
        self.flag_tracker = ProctoringFlagTracker()

    async def analyze_frame(
        self,
        frame_base64: str,
        reference_photo_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decodes base64 frame image and executes landmark extraction, gaze estimation, head pose, and EAR analysis.
        Returns objective flags and numerical metrics.
        """
        try:
            if "," in frame_base64:
                frame_base64 = frame_base64.split(",")[1]
            
            img_bytes = base64.b64decode(frame_base64)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "face_detected": False,
                    "face_count": 0,
                    "gaze_state": "unknown",
                    "head_pose_state": "unknown",
                    "identity_match_score": None,
                    "flags": [],
                }

            h, w, _ = frame.shape

            extracted = self.extractor.extract_landmarks(frame)
            face_count = extracted["face_count"]

            gaze_offset = 0.0
            gaze_direction = "center"
            head_pose = {"yaw": 0.0, "pitch": 0.0, "roll": 0.0, "is_turned_away": False}
            ear_val = 0.30
            identity_match_score = None

            if face_count > 0 and len(extracted["landmarks_list"]) > 0:
                landmarks = extracted["landmarks_list"][0]
                gaze_offset, gaze_direction = calculate_gaze_ratio(landmarks)
                head_pose = estimate_head_pose(landmarks, (w, h))
                ear_val = calculate_eye_aspect_ratio(landmarks)

            flags = self.flag_tracker.evaluate_frame_signals(
                face_count=face_count,
                gaze_direction=gaze_direction,
                is_head_turned=head_pose["is_turned_away"],
                ear_value=ear_val,
                identity_match_score=identity_match_score,
            )

            head_pose_state = head_pose.get("state", "turned_away" if head_pose.get("is_turned_away") else "forward")

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "face_detected": face_count > 0,
                "face_count": face_count,
                "gaze_direction": gaze_direction,
                "gaze_state": gaze_direction,
                "gaze_offset": gaze_offset,
                "head_pose": head_pose,
                "head_pose_state": head_pose_state,
                "ear_value": ear_val,
                "identity_match_score": identity_match_score,
                "landmarks_backend": extracted.get("backend", "unknown"),
                "flags": flags
            }

        except Exception as e:
            logger.error(f"Error during vision frame analysis: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "face_detected": False,
                "face_count": 0,
                "gaze_state": "unknown",
                "head_pose_state": "unknown",
                "identity_match_score": None,
                "flags": [],
            }
