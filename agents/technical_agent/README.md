# Technical Agent

The Technical Agent is responsible for analyzing candidate technical interview transcripts and code submissions to evaluate their technical proficiency.

## Architecture

- **Agent**: Core logic orchestrating deterministic metrics and Groq LLM evaluation (`agent.py`).
- **Controller**: API routes exposed via FastAPI (`controller.py`).
- **Service**: Orchestration layer connecting controllers to the agent (`service.py`).
- **Models**: Pydantic domain models (`models.py`).
- **Schemas**: API request/response schemas (`schemas.py`).
- **Firebase**: Firestore repository (`firebase.py`).
- **Utils**: Pure Python deterministic analysis (`utils.py`).
- **Prompts**: LLM prompt templates (`prompts.py`).

## Flow

1. Reads transcript and code submissions from Firestore `candidates/{id}/interviews/{interviewId}`.
2. Calculates deterministic metrics: code syntax checks, keyword matching.
3. Uses Groq `llama-3.3-70b` via tools to assess correctness, code quality, problem solving, and technical depth.
4. Computes a final `technical_score` (0-100).
5. Writes the result to Firestore `candidates/{id}/technical/{interviewId}`.
