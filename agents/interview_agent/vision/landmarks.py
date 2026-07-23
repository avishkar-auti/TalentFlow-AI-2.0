"""Face landmark extraction for proctoring.

MediaPipe Face Mesh is used as the primary backend (with iris landmarks),
and OpenCV Haar cascades are retained as a fallback when MediaPipe is
unavailable.
"""
import cv2
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FaceMeshExtractor:
    """MediaPipe-first face landmark extractor with OpenCV fallback."""

    def __init__(self):
        self._mp_face_mesh = None
        self._mp_name: Optional[str] = None

        self.face_cascade = None
        self.eye_cascade = None
        self.profile_cascade = None

        self._init_mediapipe()
        self._init_opencv()

    def _init_mediapipe(self) -> None:
        try:
            import mediapipe as mp

            self._mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=3,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self._mp_name = "mediapipe_face_mesh"
            logger.info("MediaPipe Face Mesh initialized for proctoring landmarks.")
        except Exception as exc:
            self._mp_face_mesh = None
            self._mp_name = None
            logger.warning(f"MediaPipe Face Mesh unavailable, fallback enabled: {exc}")

    def _init_opencv(self):
        try:
            cascade_dir = getattr(cv2, 'data', None)
            path = getattr(cascade_dir, 'haarcascades', '') if cascade_dir else ''
            
            face_xml = path + 'haarcascade_frontalface_default.xml'
            eye_xml = path + 'haarcascade_eye.xml'
            profile_xml = path + 'haarcascade_profileface.xml'

            if hasattr(cv2, 'CascadeClassifier'):
                self.face_cascade = cv2.CascadeClassifier(face_xml)
                self.eye_cascade = cv2.CascadeClassifier(eye_xml)
                self.profile_cascade = cv2.CascadeClassifier(profile_xml)
                logger.info("OpenCV Haar cascades loaded for fallback face/eye detection.")
        except Exception as e:
            logger.warning(f"OpenCV CascadeClassifier init warning: {e}")

    def _extract_with_mediapipe(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        if self._mp_face_mesh is None:
            return None

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._mp_face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {
                "face_count": 0,
                "landmarks_list": [],
                "image_size": (w, h),
                "backend": self._mp_name,
            }

        landmarks_list = []
        for face_landmarks in results.multi_face_landmarks:
            pts = np.zeros((len(face_landmarks.landmark), 3), dtype=np.float32)
            for idx, lm in enumerate(face_landmarks.landmark):
                pts[idx] = [lm.x * w, lm.y * h, lm.z * w]
            landmarks_list.append(pts)

        return {
            "face_count": len(landmarks_list),
            "landmarks_list": landmarks_list,
            "image_size": (w, h),
            "backend": self._mp_name,
        }

    def extract_landmarks(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Extracts normalized landmarks from a BGR frame.

        Returns:
            {
                "face_count": int,
                "landmarks_list": List[np.ndarray],
                "image_size": (width, height),
                "backend": str,
            }
        """
        if frame is None or frame.size == 0:
            return {
                "face_count": 0,
                "landmarks_list": [],
                "image_size": (0, 0),
                "backend": "none",
            }

        mp_result = self._extract_with_mediapipe(frame)
        if mp_result is not None and mp_result["face_count"] > 0:
            return mp_result

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray)

        faces = []
        if self.face_cascade and not self.face_cascade.empty():
            detected = self.face_cascade.detectMultiScale(
                gray_eq, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
            )
            if len(detected) > 0:
                faces = list(detected)

        # Check profile faces if frontal faces not detected
        profile_detected = False
        if len(faces) == 0 and self.profile_cascade and not self.profile_cascade.empty():
            profiles = self.profile_cascade.detectMultiScale(
                gray_eq, scaleFactor=1.1, minNeighbors=3, minSize=(60, 60)
            )
            if len(profiles) > 0:
                faces = list(profiles)
                profile_detected = True

        landmarks_list = []
        for (fx, fy, fw, fh) in faces:
            # Construct a 474-point pseudo landmark array from OpenCV detections.
            # This keeps gaze/head-pose/EAR logic operational when MediaPipe is not available.
            pts = np.zeros((474, 3), dtype=np.float32)

            # Nose tip (index 1)
            pts[1] = [fx + fw / 2.0, fy + fh * 0.55, 0.0]
            # Chin (index 152)
            pts[152] = [fx + fw / 2.0, fy + fh * 0.95, 0.0]

            # Eye region inside face box
            eye_roi_gray = gray_eq[fy:fy + int(fh * 0.55), fx:fx + fw]
            eyes = []
            if self.eye_cascade and not self.eye_cascade.empty():
                detected_eyes = self.eye_cascade.detectMultiScale(eye_roi_gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
                if len(detected_eyes) > 0:
                    eyes = list(detected_eyes)

            # Sort eyes left-to-right
            eyes = sorted(eyes, key=lambda e: e[0])

            # Default eye positions inside face box
            left_eye_center = [fx + fw * 0.3, fy + fh * 0.35]
            right_eye_center = [fx + fw * 0.7, fy + fh * 0.35]
            left_iris = [fx + fw * 0.3, fy + fh * 0.35]
            right_iris = [fx + fw * 0.7, fy + fh * 0.35]

            if len(eyes) >= 1:
                ex, ey, ew, eh = eyes[0]
                left_eye_center = [fx + ex + ew / 2.0, fy + ey + eh / 2.0]
                # Analyze dark contour inside eye box for iris center
                eye_crop = eye_roi_gray[ey:ey+eh, ex:ex+ew]
                if eye_crop.size > 0:
                    _, thresh = cv2.threshold(eye_crop, 50, 255, cv2.THRESH_BINARY_INV)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        c = max(contours, key=cv2.contourArea)
                        M = cv2.moments(c)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            left_iris = [fx + ex + cx, fy + ey + cy]

            if len(eyes) >= 2:
                ex, ey, ew, eh = eyes[1]
                right_eye_center = [fx + ex + ew / 2.0, fy + ey + eh / 2.0]
                eye_crop = eye_roi_gray[ey:ey+eh, ex:ex+ew]
                if eye_crop.size > 0:
                    _, thresh = cv2.threshold(eye_crop, 50, 255, cv2.THRESH_BINARY_INV)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        c = max(contours, key=cv2.contourArea)
                        M = cv2.moments(c)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            right_iris = [fx + ex + cx, fy + ey + cy]

            # Populate eye landmarks:
            # Left eye inner 133, outer 33, iris 468
            pts[33] = [left_eye_center[0] - fw * 0.1, left_eye_center[1], 0.0]
            pts[133] = [left_eye_center[0] + fw * 0.1, left_eye_center[1], 0.0]
            pts[468] = [left_iris[0], left_iris[1], 0.0]

            # Right eye inner 362, outer 263, iris 473
            pts[362] = [right_eye_center[0] - fw * 0.1, right_eye_center[1], 0.0]
            pts[263] = [right_eye_center[0] + fw * 0.1, right_eye_center[1], 0.0]
            pts[473] = [right_iris[0], right_iris[1], 0.0]

            # Mouth corners (61, 291)
            pts[61] = [fx + fw * 0.3, fy + fh * 0.8, 0.0]
            pts[291] = [fx + fw * 0.7, fy + fh * 0.8, 0.0]

            # EAR landmarks (362, 385, 387, 263, 373, 380)
            pts[385] = [left_eye_center[0], left_eye_center[1] - fh * 0.04, 0.0]
            pts[387] = [left_eye_center[0], left_eye_center[1] - fh * 0.04, 0.0]
            pts[373] = [left_eye_center[0], left_eye_center[1] + fh * 0.04, 0.0]
            pts[380] = [left_eye_center[0], left_eye_center[1] + fh * 0.04, 0.0]

            pts[160] = [right_eye_center[0], right_eye_center[1] - fh * 0.04, 0.0]
            pts[158] = [right_eye_center[0], right_eye_center[1] - fh * 0.04, 0.0]
            pts[153] = [right_eye_center[0], right_eye_center[1] + fh * 0.04, 0.0]
            pts[144] = [right_eye_center[0], right_eye_center[1] + fh * 0.04, 0.0]

            landmarks_list.append(pts)

        return {
            "face_count": len(faces),
            "landmarks_list": landmarks_list,
            "image_size": (w, h),
            "profile_detected": profile_detected,
            "backend": "opencv_haar_fallback",
        }
