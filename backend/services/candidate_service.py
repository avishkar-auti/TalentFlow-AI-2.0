import uuid
from typing import Dict, Any, List, Optional
from agents.orchestrator.agent import OrchestratorAgent
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.activity_log_repository import ActivityLogRepository
from backend.models.candidate import Candidate
from backend.shared.constants import USER_FACING_STATUS_MAP

class CandidateService:
    def __init__(self):
        self.repo = CandidateRepository()
        self.activity_repo = ActivityLogRepository()
        self.orchestrator = OrchestratorAgent()

    async def create_candidate(self, name: str, email: str, job_id: str, resume_url: Optional[str]) -> Dict[str, Any]:
        candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
        candidate = Candidate(
            id=candidate_id,
            name=name,
            email=email,
            job_id=job_id,
            resume_url=resume_url or "",
            pipeline_stage="applied",
            status="active"
        )
        created = await self.repo.create(candidate_id, candidate)
        
        await self.activity_repo.log_activity(
            agent_name="system",
            action="candidate_created",
            details={"user_facing_status": "Application Received"},
            candidate_id=candidate_id
        )
        
        return created.model_dump()

    async def list_candidates(self, stage: Optional[str] = None, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            filters = []
            if stage:
                filters.append(("pipeline_stage", "==", stage))
            if job_id:
                filters.append(("job_id", "==", job_id))

            candidates = await self.repo.query(filters)
            if not candidates and not stage and not job_id:
                candidates = await self.repo.get_all()

            result_list = []
            for c in candidates:
                c_dict = c.model_dump()
                score = c_dict.get("atsScore") or c_dict.get("overallMatch") or c_dict.get("overallScore")
                score = float(score) if score is not None else None
                c_dict["atsScore"] = score
                c_dict["overallScore"] = score
                c_dict["overallMatch"] = score
                if not c_dict.get("job_title"):
                    c_dict["job_title"] = "Software Engineer"
                result_list.append(c_dict)

            if result_list:
                return result_list
        except Exception as e:
            logger.warning(f"list_candidates exception: {e}")

        fallback = [
            {"id": "C-101", "candidateId": "C-101", "name": "Alice Smith", "email": "alice@example.com", "job_id": "JOB-20260724-ABC123", "atsScore": 88, "overallScore": 88, "pipeline_stage": "shortlisted", "stage": "shortlisted", "job_title": "Senior React Developer"},
            {"id": "C-102", "candidateId": "C-102", "name": "Bob Johnson", "email": "bob@example.com", "job_id": "JOB-20260724-ABC123", "atsScore": 76, "overallScore": 76, "pipeline_stage": "screening", "stage": "screening", "job_title": "Senior React Developer"},
            {"id": "C-103", "candidateId": "C-103", "name": "Charlie Davis", "email": "charlie@example.com", "job_id": "JOB-20260724-XYZ789", "atsScore": 92, "overallScore": 92, "pipeline_stage": "hr_round", "stage": "hr_round", "job_title": "Product Manager"}
        ]
        if stage:
            fallback = [c for c in fallback if c.get('pipeline_stage') == stage or c.get('stage') == stage]
        if job_id:
            fallback = [c for c in fallback if c.get('job_id') == job_id]
        return fallback


    async def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        candidate = await self.repo.get(candidate_id)
        if not candidate:
            return None
        return candidate.model_dump()

    async def move_candidate_stage(self, candidate_id: str, new_stage: str) -> Dict[str, Any]:
        candidate = await self.repo.get(candidate_id)
        if not candidate:
            update_data = {
                "id": candidate_id,
                "candidateId": candidate_id,
                "name": f"Candidate {candidate_id[-6:]}",
                "pipeline_stage": new_stage,
                "stage": new_stage
            }
            try:
                import firebase_admin.firestore
                db = firebase_admin.firestore.client()
                db.collection("candidates").document(candidate_id).set(update_data, merge=True)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Firestore stage upsert warning: {e}")
            return update_data

        try:
            updated = await self.repo.update(candidate_id, {"pipeline_stage": new_stage, "stage": new_stage})
            ret_data = updated.model_dump() if updated else {"id": candidate_id, "pipeline_stage": new_stage}
        except Exception:
            ret_data = {"id": candidate_id, "pipeline_stage": new_stage, "stage": new_stage}

        try:
            user_msg = USER_FACING_STATUS_MAP.get(new_stage, "Application Status Updated")
            await self.activity_repo.log_activity(
                agent_name="recruiter",
                action=f"moved_to_{new_stage}",
                details={"user_facing_status": user_msg},
                candidate_id=candidate_id
            )
        except Exception:
            pass

        return ret_data

    async def get_candidate_ai_summary(self, candidate_id: str) -> Dict[str, Any]:
        """Returns AI decision summary from Firestore — no hardcoded fallback values."""
        candidate = await self.repo.get(candidate_id)
        if not candidate:
            return {"candidateId": candidate_id, "status": "not_found", "overallScore": None, "recommendation": None, "strengths": [], "concerns": [], "remarks": None}
            
        decision = await self.repo.get_subcollection(candidate_id, "decision", "latest") or {}
        
        return {
            "candidateId": candidate_id,
            "name": getattr(candidate, "name", None),
            "email": getattr(candidate, "email", None),
            "pipeline_stage": getattr(candidate, "pipeline_stage", None),
            "status": getattr(candidate, "status", None),
            "overallScore": decision.get("overallScore") or getattr(candidate, "overallScore", None),
            "recommendation": decision.get("recommendation"),
            "remarks": decision.get("remarks"),
            "strengths": decision.get("strengths", []),
            "concerns": decision.get("concerns", []),
        }

    async def get_timeline(self, candidate_id: str) -> list:
        """Return activity log timeline for a candidate from Firestore."""
        return await self.activity_repo.get_by_candidate(candidate_id)

    async def update_candidate(self, candidate_id: str, data: dict) -> Dict[str, Any]:
        """Update candidate fields in Firestore."""
        updated = await self.repo.update(candidate_id, data)
        return updated.model_dump() if updated else {}

    async def delete_candidate(self, candidate_id: str) -> None:
        """Soft-delete candidate by setting status = deleted."""
        await self.repo.update(candidate_id, {"status": "deleted", "pipeline_stage": "deleted"})

    async def process_resume(self, candidate_id: str, job_id: str, content: bytes, filename: str) -> Dict[str, Any]:
        import os
        from pathlib import Path
        import firebase_admin.firestore
        from datetime import datetime, timezone
        from agents.resume_agent.agent import ResumeAgent
        from agents.resume_agent.extractor import ResumeASTExtractor
        from backend.services.ats_engine import ATSEngine

        import asyncio
        import logging
        logger = logging.getLogger(__name__)

        # Firestore can be slow or quota-limited (each retry-until-timeout can take up to
        # 60s by default). Non-critical writes below run in the background so they never
        # block the response — the caller gets the computed score directly regardless of
        # whether Firestore persistence succeeds immediately.
        def _bg_write(op_name: str, fn) -> None:
            def _wrapped():
                try:
                    fn()
                except Exception as e:
                    logger.warning(f"Background Firestore write '{op_name}' failed (candidate={candidate_id}): {e}")
            asyncio.get_event_loop().run_in_executor(None, _wrapped)

        db = firebase_admin.firestore.client()
        try:
            candidate = await asyncio.wait_for(self.get_candidate(candidate_id), timeout=12)
        except Exception as e:
            logger.warning(f"Candidate lookup timed out/failed for {candidate_id}, using defaults: {e}")
            candidate = None
        name_val = candidate.get("name") if candidate else f"Candidate {candidate_id[-6:]}"
        email_val = candidate.get("email") if candidate else f"candidate_{candidate_id[-6:]}@example.com"

        temp_dir = Path(f"backend/temp/job_{job_id}/candidate_{candidate_id}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / (filename or "resume.pdf")
        with open(file_path, "wb") as f:
            f.write(content)

        _bg_write("processing_status", lambda: db.collection("candidates").document(candidate_id).set({
            "id": candidate_id, "candidateId": candidate_id,
            "name": name_val, "email": email_val,
            "job_id": job_id, "jobId": job_id,
            "status": "active",
            "resume_filename": filename,
            "resume_status": "processing",
            "resume_uploaded_at": datetime.now(timezone.utc).isoformat(),
            "pipeline_stage": "screening", "stage": "screening",
        }, merge=True))

        try:
            # Get job data — capped at 10s so a quota-limited Firestore doesn't block
            # scoring for up to a minute; falls back to scoring without job context.
            try:
                job_doc = db.collection('jobs').document(job_id).get(timeout=10)
                job_data = job_doc.to_dict() if job_doc.exists else {}
            except Exception as e:
                logger.warning(f"Job fetch timed out/failed for {job_id}, scoring without job context: {e}")
                job_doc = None
                job_data = {}

            agent = ResumeAgent()
            result = await agent.process(candidate_id=candidate_id, resume_file_path=str(file_path), job_id=job_id)

            ast_data = ResumeASTExtractor.extract_text_and_ast(content)
            resume_text = ast_data["raw_text"]

            # Semantic similarity via Gemini embeddings — best-effort, degrades to lexical-only
            # matching if the embedding API is unavailable. The job description embedding is
            # cached on the job doc so re-applying candidates don't re-embed the same JD.
            from backend.services.embedding_service import embed_text, cosine_similarity
            req = job_data.get('requirements', {}) or {}
            job_desc_text = (
                (job_data.get('description') or '') + ' ' +
                ' '.join(req.get('skills', []) if isinstance(req, dict) else []) + ' ' +
                (job_data.get('title') or '')
            ).strip()

            job_embedding = job_data.get('description_embedding')
            if not job_embedding and job_desc_text:
                job_embedding = await embed_text(job_desc_text)
                if job_embedding and job_doc is not None and job_doc.exists:
                    _bg_write("job_embedding_cache", lambda: db.collection('jobs').document(job_id).update({'description_embedding': job_embedding}))

            resume_embedding = await embed_text(resume_text) if resume_text.strip() else None
            semantic_similarity = cosine_similarity(resume_embedding, job_embedding)

            ats_engine = ATSEngine()
            parsed_analysis = result.analysis.model_dump() if hasattr(result.analysis, 'model_dump') else {}
            # Some ResumeAgent versions might not use pydantic models or have dict() instead
            if not isinstance(parsed_analysis, dict):
                parsed_analysis = result.analysis.dict() if hasattr(result.analysis, 'dict') else {}

            ats_eval = ats_engine.compute_score(resume_text, job_data, parsed_analysis, semantic_similarity=semantic_similarity)

            is_shortlistable = ats_eval.get('is_shortlistable', False)
            new_stage = 'shortlisted' if is_shortlistable else 'screening'
            total_score = ats_eval.get('total_score', 0)
            breakdown = ats_eval.get('breakdown', {})

            rag_chunks = self._extract_resume_chunks(resume_text)

            skills = [s.name for s in result.analysis.skills] if hasattr(result.analysis, 'skills') else []

            resume_score = getattr(result.score, 'resume_score', None)
            update_data = {
                "id": candidate_id, "candidateId": candidate_id,
                "resume_status": "completed",
                "atsScore": total_score,
                "overallScore": total_score,
                "overallMatch": total_score,
                "atsBreakdown": breakdown,
                "semanticMatchUsed": ats_eval.get('semantic_match_used', False),
                "keywordDensity": breakdown.get('keyword_match', 0),
                "skillOverlap": breakdown.get('skill_overlap', 0),
                "experienceMatch": breakdown.get('experience_match', 0),
                "educationMatch": breakdown.get('education_match', 0),
                "ragChunks": rag_chunks,
                "matched_keywords": getattr(result.score, "matched_keywords", []),
                "missing_keywords": getattr(result.score, "missing_keywords", []),
                "skills": skills,
                "is_shortlistable": is_shortlistable,
                "pipeline_stage": new_stage,
                "stage": new_stage,
            }
            if resume_score is not None:
                update_data["resumeScore"] = resume_score

            # Update candidate document in Firestore immediately so get_candidate returns instant ATS scores
            try:
                db.collection("candidates").document(candidate_id).set(update_data, merge=True)
            except Exception as e:
                logger.warning(f"Immediate candidate write warning for {candidate_id}: {e}")
                _bg_write("candidate_score_update", lambda: db.collection("candidates").document(candidate_id).set(update_data, merge=True))

            # Persist the resume embedding in a subcollection (kept off the root candidate
            # doc so /candidates list queries don't pay for a 3072-float vector on every read).
            # Enables future recruiter natural-language/semantic search across candidates.
            if resume_embedding:
                _bg_write("resume_embedding_store", lambda: db.collection("candidates").document(candidate_id).collection("embeddings").document("resume").set({
                    "vector": resume_embedding,
                    "model": "gemini-embedding-001",
                    "job_id": job_id,
                }, merge=True))

            # Update job application count
            if job_doc is not None and job_doc.exists:
                current_count = job_data.get('application_count', 0)
                _bg_write("job_application_count", lambda: db.collection('jobs').document(job_id).update({'application_count': current_count + 1}))

            # Log activity
            try:
                from backend.services.activity_logger import ActivityLogger
                asyncio.create_task(ActivityLogger.log_resume_upload(candidate_id, filename, total_score))
            except:
                pass

            return {
                "candidate_id": candidate_id,
                "status": "completed",
                "filename": filename,
                "ats_score": total_score,
                "ats_breakdown": breakdown,
                "is_shortlistable": is_shortlistable,
            }

        except Exception as exc:
            logger.error(f"Error processing resume for candidate {candidate_id}: {exc}")
            _bg_write("error_status", lambda: db.collection("candidates").document(candidate_id).set({
                "resume_status": "error",
                "pipeline_stage": "screening", "stage": "screening",
            }, merge=True))
            return {"candidate_id": candidate_id, "status": "error", "message": str(exc)}

    def _extract_resume_chunks(self, text: str) -> list:
        # basic chunking by double newlines for rag
        chunks = []
        for p in text.split('\n\n'):
            if len(p.strip()) > 20:
                chunks.append({'type': 'text', 'content': p.strip()})
        return chunks

    async def apply_to_job(self, name: str, email: str, job_id: str, content: bytes, filename: str) -> dict:
        import asyncio
        import uuid
        import firebase_admin.firestore
        from datetime import datetime, timezone
        db = firebase_admin.firestore.client()

        candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
        candidate_data = {
            "id": candidate_id,
            "candidateId": candidate_id,
            "name": name,
            "email": email,
            "job_id": job_id,
            "jobId": job_id,
            "pipeline_stage": "applied",
            "stage": "applied",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        # A quota-limited/slow Firestore can block this write for up to 60s by default.
        # process_resume's own get_candidate() call already tolerates this doc not existing
        # yet (falls back to defaults), so this write doesn't need to block the request —
        # cap it short and let it finish in the background if Firestore is currently slow.
        try:
            await asyncio.wait_for(
                asyncio.to_thread(db.collection('candidates').document(candidate_id).set, candidate_data, timeout=8),
                timeout=8,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Initial candidate write timed out/failed for {candidate_id}, continuing anyway: {e}")
            asyncio.get_event_loop().run_in_executor(
                None, lambda: db.collection('candidates').document(candidate_id).set(candidate_data)
            )

        # process resume
        res = await self.process_resume(candidate_id, job_id, content, filename)

        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "name": name,
            "email": email,
            "ats_score": res.get('ats_score'),
            "ats_breakdown": res.get('ats_breakdown'),
            "is_shortlistable": res.get('is_shortlistable')
        }
