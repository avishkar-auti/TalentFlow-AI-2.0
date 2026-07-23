# Resume Agent

The Resume Agent is responsible for extracting structured data from candidate resumes (PDFs) and evaluating them against job requirements.

## Features
- **Local PDF Extraction**: Extracts text locally using `PyMuPDF` to save tokens.
- **Structured Parsing**: Uses Groq (llama-3.3-70b-versatile) to parse plain text into structured JSON.
- **Deterministic Scoring**: Calculates ATS and quality scores without relying on the LLM.
- **Caching**: Results are cached locally to avoid redundant API calls.
- **Firestore Integration**: Persists results to Firestore via the shared `backend.tools` layer.

## Architecture
- `agent.py`: Core processing logic.
- `service.py`: Business logic coordinating uploads and agent invocation.
- `controller.py`: FastAPI router for endpoints.
- `utils.py`: Deterministic utilities for extraction and scoring.
- `firebase.py`: Data persistence wrapper using `backend.tools`.

## Usage
The agent is exposed via the API endpoints in `controller.py` and never mentions itself to the end user.
