# Matching Agent

This agent computes candidate-job fit by first applying a deterministic skill-set overlap calculation in Python.
For ambiguous cases (e.g., partial skill matches, missing exact keywords but possessing transferable skills), it calls out to an LLM (Groq) for nuanced role-fit judgment.

## Components

- `agent.py`: Core `MatchingAgent` logic.
- `controller.py`: FastAPI routes.
- `service.py`: Business logic wrapper.
- `utils.py`: Deterministic calculation helpers.
- `prompts.py`: LLM instructions.
