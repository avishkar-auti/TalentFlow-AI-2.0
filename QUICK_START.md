# ⚡ Quick Start Guide - TalentFlow-AI Complete System

## 🎯 System Now Running

```
✅ Backend API:          http://localhost:8000
✅ Candidate Portal:     http://localhost:5173
✅ Recruiter Dashboard:  http://localhost:3001
```

---

## 🚀 30-Second Quick Demo

### 1️⃣ Candidate Applies (5 min)
Open **http://localhost:5173** (Candidate Portal)
```
1. Click "Browse Jobs"
2. Click "Apply Now" on any job
3. Enter name: "John Doe"
4. Enter email: "john@example.com"
5. Upload a PDF resume (any PDF)
6. Watch ATS score calculate → 85% (shortlisted!)
7. Get redirected to /status
```

**What happens in background:**
- Resume extracted → Analyzed for keywords, skills, experience
- ATS Scoring: keyword(35%) + skills(30%) + exp(15%) + edu(10%) + format(5%) + sections(5%)
- Result: `atsScore: 85%` → Auto-shortlisted (≥70 threshold)
- Saved to Firestore: `candidates/{candidate_id}`

---

### 2️⃣ Recruiter Sees New Candidate (1 min)
Open **http://localhost:3001** (Recruiter Dashboard)
```
1. Go to Candidates tab
2. Dashboard auto-refreshes every 5 seconds
3. NEW CANDIDATE appears with:
   ✅ Name: John Doe
   ✅ Email: john@example.com
   ✅ Job ID: JOB-20260724-ABC123
   ✅ ATS Score: 85%
   ✅ Stage: "shortlisted"
```

**Why this happens:**
- Recruiter dashboard polls `GET /api/v1/candidates` every 5 seconds
- Backend returns all candidates with normalized ATS scores
- New applicant syncs automatically

---

### 3️⃣ Schedule Interview (2 min)
Recruiter Dashboard - Candidates
```
1. Click "Schedule Interview" on John Doe's row
2. Modal opens pre-filled with:
   - Candidate ID: cand_xxxx
   - Job ID: JOB-20260724-ABC123
3. Select Round: "AI Screening"
4. Set Date/Time
5. Click "Schedule"
```

**Backend flow:**
- Validates ATS score >= 70 ✅ (85% passes)
- Creates interview record in Firestore
- Generates meet_link: `http://localhost:5173/interview/{interview_id}`
- Returns interview details

---

### 4️⃣ Candidate Takes Interview (3 min)
Candidate Portal - /status
```
1. Candidate refreshes /status
2. Sees "Interview Scheduled" with countdown
3. Clicks "Start AI Interview"
4. Allows camera + microphone
```

Candidate Portal - /interview/{id}
```
5. Face detection starts running (face-api.js + MediaPipe)
6. AI asks questions via chat
7. Candidate responds via speech recognition
```

**Proctoring Active:**
- Face detected? ✅ "Clear to proceed"
- Look away? ⚠️ Warning #1 (violation: LOOKING_AWAY)
- No face > 3s? ⚠️ Warning #2 (violation: NO_FACE)
- Multiple faces? ⚠️ Warning #3 (violation: MULTIPLE_FACES)
- Eye closed? ⚠️ Warning #4 (violation: EYE_CLOSED)
- Audio noise? ⚠️ Warning #5 (violation: AUDIO_NOISE)
- **5th warning → AUTO-TERMINATE**
  - Interview status = "terminated"
  - Candidate status = "rejected"
  - No manual intervention needed

---

### 5️⃣ HR Interview (Auto-Created)
If candidate passed AI screening:
```
Recruiter Dashboard - Interviews
1. New interview auto-created: type = "hr_round"
2. Can schedule/join like AI round
3. Same proctoring rules apply
```

---

### 6️⃣ Technical Coding (1-on-1 Chat!)
Candidate Portal - /technical/{id}
```
LEFT SIDE: Code Editor
- Language: Python/JavaScript/TypeScript selector
- Starter code provided
- "Run Code" button → Output console
- "Submit Solution" → AI scores it

RIGHT SIDE: NEW! Recruiter Chat Panel
- Title: "Recruiter Chat"
- Green pulse indicator = Connected
- Shows "Recruiter will join soon..."
- Input field for typing messages
```

Recruiter Dashboard - /interviews
```
1. Go to Interviews tab
2. Find "Technical Coding" round
3. Click "Chat" button
4. WebSocket connects
5. Type message: "How would you optimize this solution?"
6. Message relays to candidate's chat panel
7. Candidate types back instantly
8. Full conversation history in Firestore
```

**Real-time Flow:**
```
Recruiter types: "Add error handling"
   ↓
WebSocket sends to backend
   ↓
Backend relays to candidate (WS /recruiter-chat/{id}?role=recruiter)
   ↓
Candidate's chat panel updates
   ↓
Candidate types: "Done, added try-catch"
   ↓
WebSocket sends back
   ↓
Recruiter sees message instantly
```

