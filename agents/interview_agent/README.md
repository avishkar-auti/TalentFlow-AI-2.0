# Interview Agent

This directory contains the Interview Agent for TalentFlow-AI.

## Features
- **Live Interactive Interviews**: Uses WebSockets for real-time text/audio communication with candidates.
- **LLM Integration**: Powered by Gemini 1.5 Flash (via tools layer) for dynamic, context-aware conversational interviewing.
- **Sliding Context Window**: Maintains context of the last 3 turns to ensure low latency and focused responses.
- **Proctoring**: Async video frame analysis (MediaPipe Face Mesh + OpenCV fallback) running in parallel to ensure candidate integrity without subjective bias. Logs objective flags only (for example: `gaze_away_from_screen`, `head_turned_away`, `no_face_detected`, `multiple_faces_detected`) with timestamps/durations.
- **Consent Gate**: Requires explicit candidate consent before starting the interview phases.

## Components
- `controller.py`: FastAPI routes and WebSocket endpoints.
- `session.py`: WebSocket manager handling the live event loop, message routing, and async video processing triggers.
- `agent.py`: Core logic for state machine, prompt assembly, and interacting with the LLM.
- `vision/`: Image processing and proctoring modules (`landmarks.py`, `gaze.py`, `head_pose.py`, `ear.py`, `flags.py`, `engine.py`).
- `models.py` / `schemas.py`: Pydantic models for data validation.
- `firebase.py`: Repository pattern for Firestore interactions.
