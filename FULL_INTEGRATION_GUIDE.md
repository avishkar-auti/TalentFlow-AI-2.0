# 🚀 Complete End-to-End Integration Guide

## Overview
Full hiring pipeline from resume upload → ATS screening → AI interview with proctoring → 1-on-1 chat → Technical coding → Offer.

---

## 📊 Complete Data Flow

```
CANDIDATE PORTAL (localhost:3001)
    ↓
[Browse Jobs] → [Apply + Resume Upload]
    ↓
Resume saved to: backend/temp/job_{job_id}/candidate_{id}/resume.pdf
Resume sent to backend: POST /api/v1/jobs/{job_id}/apply
    ↓
BACKEND Processing:
    - Resume Extraction (text, skills, experience)
    - ATS Scoring (6-factor: keyword, skills, exp, edu, format, sections)
    - Firestore Save: candidates/{candidate_id}
    - Auto-shortlist if score >= 70
    ↓
RECRUITER DASHBOARD (localhost:5173)
    Auto-refresh every 5 seconds
    New candidate appears with:
    - Name, Email, Job ID
    - ATS Score (0-100%)
    - Pipeline Stage (Applied → Shortlisted → Interview → etc)
    - Action: Schedule Interview
    ↓
[Schedule AI Interview] → Interview created with meet_link
    ↓
CANDIDATE PORTAL - Interview Room (localhost:5173/interview/{id})
    - Face Detection (face-api.js)
    - Gesture/Movement Analysis
    - Warning Counter (0-5)
    - Auto-Termination on 5 warnings → Reject candidate
    ↓
If NOT terminated:
    [Pass Interview] → Auto-create HR Round → Auto-create Technical Round
    ↓
CANDIDATE PORTAL - Technical Sandbox (localhost:5173/technical/{id})
    - Code Editor (Python/JS/TypeScript)
    - Run Code → Output Console
    - Submit Code → AI Scoring:
        * Code Quality (0-100)
        * Readability Assessment
        * Test Coverage Analysis
        * Time/Space Complexity Estimation
    ↓
Real-time 1-on-1 Chat (WebSocket)
    - Recruiter (recruiter dashboard) connects
    - Candidate (technical sandbox) sees chat panel
    - Messages relay in real-time
    - History persisted to Firestore
    ↓
[Pass Technical] → Auto-create Offer Round
    ↓
Final Status: Offer / Rejected
```

---

## 🔌 API Endpoints

### Candidate Application
```bash
POST /api/v1/jobs/{job_id}/apply
  Payload: FormData
    - file: resume.pdf
    - name: string
    - email: string
  Response: {
    candidate_id, job_id, name, email,
    ats_score, ats_breakdown, is_shortlistable
  }
```

### Candidate Retrieval (Real-time Sync)
```bash
GET /api/v1/candidates
  # Called every 5 seconds by recruiter dashboard
  Response: [
    { id, name, email, job_id, ats_score, pipeline_stage, ... },
    ...
  ]
```

### Interview Management
```bash
POST /api/v1/interviews
  - Schedule new interview (enforces ATS >= 70)

POST /api/v1/interviews/{id}/pass
  - Mark passed, auto-create next round

POST /api/v1/interviews/{id}/fail
  - Mark failed, reject candidate

GET /api/v1/interviews/{id}/summary
  - Full interview data + chat history + proctoring flags
```

### Code Submission
```bash
POST /api/v1/interviews/code-submission
  Payload: {
    interview_id: string,
    language: "python" | "javascript" | "typescript",
    code: string,
    expected_output: string
  }
  Response: {
    code_quality_score: 0-100,
    readability: string,
    test_coverage: string,
    execution_time_estimate: string,
    space_complexity_estimate: string,
    feedback: string
  }
```

### Proctoring
```bash
POST /api/v1/interviews/proctoring-flag
  Payload: {
    interview_id: string,
    flag_type: "NO_FACE" | "MULTIPLE_FACES" | "LOOKING_AWAY" | ... ,
    severity: "warning" | "critical"
  }
  Response: {
    warning_number: 1-5,
    auto_terminated: boolean,
    flag: { flag_type, severity, timestamp, ... }
  }
  # If warning_number >= 5: Interview auto-terminated, candidate rejected
```

