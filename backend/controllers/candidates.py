"""Extended candidates controller — full endpoint map for the candidate pipeline."""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.candidate_service import CandidateService
from backend.services.matching_service import MatchingService
from backend.services.background_service import BackgroundService
from backend.services.decision_service import DecisionService
from backend.services.speech_service import SpeechService
from backend.services.technical_service import TechnicalService
from backend.services.proctoring_service import ProctoringService
from backend.services.interview_service import InterviewService
from backend.shared.response import success_response, error_response, APIResponse

router = APIRouter(tags=["Candidates"])


# ── Request schemas ──────────────────────────────────────────────────────────

class CreateCandidateRequest(BaseModel):
    name: str
    email: str
    job_id: str
    resume_url: Optional[str] = None


class MoveCandidateStageRequest(BaseModel):
    stage: str


class ScheduleInterviewRequest(BaseModel):
    job_id: str
    scheduled_at: str
    type: str = "speech"
    duration_minutes: int = 60


class ConsentRequest(BaseModel):
    consent_given: bool
    eye_gaze_tracking: bool = True
    video_recording: bool = True
    candidate_name: str = ""


class TechnicalSubmitRequest(BaseModel):
    answers: dict
    interview_id: str


class RecomputeMatchRequest(BaseModel):
    job_id: str


# ── Core CRUD ────────────────────────────────────────────────────────────────

@router.post("", response_model=APIResponse)
async def create_candidate(req: CreateCandidateRequest):
    svc = CandidateService()
    candidate = await svc.create_candidate(req.name, req.email, req.job_id, req.resume_url)
    return success_response(candidate, "Candidate created successfully")


@router.get("", response_model=APIResponse)
async def list_candidates(
    job_id: Optional[str] = None,
    stage: Optional[str] = None,
    score_min: Optional[float] = None,
):
    svc = CandidateService()
    candidates = await svc.list_candidates(stage=stage, job_id=job_id)
    if score_min is not None:
        candidates = [c for c in candidates if c.get("overallScore", 0) >= score_min]
    return success_response(candidates)


