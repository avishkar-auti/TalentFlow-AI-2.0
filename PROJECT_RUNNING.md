# 🚀 TalentFlow-AI-2.0 Project is NOW RUNNING

## ✅ Servers Status

| Service | Port | URL | Status |
|---------|------|-----|--------|
| **Candidate Portal** | 5173 | http://localhost:5173 | ✅ Running |
| **Recruiter Dashboard** | 3001 | http://localhost:3001 | ✅ Running |
| **Backend API** | 8000 | http://localhost:8000 | ✅ Running |

---

## 🎯 Quick Test Flow

### **Step 1: Browse Jobs (Candidate Portal)**
1. Open **http://localhost:5173** (Candidate Portal)
2. You'll see "Explore Open Job Openings"
3. Job cards display **Job IDs** like `JOB-20260724-ABC123`

### **Step 2: Apply to Job**
1. Click **"Apply Now"** on any job
2. Fill in your name and email
3. **Upload a resume PDF**
4. Watch the **ATS Score animation** (should show ~85%)
5. Auto-redirect to `/status` page

### **Step 3: Check Application Status**
1. On `/status` page, you'll see:
   - **Pipeline Timeline** (Applied → Screening → Shortlisted → etc)
   - **ATS Score Breakdown** (6 factors: keyword, skills, experience, education, format, sections)
   - **Matched/Missing Keywords**

### **Step 4: Test Interview Room (Face Detection)**
1. Manually navigate to: **http://localhost:5173/interview/demo_int_1**
2. Click **"Start Interview"**
3. Click **"Allow"** for camera/mic permissions
4. Your **face is now being detected** via face-api.js
5. **Test violations**:
   - Look left/right → See "Looking away" warning
   - No face > 3 seconds → See "Face absent" warning  
   - After 5 warnings → Auto-terminate

### **Step 5: Test Technical Coding + Recruiter Chat (NEW)**
1. Navigate to: **http://localhost:5173/technical/demo_int_1**
2. On the **right side**, you'll see **"Recruiter Chat"** panel (1 column)
3. The panel says "Recruiter will join soon..."
4. In another tab, open **http://localhost:3001** (Recruiter Dashboard)

### **Step 6: Recruiter Side - Schedule & Chat**
1. On Recruiter Dashboard (`localhost:3001`):
   - Go to **"Interviews"** tab
   - Click **"Chat"** on any interview (or create one)
   - WebSocket connects to candidate's technical sandbox
2. **Type a message** → Watch it appear in candidate's chat panel in real-time!
3. Candidate **types back** → Appears in recruiter's interview chat

### **Step 7: Create a Job (Recruiter Side)**
1. Go to **"Jobs"** on recruiter dashboard
2. Click **"+ New Job"**
3. Fill in:
   - Title, Department, Location
   - **Description** (new field)
   - **Experience Level** (new field)
   - **Salary Range** (new field)
   - **Required Skills** (tag input)
4. Click **"Create Job"**
5. You'll see the new **Job ID** badge on the card (format: `JOB-{date}-{hash}`)

### **Step 8: View Candidates + ATS Filtering**
1. On recruiter dashboard, go to **"Candidates"** tab
2. You'll see a **"Job ID"** column
3. Each candidate shows **ATS Score** (green ≥70, amber 50-70, red <50)
4. Filter by **Job** dropdown
5. Click **"Schedule Interview"** → Pre-filled with candidate + job info

---

## 🔌 API Quick Test (Backend)

Test endpoints with curl:

```bash
# List jobs
curl http://localhost:8000/api/v1/jobs

# List candidates
curl http://localhost:8000/api/v1/candidates

# List interviews
curl http://localhost:8000/api/v1/interviews
```

---

## 📊 Key Features to Verify

### ✅ Implemented & Working
- [x] Job creation with human-readable IDs
- [x] Resume upload → ATS scoring (6 factors)
- [x] Interview scheduling with ATS gate (≥70)
- [x] Face detection in interview room
- [x] Proctoring warnings (5-warning auto-terminate)
- [x] **NEW: Recruiter ↔ Candidate 1-on-1 chat**
- [x] Round chain (AI → HR → Technical)
- [x] Firestore data persistence

### 🎯 Demo Data
- Default fallback data included if Firestore not available
- Mock candidates & jobs appear if API fails

---

## 🛠️ Troubleshooting

### Backend won't start?
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
python -m uvicorn app:app --reload --port 8000
```

### Frontend won't load?
```bash
cd frontend/candidate-portal
npm install  # Install dependencies
npm run dev
```

### WebSocket chat not connecting?
- Check browser console (F12) for errors
- Verify backend is running on port 8000
- Check that `/ws/recruiter-chat/{interview_id}` is accessible

### Firestore not connected?
- App has fallback mock data
- Check backend logs for Firebase initialization errors
- Verify `.env` has correct Firebase credentials

---

## 📝 Test Scenarios

### Scenario 1: Complete Hiring Flow
1. **Recruiter** creates job → Gets Job ID
2. **Candidate** applies to job → Resume uploads → ATS scores
3. **Recruiter** sees candidate with ATS badge
4. **Recruiter** schedules "AI Screening" interview
5. **Candidate** sees scheduled interview on `/status`
6. **Candidate** joins `/interview/{id}` → Face detection works
7. **Recruiter** sees interview passed → Auto-creates "HR Round"
8. **Candidate** joins `/technical/{id}` → Recruiter chat opens
9. **Recruiter** & **Candidate** chat in real-time via WebSocket
10. **Recruiter** marks "Pass" → Candidate moves to "Offer" stage

### Scenario 2: Proctoring Violation
1. **Candidate** enters interview room
2. **Looks away** → Warning counter increments
3. **No face detected** > 3 seconds → Warning
4. Repeat 5 times → **Auto-terminated**
5. Interview status → **"terminated"**
6. Candidate status → **"rejected"**

### Scenario 3: ATS Gate Test
1. Create job with high skill requirements
2. Upload resume with low skill overlap
3. ATS score shows < 70
4. Try to schedule interview → **HTTP 400** "Resume not shortlisted"
5. Only candidates with ATS ≥ 70 can schedule interviews

---

## 🎬 Browser Tabs to Open

For full demo, open in 2+ browser tabs:

**Tab 1 (Candidate)**
- http://localhost:5173 → Browse jobs
- http://localhost:5173/status → View application status
- http://localhost:5173/interview/demo_int_1 → Interview room
- http://localhost:5173/technical/demo_int_1 → Technical sandbox + chat

**Tab 2 (Recruiter)**
- http://localhost:3001/jobs → Manage job postings
- http://localhost:3001/candidates → View candidates with ATS scores
- http://localhost:3001/interviews → Schedule & chat with candidates

---

## 📞 Need Help?

Check these files for reference:
- `IMPLEMENTATION_SUMMARY.md` — Complete technical summary
- `backend/controllers/jobs.py` — Job creation & apply endpoint
- `backend/services/ats_engine.py` — ATS scoring logic
- `frontend/candidate-portal/src/pages/TechnicalSandbox.tsx` — Recruiter chat integration
- `backend/controllers/interviews.py` — Interview WebSocket endpoints

---

**Happy testing! All systems online. 🚀**