### WebSocket Endpoints
```
WS /ws/interview/{id}
  - Main interview session (AI questions/responses)

WS /ws/interview/{id}/vision
  - Vision proctoring (frame submission + analysis)

WS /ws/recruiter-chat/{id}?role=candidate|recruiter
  - 1-on-1 recruiter ↔ candidate chat
```

---

## 🎯 Complete Test Scenario

### Step 1: Candidate Applies (localhost:3001)
```
1. Go to http://localhost:3001
2. Click "Browse Jobs"
3. Click "Apply Now" on a job
4. Fill name, email, upload resume PDF
5. Watch ATS score animate (85% = shortlisted)
6. Note candidate_id and job_id in browser console
```

**Backend Action**: Resume processed, ATS calculated, Firestore saved

---

### Step 2: Recruiter Sees New Candidate (localhost:5173)
```
1. Go to http://localhost:5173/candidates
2. Dashboard auto-refreshes every 5 seconds
3. New candidate appears with:
   - Name, Email
   - Job ID (JOB-20260724-xxx)
   - ATS Score: 85%
   - Stage: "shortlisted"
```

**Backend Action**: GET /candidates called, returns new record

---

### Step 3: Schedule AI Interview
```
Recruiter Dashboard:
1. Click "Schedule Interview" on candidate
2. Set Round: "AI Screening"
3. Set Time
4. Click "Schedule"

Candidate Portal:
1. Go to /status
2. See "Interview Scheduled"
3. See meet_link: http://localhost:5173/interview/{id}
```

**Backend Action**: Interview record created, ATS >= 70 gate enforced

---

### Step 4: Take AI Interview with Proctoring
```
Candidate Portal - Interview Room:
1. Navigate to /interview/{interview_id}
2. Click "Start Interview" button
3. Allow camera + microphone
4. See face detection running
5. Try violations:
   - Look left/right → Warning "Looking away"
   - No face > 3s → Warning "Face absent"
   - Multiple people → Warning "Multiple faces"
   - Repeat 5x → AUTO-TERMINATE
6. Status → Terminated, Rejected
```

**Backend Actions**:
- Server analyzes vision frames via `/ws/interview/{id}/vision`
- Flags accumulate in Firestore
- On 5th warning → Interview status = "terminated", Candidate status = "rejected"
- Auto-reject without human intervention

---

### Step 5: HR Interview (If Not Terminated)
```
If candidate passed AI screening:
1. New interview auto-created: type = "hr_round"
2. Similar flow to AI, but with HR-specific questions
3. Recruiter can see it in Interviews tab
```

**Backend Action**: pass_interview() → auto-create next round

---

### Step 6: Technical Coding + Recruiter Chat
```
Candidate Portal - Technical Sandbox:
1. Navigate to /technical/{interview_id}
2. See code editor + chat panel on right
3. Write Python/JS/TypeScript solution
4. Click "Run Code" → See output
5. Click "Submit Solution" → Sends for AI scoring

Backend:
- Analyzes code quality (comments, tests, complexity)
- Returns score + feedback
- Result saved to Firestore interviews/{id}/code_submission

Recruiter Dashboard - Interviews:
1. Go to /interviews
2. Click "Chat" on technical round
3. WebSocket connects to candidate's chat panel
4. Type message → Relayed instantly to candidate
5. Candidate types back → Appears on recruiter side
6. Full conversation history in Firestore interviews/{id}/chat/messages
```

**Backend Actions**:
- POST /interviews/code-submission → AI scoring
- WS /ws/recruiter-chat/{id}?role=recruiter → Message relay
- Both sides can see real-time conversation

---

