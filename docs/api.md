# TalentFlow-AI API Documentation

## 1. Overview & Base Configuration

- **Base URL**: `http://localhost:8000/api/v1` (or `https://api.talentflow.ai/api/v1` in production)
- **Content-Type**: `application/json` (except multi-part file uploads)
- **Request Tracing**: All responses contain the `X-Request-ID` header.

---

## 2. Authentication & Authorization

All protected endpoints require a Firebase Authentication ID Token passed as a Bearer token in the `Authorization` header:

```http
Authorization: Bearer <firebase_id_token>
```

### User Roles & Permissions
- **Admin**: Full access (`admin`)
- **Recruiter**: Job creation, candidate management, interview scheduling, report viewing (`recruiter`)
- **Candidate**: Application submission, candidate self-profile, live interview session participation (`candidate`)

---

## 3. Standard Error Format

All error responses adhere to the following standard JSON structure:

```json
{
  "detail": "Error description message",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2026-07-24T01:00:00Z",
  "request_id": "c7a8b9e1-3d4f-4a2b-9e8d-1a2b3c4d5e6f"
}
```

### Common HTTP Status Codes
| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request succeeded |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid input parameter or schema validation failure |
| `401` | Unauthorized | Missing or invalid Firebase ID Token |
| `403` | Forbidden | Insufficient user role permissions |
| `404` | Not Found | Requested document or entity does not exist |
| `422` | Unprocessable Entity | Pydantic validation error |
| `500` | Internal Server Error | Server runtime error |

---

## 4. Endpoints Reference

### 4.1 System & Health

#### `GET /health`
Returns backend service health status.

- **Auth**: None
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### 4.2 Auth Controller (`/api/v1/auth`)

#### `POST /api/v1/auth/login`
Authenticate user with Firebase ID token and retrieve user profile details.

- **Auth**: Bearer Token
- **Request Body**:
```json
{
  "token": "eyJhbGciOiJSUzI1NiIs..."
}
```
- **Response `200 OK`**:
```json
{
  "uid": "recruiter_01",
  "email": "recruiter@talentflow.ai",
  "role": "recruiter",
  "name": "Sarah Jenkins",
  "company": "TechCorp Inc"
}
```

#### `POST /api/v1/auth/verify`
Verify token validity.

- **Auth**: Bearer Token
- **Response `200 OK`**:
```json
{
  "valid": true,
  "uid": "recruiter_01",
  "email": "recruiter@talentflow.ai"
}
```

#### `GET /api/v1/auth/me`
Get current authenticated user profile.

