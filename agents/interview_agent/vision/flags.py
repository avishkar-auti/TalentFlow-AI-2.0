"""
Objective Proctoring Flag Generator with Debouncing & Duration Tracking.
Ensures zero subjective bias and strict threshold enforcement.
"""
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ProctoringFlagTracker:
    """Tracks continuous violations and emits objective proctoring flags with 5-warning alert limit."""

    EVENT_DESCRIPTIONS = {
        "no_face_detected": "Candidate face not detected. Please remain directly in front of the camera.",
        "multiple_faces_detected": "Multiple people detected in video stream. The test must be taken alone.",
        "gaze_away_from_screen": "Eye gaze directed away from the screen for an extended period.",
        "head_turned_away": "Head turned away from camera view.",
        "eyes_closed_extended": "Eyes closed for an extended duration.",
        "identity_mismatch": "Identity verification match score below baseline threshold."
    }

    def __init__(self, max_warnings: int = 5):
        self.active_events: Dict[str, float] = {}  # event -> start_time
        self.last_flag_time: Dict[str, float] = {}  # event -> last_emitted_time
        self.debounce_seconds = 4.0
        self.warning_count = 0
        self.max_warnings = max_warnings

    def evaluate_frame_signals(
        self,
        face_count: int,
        gaze_direction: str,
        is_head_turned: bool,
        ear_value: float,
        identity_match_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluates current frame signals and emits objective flags if threshold duration is exceeded.
        Applies warning counts up to max_warnings (5) and signals auto-termination.
        """
        now = time.time()
        emitted_flags: List[Dict[str, Any]] = []

        # 1. No Face Detected threshold (> 2.5s)
        if face_count == 0:
            self._track_event("no_face_detected", now, threshold_s=2.5, emitted_flags=emitted_flags, details={"face_count": 0})
        else:
            self._reset_event("no_face_detected")

        # 2. Multiple Faces Detected (> 1.5s)
        if face_count > 1:
            self._track_event("multiple_faces_detected", now, threshold_s=1.5, emitted_flags=emitted_flags, details={"face_count": face_count})
        else:
            self._reset_event("multiple_faces_detected")

        # 3. Gaze Away from Screen (> 2.0s)
        if gaze_direction in ["looking_left", "looking_right"]:
            self._track_event("gaze_away_from_screen", now, threshold_s=2.0, emitted_flags=emitted_flags, details={"direction": gaze_direction})
        else:
            self._reset_event("gaze_away_from_screen")

        # 4. Head Turned Away (> 2.5s)
        if is_head_turned:
            self._track_event("head_turned_away", now, threshold_s=2.5, emitted_flags=emitted_flags, details={"head_pose": "turned_away"})
        else:
            self._reset_event("head_turned_away")

        # 5. Extended Eyes Closed (> 4.0s)
        if ear_value < 0.18:
            self._track_event("eyes_closed_extended", now, threshold_s=4.0, emitted_flags=emitted_flags, details={"ear": ear_value})
        else:
            self._reset_event("eyes_closed_extended")

        # 6. Identity Mismatch (if reference photo is provided)
        if identity_match_score is not None and identity_match_score < 0.45:
            self._track_event("identity_mismatch", now, threshold_s=2.0, emitted_flags=emitted_flags, details={"match_score": identity_match_score})
        else:
            self._reset_event("identity_mismatch")

        return emitted_flags

    def _track_event(self, event_type: str, now: float, threshold_s: float, emitted_flags: List[Dict[str, Any]], details: Dict[str, Any]):
        if event_type not in self.active_events:
            self.active_events[event_type] = now
            return

        duration = now - self.active_events[event_type]
        last_emitted = self.last_flag_time.get(event_type, 0.0)

        if duration >= threshold_s and (now - last_emitted >= self.debounce_seconds):
            self.warning_count += 1
            user_msg = self.EVENT_DESCRIPTIONS.get(event_type, "Proctoring rule violation detected.")
            
            is_terminated = self.warning_count >= self.max_warnings
            
            flag = {
                "event": event_type,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "start_timestamp": time.strftime("%H:%M:%S", time.gmtime(self.active_events[event_type])),
                "duration_seconds": round(duration, 1),
                "details": details,
                "warning_number": self.warning_count,
                "max_warnings": self.max_warnings,
                "user_message": f"Warning {self.warning_count}/{self.max_warnings}: {user_msg}",
                "is_terminated": is_terminated,
            }
            emitted_flags.append(flag)
            self.last_flag_time[event_type] = now
            logger.warning(f"Proctoring Warning {self.warning_count}/{self.max_warnings}: {event_type} (duration: {duration:.1f}s)")

    def _reset_event(self, event_type: str):
        if event_type in self.active_events:
            del self.active_events[event_type]
