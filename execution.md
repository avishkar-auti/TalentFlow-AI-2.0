Open a terminal at the project root directory (TalentFlow-AI-2.0):

bash


# Using the project's Python virtual environment
.\venv\Scripts\python -m backend.main
(Alternatively, using uvicorn directly:)

bash


.\venv\Scripts\uvicorn backend.app:create_app --factory --reload --port 8000
Backend API URL: http://localhost:8000
API Docs (Swagger UI): http://localhost:8000/docs
2. 🖥️ Start Frontend 1: Recruiter Dashboard
Open a new terminal window:

bash


cd frontend/recruiter-dashboard
npm run dev
Recruiter Dashboard URL: http://localhost:5173
3. 👤 Start Frontend 2: Candidate Portal
Open another new terminal window:

bash


cd frontend/candidate-portal
npm run dev
Candidate Portal URL: http://localhost:3001