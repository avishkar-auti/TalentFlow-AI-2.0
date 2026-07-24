# 🚀 TalentFlow-AI 2.0 - Execution Guide

## Quick Start (All-in-One)

### Option 1: Using Concurrently (Recommended)

```bash
# Install concurrently (first time only)
npm install -D concurrently

# Run everything in one terminal
npm run dev:all
```

**Add this to `package.json` in root:**
```json
{
  "scripts": {
    "dev:all": "concurrently \"npm run dev:backend\" \"npm run dev:frontend:recruiter\" \"npm run dev:frontend:candidate\"",
    "dev:backend": "cd backend && python -m uvicorn app:app --reload --port 8000",
    "dev:frontend:recruiter": "cd frontend/recruiter-dashboard && npm run dev",
    "dev:frontend:candidate": "cd frontend/candidate-portal && npm run dev"
  },
  "devDependencies": {
    "concurrently": "^8.0.0"
  }
}
```

---

### Option 2: Using Start Script (Cross-Platform)

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**macOS/Linux (Bash):**
```bash
bash start.sh
```

---

## Manual Start (3 Terminal Windows)

### Terminal 1: Backend API

```bash
cd backend
python -m uvicorn app:app --reload --port 8000
```

**Backend API URL:** http://localhost:8000  
**API Docs (Swagger UI):** http://localhost:8000/docs

---

### Terminal 2: Recruiter Dashboard

```bash
cd frontend/recruiter-dashboard
npm run dev
```

**Recruiter Dashboard URL:** http://localhost:3001

---

### Terminal 3: Candidate Portal

```bash
cd frontend/candidate-portal
npm run dev
```

**Candidate Portal URL:** http://localhost:5173

---

## URLs After Starting

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://localhost:8000 | FastAPI server + Firestore |
| **API Docs** | http://localhost:8000/docs | Swagger UI for testing endpoints |
| **Recruiter Dashboard** | http://localhost:3001 | Hiring manager interface |
| **Candidate Portal** | http://localhost:5173 | Job seeker interface |

---

## Environment Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm/yarn
- Firebase account with Firestore

### Install Dependencies (First Time)

```bash
# Backend
cd backend
pip install -r requirements.txt

# Recruiter Dashboard
cd ../frontend/recruiter-dashboard
npm install

# Candidate Portal
cd ../frontend/candidate-portal
npm install
```

---

## Testing the System

### 1️⃣ Candidate Portal (Apply)
```
1. Open http://localhost:5173
2. Click "Browse Jobs"
3. Upload resume → See ATS score
4. Navigate to status page
```

### 2️⃣ Recruiter Dashboard (Review)
```
1. Open http://localhost:3001
2. Go to Candidates tab
3. See new applicant (auto-refresh 5s)
4. Click "Schedule Interview"
5. Complete the beautiful modal form
```

### 3️⃣ Interview Flow
```
1. Candidate: /status → "Start AI Interview"
2. Face detection activates
3. Complete interview or test violations
4. Recruiter: /interviews → View results
```

---

## Stopping Services

### If using start script:
- **Windows**: `Ctrl+C` in PowerShell window
- **macOS/Linux**: `Ctrl+C` in terminal

### If using separate terminals:
- Press `Ctrl+C` in each terminal window

---

## Troubleshooting

### Backend won't start?
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Frontend won't start?
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Or for specific app
cd frontend/candidate-portal
npm install
npm run dev
```

### Firestore connection fails?
- Ensure Firebase credentials are set (check `.env` files)
- Verify Firestore database is created in Firebase console

---

## Next Steps

After starting:
1. ✅ Create a job (Recruiter: /jobs)
2. ✅ Apply with resume (Candidate: /jobs)
3. ✅ Schedule interview (Recruiter: /candidates)
4. ✅ Take interview (Candidate: /status)
5. ✅ Send offer (Recruiter: candidate profile)
6. ✅ Accept/Reject (Candidate: /status)

---

**All systems running! Happy testing! 🎉**