### Step 7: Final Decision
```
Recruiter Dashboard:
1. Review interview results, code score, chat notes
2. Click "Pass" → Auto-create Offer round
3. Or Click "Fail" → Candidate rejected

Candidate Portal - Status:
1. See final pipeline stage: "Offer" or "Rejected"
2. If Offer: "Congratulations! Click to view offer details"
3. If Rejected: "We appreciate your interest..."
```

---

## 🎯 Key Features Implemented

### 1. ✅ Real-Time Candidate Sync
- Recruiter dashboard polls every 5 seconds
- New applications appear instantly
- ATS scores auto-calculated

### 2. ✅ 5-Warning Auto-Rejection
- Gesture detection (face-api.js client + MediaPipe server)
- Flag types: NO_FACE, MULTIPLE_FACES, LOOKING_AWAY, EYE_CLOSED, AUDIO_NOISE, etc.
- 5th warning → Auto-terminate → Reject candidate
- No manual intervention needed

### 3. ✅ 1-on-1 Recruiter Chat
- Real-time WebSocket relay
- Recruiter (role=recruiter) ↔ Candidate (role=candidate)
- Chat panel in Technical Sandbox
- History persisted to Firestore

### 4. ✅ Code Submission + AI Scoring
- Support: Python, JavaScript, TypeScript
- Scoring factors: Readability, Tests, Complexity estimates
- Feedback: "Add comments", "Include test cases", etc.
- Result saved to Firestore

### 5. ✅ Auto-Round Chain
- Pass AI Screening → Auto-create HR Round
- Pass HR Round → Auto-create Technical Round
- Pass Technical → Auto-create Offer Round

### 6. ✅ Complete Proctoring
- Server-side: OpenCV + MediaPipe vision analysis
- Client-side: face-api.js gesture detection
- Defense-in-depth: Both validate
- Persistent flags: All violations logged to Firestore

---

## 🚀 Running the Full Stack

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app:app --reload --port 8000

# Terminal 2: Candidate Portal
cd frontend/candidate-portal
npm run dev  # http://localhost:3001

# Terminal 3: Recruiter Dashboard
cd frontend/recruiter-dashboard
npm run dev  # http://localhost:5173
```

---

## 📝 Firestore Data Structure

```
candidates/{candidate_id}/
  - id, name, email, job_id
  - atsScore, resumeScore, atsBreakdown
  - keywordDensity, skillOverlap, experienceMatch
  - pipeline_stage: applied|screening|shortlisted|interview|hr|technical|offer|rejected

interviews/{interview_id}/
  - id, candidate_id, job_id, type, round_number
  - status: scheduled|in_progress|completed|terminated
  - warning_count: 0-5
  - proctoring_flags: [{flag_type, severity, timestamp, warning_number}]
  - pass_fail: pass|fail
  - code_submission: {language, code, score, submitted_at}
  
  /chat/messages/
    - sender_role: recruiter|candidate
    - content: string
    - timestamp: ISO8601
  
  /proctoring_flags/
    - All flag events with timestamps
```

---

## ✅ Verification Checklist

- [ ] Candidate applies → Appears in recruiter dashboard within 5 seconds
- [ ] ATS score displays correctly (85 vs 65 vs 82)
- [ ] Can schedule interview only if ATS >= 70
- [ ] Video interview loads face detection
- [ ] 5th warning triggers auto-termination
- [ ] Terminated candidate shows as "rejected"
- [ ] Pass interview → Next round auto-created
- [ ] Recruiter chat connects to technical sandbox
- [ ] Messages relay in real-time
- [ ] Code submission accepted + scored
- [ ] Final status shows correct pipeline stage

---

## 🎬 Demo Flow (10 minutes)

1. **Apply (2 min)**: Candidate portal → Browse → Apply → Upload resume
2. **Sync (1 min)**: Switch to recruiter, see new candidate appear
3. **Interview (4 min)**: Schedule → Take interview → Test face detection → 5 warnings → Terminate
4. **Chat (2 min)**: Recruiter sends message → See it in technical sandbox chat panel
5. **Code (1 min)**: Submit code → See AI scoring result

---

**Ready for production testing! 🎉**