@router.get("/{id}", response_model=APIResponse)
async def get_candidate(id: str):
    svc = CandidateService()
    candidate = await svc.get_candidate(id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return success_response(candidate)


@router.patch("/{id}/stage", response_model=APIResponse)
async def move_stage(id: str, req: MoveCandidateStageRequest):
    svc = CandidateService()
    try:
        result = await svc.move_candidate_stage(id, req.stage)
        return success_response(result, f"Candidate moved to {req.stage}")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{id}", response_model=APIResponse)
async def delete_candidate(id: str):
    svc = CandidateService()
    candidate = await svc.get_candidate(id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    # Soft-delete via stage update
    await svc.move_candidate_stage(id, "deleted")
    return success_response({"id": id}, "Candidate removed")


# ── Resume ────────────────────────────────────────────────────────────────────

@router.post("/{id}/resume", response_model=APIResponse)
async def upload_resume(id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    svc = CandidateService()
    content = await file.read()
    result = await svc.process_resume(id, content, file.filename)
    return success_response(result, "Resume uploaded — pipeline processing started")


@router.get("/{id}/resume-analysis", response_model=APIResponse)
async def get_resume_analysis(id: str):
    import firebase_admin.firestore
    db = firebase_admin.firestore.client()
    doc = db.collection("candidates").document(id).collection("resume_analysis").document("latest").get()
    if not doc.exists:
        return success_response({"status": "not_analyzed"}, "Resume not yet analyzed")
    return success_response(doc.to_dict())


@router.post("/{id}/resume/reprocess", response_model=APIResponse)
async def reprocess_resume(id: str):
    return success_response(
        {"status": "queued", "candidate_id": id},
        "Resume reprocess queued"
    )


# ── Matching ─────────────────────────────────────────────────────────────────

@router.get("/{id}/matching", response_model=APIResponse)
async def get_matching(id: str, job_id: Optional[str] = None):
    svc = MatchingService()
    result = await svc.get_match_scores(id, job_id)
    return success_response(result)


@router.post("/{id}/matching/recompute", response_model=APIResponse)
async def recompute_matching(id: str, req: RecomputeMatchRequest):
    svc = MatchingService()
    result = await svc.recompute_match(id, req.job_id)
    return success_response(result)


# ── Background ────────────────────────────────────────────────────────────────

@router.get("/{id}/background", response_model=APIResponse)
async def get_background(id: str):
    svc = BackgroundService()
    result = await svc.get_background_check(id)
    return success_response(result)


@router.post("/{id}/background/recheck", response_model=APIResponse)
async def recheck_background(id: str):
    svc = BackgroundService()
    result = await svc.recheck_background(id)
    return success_response(result)


# ── Interview (per-candidate) ─────────────────────────────────────────────────

@router.post("/{id}/interview/schedule", response_model=APIResponse)
async def schedule_interview(id: str, req: ScheduleInterviewRequest):
    svc = InterviewService()
    interview = await svc.schedule({
        "candidate_id": id,
        "job_id": req.job_id,
        "scheduled_at": req.scheduled_at,
        "type": req.type,
        "duration_minutes": req.duration_minutes,
    })
    return success_response(interview, "Interview scheduled")


@router.get("/{id}/interview/{interview_id}", response_model=APIResponse)
async def get_interview(id: str, interview_id: str):
    svc = InterviewService()
    interview = await svc.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return success_response(interview)


@router.post("/{id}/interview/{interview_id}/consent", response_model=APIResponse)
async def record_consent(id: str, interview_id: str, req: ConsentRequest):
    import firebase_admin.firestore
    from datetime import datetime, timezone
    db = firebase_admin.firestore.client()
    consent_record = {
        "candidate_id": id,
        "interview_id": interview_id,
        "consent_given": req.consent_given,
        "eye_gaze_tracking_consent": req.eye_gaze_tracking,
        "video_recording_consent": req.video_recording,
        "candidate_name": req.candidate_name,
        "consented_at": datetime.now(timezone.utc).isoformat(),
    }
    db.collection("interviews").document(interview_id).collection("consent").document("record").set(consent_record)
    return success_response(consent_record, "Consent recorded")


@router.get("/{id}/interview/{interview_id}/proctoring-flags", response_model=APIResponse)
async def get_proctoring_flags(id: str, interview_id: str):
    svc = ProctoringService()
    summary = await svc.get_proctoring_summary(interview_id)
    return success_response(summary)


@router.post("/{id}/interview/{interview_id}/end", response_model=APIResponse)
async def end_interview(id: str, interview_id: str):
    import firebase_admin.firestore
    from datetime import datetime, timezone
    db = firebase_admin.firestore.client()
    db.collection("interviews").document(interview_id).update({
        "status": "completed",
        "ended_at": datetime.now(timezone.utc).isoformat(),
    })
    return success_response({"interview_id": interview_id, "status": "completed"}, "Interview ended")


# ── Speech ────────────────────────────────────────────────────────────────────

@router.get("/{id}/speech/{interview_id}", response_model=APIResponse)
async def get_speech_analysis(id: str, interview_id: str):
    svc = SpeechService()
    result = await svc.get_speech_analysis(id, interview_id)
    return success_response(result)


# ── Technical ─────────────────────────────────────────────────────────────────

@router.post("/{id}/technical/submit", response_model=APIResponse)
async def submit_technical(id: str, req: TechnicalSubmitRequest):
    svc = TechnicalService()
    result = await svc.submit_technical(id, req.answers, req.interview_id)
    return success_response(result, "Technical submission received")


@router.get("/{id}/technical/{interview_id}", response_model=APIResponse)
async def get_technical_result(id: str, interview_id: str):
    svc = TechnicalService()
    result = await svc.get_technical_result(id, interview_id)
    return success_response(result)


# ── Decision ──────────────────────────────────────────────────────────────────

@router.get("/{id}/decision", response_model=APIResponse)
async def get_decision(id: str):
    svc = DecisionService()
    result = await svc.get_decision(id)
    return success_response(result)


@router.post("/{id}/decision/generate", response_model=APIResponse)
async def generate_decision(id: str):
    svc = DecisionService()
    result = await svc.generate_decision(id)
    return success_response(result)


@router.get("/{id}/decision/report.pdf")
async def get_decision_report(id: str):
    svc = DecisionService()
    url = await svc.get_report_url(id)
    if not url:
        raise HTTPException(status_code=404, detail="Report not yet generated")
    return RedirectResponse(url=url)


# ── Legacy ────────────────────────────────────────────────────────────────────

@router.get("/{id}/timeline", response_model=APIResponse)
async def get_timeline(id: str):
    svc = CandidateService()
    timeline = await svc.get_timeline(id)
    return success_response(timeline)


@router.get("/{id}/summary", response_model=APIResponse)
async def get_summary(id: str):
    svc = CandidateService()
    summary = await svc.get_candidate_ai_summary(id)
    return success_response(summary)
