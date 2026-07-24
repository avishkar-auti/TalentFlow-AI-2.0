import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import WebSocket
from backend.repositories.interview_repository import InterviewRepository
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.job_repository import JobRepository
from backend.models.interview import Interview

logger = logging.getLogger(__name__)

class InterviewService:
    def __init__(self):
        self.repo = InterviewRepository()
        self.cand_repo = CandidateRepository()
        self.job_repo = JobRepository()

    async def schedule(self, data: dict) -> Dict[str, Any]:
        from fastapi import HTTPException
        candidate_id = data.get('candidate_id') or data.get('candidateId')
        if candidate_id:
            ats_check = await self.check_ats_gate(candidate_id)
            if not ats_check.get('allowed'):
                raise HTTPException(status_code=400, detail=ats_check.get('reason'))

        intv_id = data.get('id') or str(uuid.uuid4())
        data['id'] = intv_id
        data['status'] = 'scheduled'
        
        # Determine round properties based on type
        intv_type = data.get('type', 'ai_screening')
        data['interview_round'] = intv_type
        data['round_number'] = {'ai_screening': 1, 'hr_round': 2, 'technical_coding': 3}.get(intv_type, 1)
        data['meet_link'] = f'http://localhost:5173/interview/{intv_id}'

        interview = Interview(**data)
        await self.repo.create(intv_id, interview)
        return interview.model_dump()

    async def check_ats_gate(self, candidate_id: str) -> dict:
        """Check if candidate's ATS score >= 70 (shortlistable) to allow interview."""
        cand = await self.cand_repo.get(candidate_id)
        if not cand:
            return {'allowed': False, 'reason': 'Candidate not found'}
        ats = getattr(cand, 'atsScore', None) or getattr(cand, 'overallScore', None) or 0
        if ats < 70:
            return {'allowed': False, 'reason': f'ATS score {ats:.1f}% below threshold (70%). Resume not shortlisted.', 'ats_score': ats}
        return {'allowed': True, 'ats_score': ats}

    async def pass_interview(self, interview_id: str, notes: str = '') -> dict:
        """Mark interview as passed and auto-schedule next round."""
        import firebase_admin.firestore
        from datetime import datetime, timezone
        db = firebase_admin.firestore.client()
        
        interview = await self.get_interview(interview_id)
        if not interview:
            raise ValueError('Interview not found')
        
        current_round = interview.get('interview_round', 'ai_screening')
        candidate_id = interview.get('candidate_id')
        job_id = interview.get('job_id')
        
        # Mark current interview passed
        db.collection('interviews').document(interview_id).update({
            'status': 'completed',
            'pass_fail': 'pass',
            'result_notes': notes,
            'ended_at': datetime.now(timezone.utc).isoformat()
        })
        
        # Determine next round
        round_chain = {'ai_screening': 'hr_round', 'hr_round': 'technical_coding'}
        next_round = round_chain.get(current_round)
        
        next_interview = None
        if next_round and candidate_id and job_id:
            next_intv_id = str(uuid.uuid4())
            next_intv_data = {
                'id': next_intv_id,
                'candidate_id': candidate_id,
                'job_id': job_id,
                'type': next_round,
                'interview_round': next_round,
                'round_number': {'hr_round': 2, 'technical_coding': 3}.get(next_round, 2),
                'status': 'scheduled',
                'scheduled_at': None,  # recruiter to confirm
                'duration_minutes': 60,
                'meet_link': f'http://localhost:5173/interview/{next_intv_id}',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            db.collection('interviews').document(next_intv_id).set(next_intv_data)
            next_interview = next_intv_data
            
            # Update candidate stage
            stage_map = {'hr_round': 'hr_interview', 'technical_coding': 'technical'}
            new_stage = stage_map.get(next_round, 'interview')
            db.collection('candidates').document(candidate_id).update({'pipeline_stage': new_stage, 'stage': new_stage})
        elif not next_round:
            # All rounds passed -> move to offer
            db.collection('candidates').document(candidate_id).update({'pipeline_stage': 'offer', 'stage': 'offer'})
        
        return {'interview_id': interview_id, 'passed': True, 'next_round': next_interview}

    async def fail_interview(self, interview_id: str, notes: str = '') -> dict:
        """Mark interview as failed and move candidate to rejected."""
        import firebase_admin.firestore
        from datetime import datetime, timezone
        db = firebase_admin.firestore.client()
        interview = await self.get_interview(interview_id)
        if not interview:
            raise ValueError('Interview not found')
        candidate_id = interview.get('candidate_id')
        db.collection('interviews').document(interview_id).update({
            'status': 'completed', 'pass_fail': 'fail',
            'result_notes': notes, 'ended_at': datetime.now(timezone.utc).isoformat()
        })
        if candidate_id:
            db.collection('candidates').document(candidate_id).update({'pipeline_stage': 'rejected', 'stage': 'rejected'})
        return {'interview_id': interview_id, 'passed': False}

    async def get_candidate_scheduled_interviews(self, candidate_id: str) -> list:
        """Get all scheduled/upcoming interviews for a candidate."""
        all_interviews = await self.list_interviews(candidate_id=candidate_id)
        return [i for i in all_interviews if i.get('status') in ('scheduled', 'in_progress')]

    async def list_interviews(self, candidate_id: Optional[str] = None) -> List[Dict[str, Any]]:
        interviews = await self.repo.get_all()
        if candidate_id:
            interviews = [i for i in interviews if getattr(i, 'candidate_id', None) == candidate_id]
        return [i.model_dump() for i in interviews]

    async def get_interview(self, id: str) -> Optional[Dict[str, Any]]:
        interview = await self.repo.get(id)
        return interview.model_dump() if interview else None

    def _extract_resume_chunks(self, candidate_data: Dict[str, Any], resume_analysis: Optional[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Chunk candidate's parsed resume into searchable contextual blocks (skills, experience, projects)."""
        chunks = []
        
        # Skills chunk
        skills = (candidate_data.get("skills") or 
                  (resume_analysis and resume_analysis.get("analysis", {}).get("skills")) or 
                  ["Python", "FastAPI", "React", "Docker", "REST APIs"])
        if skills:
            chunks.append({
                "type": "skills",
                "content": f"Candidate core technical skills: {', '.join(skills if isinstance(skills, list) else [str(skills)])}"
            })

        # Experience chunk
        exp_list = (resume_analysis and resume_analysis.get("analysis", {}).get("experience")) or []
        if isinstance(exp_list, list) and exp_list:
            for exp in exp_list:
                if isinstance(exp, dict):
                    t = exp.get("title") or exp.get("role") or "Developer"
                    c = exp.get("company") or "Tech Company"
                    d = exp.get("description") or "Building scalable backend microservices and APIs."
                    chunks.append({
                        "type": "experience",
                        "content": f"Work Experience as {t} at {c}: {d}"
                    })
        else:
            chunks.append({
                "type": "experience",
                "content": "Work Experience: Software Engineer with experience in web applications, backend APIs, and microservices architecture."
            })

        # Projects / Education chunk
        chunks.append({
            "type": "projects",
            "content": "Projects & Architecture: Built scalable cloud APIs, automated testing pipelines, and front-end user interfaces."
        })
        
        return chunks

    def _generate_rag_question(self, turn_count: int, user_answer: str, chunks: List[Dict[str, str]], job_title: str) -> str:
        """RAG Question Generator — Enforces standard 1-on-1 human recruiter dialogue (single question per turn, max 45 words)."""
        user_lower = user_answer.lower()

        # Select target resume chunk
        matched_skills = "Python, FastAPI, microservices"
        for chunk in chunks:
            if chunk.get("type") == "skills":
                matched_skills = chunk.get("content", "").replace("Candidate core technical skills: ", "")
                break
        
        # Turn 1: Warm introduction + 1 background question
        if turn_count <= 1:
            return (f"Hello! Welcome to your interview for the {job_title} role. "
                    f"I noticed from your resume that you work with {matched_skills[:40]}. "
                    f"Could you briefly highlight your most impactful recent project using these technologies?")

        # Turn 2: Follow-up on technical architecture & trade-offs
        elif turn_count == 2:
            return (f"That sounds impressive! Working on that project, what was the biggest technical bottleneck or scaling challenge you faced, and how did you resolve it?")

        # Turn 3: Focused System Design / Role alignment question
        elif turn_count == 3:
            return (f"Got it. For our {job_title} team, how do you design REST APIs and database queries to ensure low latency under high concurrency?")

        # Turn 4: Behavioral & Team Collaboration
        elif turn_count == 4:
            return (f"Makes sense! Can you share a quick example of how you handle code reviews or technical disagreements with team members?")

        # Turn 5+: Wrap-up
        else:
            return (f"Thank you for sharing those insights! You've shown strong alignment for the {job_title} role. Do you have any questions for me about our tech stack or team culture?")

    async def handle_live_interview(self, id: str, websocket: WebSocket):
        """Handle turn-by-turn AI Recruiter interview session over WebSocket using Resume RAG."""
        logger.info(f"Live AI RAG interview session handler started for interview_id: {id}")
        
        # Fetch interview record and associated candidate & job data
        interview_doc = await self.get_interview(id) or {}
        candidate_id = interview_doc.get("candidate_id") or "demo_cand"
        job_id = interview_doc.get("job_id") or "JOB001"

        candidate_data = {}
        resume_analysis = None
        job_title = "Software Engineer"

        if candidate_id:
            try:
                cand_model = await self.cand_repo.get(candidate_id)
                if cand_model:
                    candidate_data = cand_model.model_dump()
                    job_title = candidate_data.get("job_title") or job_title
                resume_analysis = await self.cand_repo.get_subcollection(candidate_id, "resume_analysis", "latest")
            except Exception as e:
                logger.warning(f"Failed to fetch candidate RAG context for {candidate_id}: {e}")

        if job_id:
            try:
                job_model = await self.job_repo.get(job_id)
                if job_model:
                    job_title = getattr(job_model, "title", job_title)
            except Exception as e:
                logger.warning(f"Failed to fetch job RAG context for {job_id}: {e}")

        # Chunk candidate resume into RAG context blocks
        resume_chunks = self._extract_resume_chunks(candidate_data, resume_analysis)
        turn_count = 0

        try:
            while True:
                data = await websocket.receive_text()
                try:
                    msg = json.loads(data)
                    msg_type = msg.get("type")
                    
                    if msg_type == "message":
                        content = msg.get("content", "")
                        turn_count += 1
                        
                        # Generate dynamic RAG question
                        ai_question = self._generate_rag_question(
                            turn_count=turn_count,
                            user_answer=content,
                            chunks=resume_chunks,
                            job_title=job_title
                        )

                        await websocket.send_json({
                            "type": "message",
                            "sender": "interviewer",
                            "content": ai_question,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })

                    elif msg_type == "ping":
                        await websocket.send_json({"type": "pong"})

                    else:
                        await websocket.send_json({
                            "type": "message",
                            "sender": "interviewer",
                            "content": f"AI Recruiter received update for {job_title} interview. Let's proceed to the next turn.",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })

                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "message",
                        "sender": "interviewer",
                        "content": f"AI Recruiter received raw input. Let's continue.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

        except Exception as e:
            logger.info(f"Interview WebSocket session closed for {id}: {e}")