- **Auth**: Bearer Token
- **Response `200 OK`**:
```json
{
  "id": "recruiter_01",
  "name": "Sarah Jenkins",
  "email": "recruiter@talentflow.ai",
  "company": "TechCorp Inc",
  "role": "recruiter",
  "active_jobs": ["job_101", "job_102"],
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

### 4.3 Jobs Controller (`/api/v1/jobs`)

#### `POST /api/v1/jobs`
Create a new job posting.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Request Body**:
```json
{
  "title": "Senior AI/ML Engineer",
  "description": "We are looking for a Senior AI/ML Engineer to build multi-agent LLM pipelines.",
  "requirements": {
    "skills": ["Python", "FastAPI", "PyTorch", "LangChain", "Firestore"],
    "experience_years": 5,
    "education": "Bachelor's in CS or equivalent",
    "location": "Remote / San Francisco"
  },
  "status": "open"
}
```
- **Response `201 Created`**:
```json
{
  "id": "job_101",
  "title": "Senior AI/ML Engineer",
  "description": "We are looking for a Senior AI/ML Engineer...",
  "requirements": {
    "skills": ["Python", "FastAPI", "PyTorch", "LangChain", "Firestore"],
    "experience_years": 5,
    "education": "Bachelor's in CS or equivalent",
    "location": "Remote / San Francisco"
  },
  "recruiter_id": "recruiter_01",
  "status": "open",
  "created_at": "2026-07-24T01:00:00Z",
  "application_count": 0,
  "pipeline_stages": ["applied", "screening", "recruiter_review", "interview_scheduled", "interview_completed", "decision", "hired", "rejected"]
}
```

#### `GET /api/v1/jobs`
List all jobs with optional filtering.

- **Auth**: Bearer Token
- **Query Params**:
  - `status` (optional): `open` | `closed` | `draft`
  - `limit` (optional, default: 20)
  - `offset` (optional, default: 0)
- **Response `200 OK`**:
```json
{
  "items": [
    {
      "id": "job_101",
      "title": "Senior AI/ML Engineer",
      "status": "open",
      "application_count": 12,
      "created_at": "2026-07-24T01:00:00Z"
    }
  ],
  "total": 1
}
```

#### `GET /api/v1/jobs/{job_id}`
Retrieve job details by ID.

- **Auth**: Bearer Token
- **Response `200 OK`**: (Job object matching schema above)

#### `PUT /api/v1/jobs/{job_id}`
Update an existing job posting.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Request Body**: Partial or full fields of Job.
- **Response `200 OK`**: Updated Job object.

#### `DELETE /api/v1/jobs/{job_id}`
Delete a job posting.

- **Auth**: Bearer Token (`admin`, job owner `recruiter`)
- **Response `200 OK`**: `{"message": "Job job_101 deleted successfully"}`

---

### 4.4 Candidates Controller (`/api/v1/candidates`)

#### `POST /api/v1/candidates`
Register a new candidate application.

- **Auth**: Bearer Token or Public Application submission
- **Request Body**:
```json
{
  "name": "Alex Mercer",
  "email": "alex.mercer@example.com",
  "phone": "+1-555-0192",
  "applied_job_id": "job_101",
  "metadata": {
    "source": "LinkedIn"
  }
}
```
- **Response `201 Created`**:
```json
{
  "id": "cand_201",
  "name": "Alex Mercer",
  "email": "alex.mercer@example.com",
  "phone": "+1-555-0192",
  "resume_url": null,
  "pipeline_stage": "applied",
  "status": "active",
  "applied_job_id": "job_101",
  "created_at": "2026-07-24T01:00:00Z",
  "updated_at": "2026-07-24T01:00:00Z",
  "metadata": {"source": "LinkedIn"}
}
```

#### `POST /api/v1/candidates/{id}/resume`
Upload resume file (PDF / DOCX) for a candidate.

- **Auth**: Bearer Token
- **Content-Type**: `multipart/form-data`
- **Form Data**: `file` (binary PDF/DOCX document)
- **Response `200 OK`**:
```json
{
  "candidate_id": "cand_201",
  "resume_url": "https://storage.googleapis.com/talentflow-ai.appspot.com/resumes/cand_201_resume.pdf",
  "message": "Resume uploaded successfully"
}
```

#### `GET /api/v1/candidates`
List candidates with optional filtering by job or pipeline stage.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Query Params**:
  - `job_id` (optional): Filter candidates by job ID
  - `pipeline_stage` (optional): Filter by stage (`applied`, `screening`, etc.)
- **Response `200 OK`**:
```json
{
  "items": [
    {
      "id": "cand_201",
      "name": "Alex Mercer",
      "email": "alex.mercer@example.com",
      "pipeline_stage": "applied",
      "status": "active",
      "applied_job_id": "job_101",
      "created_at": "2026-07-24T01:00:00Z"
    }
  ],
  "total": 1
}
```

#### `GET /api/v1/candidates/{id}`
Retrieve full candidate profile.

- **Auth**: Bearer Token
- **Response `200 OK`**: Candidate object.

#### `PUT /api/v1/candidates/{id}`
Update candidate fields.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Request Body**: Partial candidate schema.
- **Response `200 OK`**: Updated Candidate object.

#### `POST /api/v1/candidates/{id}/pipeline-stage`
Manually transition candidate pipeline stage.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Request Body**:
```json
{
  "stage": "interview_scheduled",
  "remarks": "Passed initial resume screening."
}
```
- **Response `200 OK`**:
```json
{
  "candidate_id": "cand_201",
  "previous_stage": "screening",
  "current_stage": "interview_scheduled",
  "updated_at": "2026-07-24T01:05:00Z"
}
```

#### `GET /api/v1/candidates/{id}/score`
Retrieve aggregated scores (resume, matching, interview evaluation) for candidate.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Response `200 OK`**:
```json
{
  "candidate_id": "cand_201",
  "job_id": "job_101",
  "ats_score": 88.5,
  "matching_score": 92.0,
  "technical_score": 85.0,
  "overall_score": 88.8,
  "recommendation": "strong_hire"
}
```

---

### 4.5 Interviews Controller (`/api/v1/interviews`)

#### `POST /api/v1/interviews`
Schedule an interview session.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Request Body**:
```json
{
  "candidate_id": "cand_201",
  "job_id": "job_101",
  "scheduled_at": "2026-07-25T14:00:00Z",
  "duration_minutes": 60,
  "interviewer_type": "ai"
}
```
- **Response `201 Created`**:
```json
{
  "id": "int_301",
  "candidate_id": "cand_201",
  "job_id": "job_101",
  "scheduled_at": "2026-07-25T14:00:00Z",
  "duration_minutes": 60,
  "status": "scheduled",
  "transcript": [],
  "proctoring_flags": [],
  "interviewer_type": "ai",
  "created_at": "2026-07-24T01:00:00Z"
}
```

#### `GET /api/v1/interviews/{id}`
Retrieve interview details.

- **Auth**: Bearer Token
- **Response `200 OK`**: Interview Object.

#### `POST /api/v1/interviews/{id}/start`
Start an interview session.

- **Auth**: Bearer Token
- **Response `200 OK`**: `{"id": "int_301", "status": "in_progress", "started_at": "2026-07-25T14:00:00Z"}`

#### `POST /api/v1/interviews/{id}/end`
Conclude an interview session.

- **Auth**: Bearer Token
- **Response `200 OK`**: `{"id": "int_301", "status": "completed", "ended_at": "2026-07-25T14:45:00Z"}`

#### `GET /api/v1/candidates/{id}/interview/{interview_id}/proctoring-flags`
Retrieve objective proctoring flags for an interview session.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Response `200 OK`**:
```json
{
  "interview_id": "int_301",
  "total_flags": 3,
  "summary": "3 flag(s) detected",
  "flags": [
    {
      "event": "gaze_away_from_screen",
      "start": "00:04:12",
      "duration_s": 6.0,
      "timestamp": "2026-07-25T14:04:18Z",
      "details": {
        "direction": "looking_down"
      }
    },
    {
      "event": "head_turned_away",
      "start": "00:09:30",
      "duration_s": 3.0,
      "timestamp": "2026-07-25T14:09:33Z",
      "details": {
        "head_pose": "turned_away"
      }
    }
  ]
}
```

---

### 4.6 WebSocket Protocol for Interview Stream

#### `WS /ws/interview/{interview_id}`
Real-time bi-directional streaming for live AI interview flow (text/audio control channel).

#### `WS /ws/interview/{interview_id}/vision`
Dedicated vision/proctoring channel for frame analysis.

#### Connection Lifecycle
1. **Client connects**: `ws://localhost:8000/ws/interview/int_301/vision`
2. **Handshake**: Server verifies token & interview status. Sends initial greeting frame.
3. **Streaming loop**: Client streams base64 JPEG frames, receives objective proctoring signal outputs.

