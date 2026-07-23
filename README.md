# TalentFlow-AI

TalentFlow-AI is a next-generation, AI-powered recruitment platform that streamlines the hiring process through automated resume screening, intelligent candidate matching, and interactive AI-driven interviews.

## Features

- **Automated Resume Parsing & Screening:** Extracts key information from resumes using advanced LLMs.
- **Intelligent Candidate Matching:** Evaluates candidates against job descriptions and provides match scores and detailed reasoning.
- **AI-Driven Interactive Interviews:** Conducts automated, real-time interviews with candidates, simulating a human recruiter.
- **Comprehensive Recruiter Dashboard:** Provides recruiters with a centralized view of candidates, jobs, and interview results.
- **Candidate Portal:** Allows candidates to apply for jobs, track their status, and participate in AI interviews.

## Tech Stack

- **Backend:** FastAPI (Python), Uvicorn, Pydantic, Structlog
- **Frontend:** React, Next.js (optional), TailwindCSS
- **Database & Storage:** Firebase Firestore, Firebase Cloud Storage
- **AI/LLMs:** Groq (LLaMA 3, Mixtral for fast inference), Google Gemini Pro (for complex interview reasoning)
- **Computer Vision/Audio:** OpenCV, MediaPipe (for real-time interview engagement tracking)
- **Deployment:** Docker, Docker Compose

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Firebase Project with Firestore and Storage enabled

### 2. Environment Variables
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```
Ensure you have your Gemini and Groq API keys, and your Firebase credentials file ready.

### 3. Firebase Credentials
Place your Firebase Admin SDK service account key at the path specified in your `.env` file (default: `./firebase-credentials.json`). DO NOT commit this file to version control.

### 4. Running Locally with Docker
The easiest way to get the entire stack running is using Docker Compose:
```bash
docker-compose up --build
```
This will start:
- Backend API at `http://localhost:8000`
- Recruiter Dashboard at `http://localhost:3000`
- Candidate Portal at `http://localhost:3001`

### 5. Running Locally (Manual)
To run the backend manually:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Architecture Overview
TalentFlow-AI follows a modular architecture:
- `backend/`: Core FastAPI application and REST endpoints.
- `agents/`: Dedicated AI agents for parsing, matching, decision-making, and interviewing.
- `tools/`: Shared integrations with external services (Firebase, LLM providers).
- `frontend/`: Web interfaces for recruiters and candidates.

## API Documentation
Once the backend is running, the interactive API documentation (Swagger UI) is available at:
`http://localhost:8000/docs`