**Code Scoring:**
```
Candidate clicks "Submit Solution"
   ↓
Code sent to: POST /api/v1/interviews/code-submission
   ↓
Backend AI analyzes:
   - Code Quality Score (0-100)
   - Readability (has comments? yes=+10%)
   - Test Coverage (has tests? yes=+15%)
   - Complexity Estimates (O(n), O(1), etc)
   ↓
Returns feedback:
   ✅ "Excellent code quality!"
   ⚠️ "Add inline comments"
   ⚠️ "Include test cases"
   ↓
Score saved to Firestore
```

---

### 7️⃣ Final Decision
Recruiter Dashboard - Interview Results
```
1. Review:
   - Interview passed/failed
   - Proctoring flags
   - Chat messages
   - Code score (if technical)

2. Click "Pass" → Auto-creates Offer round
   Or "Fail" → Candidate rejected
```

Candidate Portal - /status
```
Final Stage: "Offer" 🎉
Message: "Congratulations! Click to view offer details"

Or: "Rejected" 😞
Message: "We appreciate your interest..."
```

---

## 📊 What's Working

| Feature | Status | Details |
|---------|--------|---------|
| **Resume Upload** | ✅ | Auto-ATS scoring, 6 factors |
| **Real-time Sync** | ✅ | Recruiter dashboard auto-refreshes (5s) |
| **ATS Gate** | ✅ | Only >= 70 can schedule interviews |
| **Face Detection** | ✅ | face-api.js + MediaPipe server-side |
| **5-Warning Reject** | ✅ | Auto-terminate on 5 violations |
| **Round Chain** | ✅ | Pass → Auto-create next round |
| **1-on-1 Chat** | ✅ | Real-time WebSocket relay |
| **Code Scoring** | ✅ | Quality, readability, tests, complexity |
| **Firestore Save** | ✅ | All data persisted |

---

## 🎬 Live Testing URLs

**Candidate Portal (Click to open)**
- Browse Jobs: http://localhost:5173
- Apply Status: http://localhost:5173/status
- Interview: http://localhost:5173/interview/demo_int_1
- Technical: http://localhost:5173/technical/demo_int_1

**Recruiter Dashboard (Click to open)**
- Candidates: http://localhost:3001/candidates
- Interviews: http://localhost:3001/interviews
- Jobs: http://localhost:3001/jobs

**Backend API**
- Health: http://localhost:8000/docs (Swagger UI)
- Candidates: http://localhost:8000/api/v1/candidates
- Interviews: http://localhost:8000/api/v1/interviews

---

## 🔧 If Something Breaks

### Backend won't start?
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```

### Frontend won't load?
```bash
cd frontend/candidate-portal  # or recruiter-dashboard
npm install
npm run dev
```

### Chat not connecting?
1. Check browser console (F12)
2. Verify localhost:8000 is accessible
3. Check WebSocket URL: `ws://localhost:8000/ws/recruiter-chat/{id}?role=candidate`

### ATS score showing as "% /"?
- Wait 5 seconds for auto-refresh
- Or reload page: F5
- Check browser console for errors

---

## 📚 Documentation Files

- **`FULL_INTEGRATION_GUIDE.md`** ← Complete technical overview
- **`IMPLEMENTATION_SUMMARY.md`** ← Architecture & endpoints
- **`PROJECT_RUNNING.md`** ← Detailed test scenarios
- **`QUICK_START.md`** ← This file!

---

## 🎯 Key Learnings

1. **Auto-refresh = Real-time UX**: Recruiter doesn't need to refresh; candidates appear automatically
2. **5-warning auto-reject = Zero manual work**: Violations trigger rejection without human review
3. **WebSocket chat = Instant collaboration**: Recruiter & candidate communicate in real-time during technical round
4. **Firestore persistence = Complete audit trail**: Every interview, flag, message, and score is logged
5. **Round chaining = Workflow automation**: Pass → Next round auto-created, no manual scheduling

---

## ✅ Success Checklist

After running through the demo:
- [ ] Candidate applied with resume
- [ ] New candidate appeared in recruiter dashboard within 5 seconds
- [ ] ATS score displayed correctly
- [ ] Could schedule interview (passed ATS >= 70 gate)
- [ ] Face detection ran in interview
- [ ] Tested 5-warning violations
- [ ] Chat panel appeared in technical sandbox
- [ ] Recruiter sent message, candidate saw it instantly
- [ ] Code submission accepted and scored
- [ ] Final status shows correct pipeline stage

---

**Everything is ready for production. Happy testing! 🚀**

Questions? Check the full integration guide or backend logs at `/tmp/backend.log`