#### Client to Server Message Frames (vision channel)
```json
{
  "type": "frame",
  "data": "<base64_encoded_jpeg_image>",
  "reference_photo": "<optional_base64_photo_for_identity_check>"
}
```
```json
{
  "type": "ping"
}
```

#### Server to Client Response Frames (vision channel)
```json
{
  "type": "vision_result",
  "timestamp": "2026-07-25T14:04:18Z",
  "face_count": 1,
  "face_detected": true,
  "gaze_direction": "looking_down",
  "gaze_state": "looking_down",
  "gaze_offset": 0.41,
  "head_pose": {
    "yaw": 4.5,
    "pitch": 23.1,
    "roll": -1.2,
    "is_turned_away": true,
    "state": "turned_away"
  },
  "head_pose_state": "turned_away",
  "ear_value": 0.24,
  "identity_match_score": null,
  "landmarks_backend": "mediapipe_face_mesh",
  "flags": [
    {
      "event": "head_turned_away",
      "timestamp": "2026-07-25T14:04:18Z",
      "start_timestamp": "14:04:15",
      "duration_seconds": 3.0
    }
  ]
}
```
```json
{
  "type": "pong"
}
```

---

### 4.7 Dashboard Controller (`/api/v1/dashboard`)

#### `GET /api/v1/dashboard/summary`
Get high-level hiring metrics.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Response `200 OK`**:
```json
{
  "total_active_jobs": 8,
  "total_candidates": 142,
  "interviews_conducted": 38,
  "pending_decisions": 5,
  "time_to_hire_avg_days": 11.4
}
```

#### `GET /api/v1/dashboard/pipeline-metrics`
Get pipeline distribution breakdown.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Response `200 OK`**:
```json
{
  "applied": 50,
  "screening": 30,
  "recruiter_review": 15,
  "interview_scheduled": 12,
  "interview_completed": 20,
  "decision": 5,
  "hired": 6,
  "rejected": 4
}
```

---

### 4.8 Reports Controller (`/api/v1/reports`)

#### `GET /api/v1/reports/candidate/{candidate_id}`
Retrieve generated evaluation report for candidate.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Response `200 OK`**:
```json
{
  "id": "rep_501",
  "candidate_id": "cand_201",
  "job_id": "job_101",
  "scores": {
    "resume_score": 88.5,
    "matching_score": 92.0,
    "technical_score": 85.0,
    "interview_score": 89.0
  },
  "recommendation": "strong_hire",
  "remarks": "Exceptional technical proficiency in Python state machines and agent design.",
  "generated_at": "2026-07-24T01:00:00Z",
  "pdf_url": "https://storage.googleapis.com/talentflow-ai.appspot.com/reports/rep_501.pdf"
}
```

#### `POST /api/v1/reports/generate`
Trigger asynchronous generation of candidate report.

- **Auth**: Bearer Token (`recruiter`, `admin`)
- **Request Body**: `{"candidate_id": "cand_201", "job_id": "job_101"}`
- **Response `202 Accepted`**: `{"report_id": "rep_501", "status": "generating"}`
