# Speech Agent

The Speech Agent is responsible for analyzing candidate interview transcripts to evaluate communication skills.

## Architecture

- **Agent**: Core logic orchestrating deterministic metrics and LLM evaluation (`agent.py`).
- **Controller**: API routes exposed via FastAPI (`controller.py`).
- **Service**: Orchestration layer connecting controllers to the agent (`service.py`).
- **Models**: Pydantic domain and data models (`models.py`).
- **Schemas**: API request/response schemas (`schemas.py`).
- **Firebase**: Firestore repository following the repository pattern (`firebase.py`).
- **Utils**: Pure Python deterministic analysis functions (`utils.py`).
- **Prompts**: LLM prompt templates (`prompts.py`).

## Flow

1. Reads transcript from Firestore `candidates/{id}/interviews/{interviewId}`.
2. Calculates deterministic metrics: word count, speaking pace (WPM), vocabulary diversity, and filler word frequency.
3. Uses Gemini LLM to assess communication clarity, confidence, articulation, and overall fluency based on the transcript and metrics.
4. Computes a final `speech_score` (0-100).
5. Writes the result to Firestore `candidates/{id}/speech/{interviewId}`.
