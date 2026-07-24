"""
Resume Agent Orchestrator.
Orchestrates layout extraction (AST), structure parsing (LLM/rule), ATS scoring, and Firestore/Storage persistence.
"""
import asyncio
import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from .extractor import ResumeASTExtractor
from .parser import ResumeParser
from .ats import ATSScanner
from .models import ResumeAnalysis, ResumeScore, ResumeAnalysisResult, Skill
from .firebase import save_analysis, get_job_requirements_from_firestore, save_resume_file_to_storage

logger = logging.getLogger(__name__)

class ResumeAgent:
    """Production Resume Agent for TalentFlow-AI."""

    async def process(
        self,
        candidate_id: str,
        resume_file_path: str,
        job_id: Optional[str] = None,
        job_requirements: Optional[List[str]] = None
    ) -> ResumeAnalysisResult:
        """
        Full End-to-End Resume Processing:
        1. Local AST Layout & Text Extraction (PyMuPDF)
        2. Fetch Target Job Requirements from Firestore
        3. Structured Resume Parsing (Groq LLM / AST Fallback)
        4. Real ATS Scanning & Quality Evaluation
        5. Write Analysis & Resume Record to Firestore & Firebase Storage
        """
        logger.info(f"Processing resume for candidate_id={candidate_id}, file={resume_file_path}")

        # 1. Read file bytes & extract layout AST
        if not os.path.exists(resume_file_path):
            raise FileNotFoundError(f"Resume file not found at path: {resume_file_path}")

        with open(resume_file_path, "rb") as f:
            file_bytes = f.read()

        filename = os.path.basename(resume_file_path)
        ast_data = ResumeASTExtractor.extract_text_and_ast(file_bytes)
        raw_text = ast_data["raw_text"]

        # 2. Fetch real job requirements from Firestore if job_id provided
        if job_id and not job_requirements:
            job_requirements = await get_job_requirements_from_firestore(job_id)
        if job_requirements is None:
            job_requirements = []

        # 3. Parse resume structure into typed AST fields
        parsed_dict = await ResumeParser.parse_resume_content(raw_text, ast_data["blocks_ast"])
        
        # Convert dictionary to ResumeAnalysis typed model
        try:
            analysis = ResumeAnalysis(**parsed_dict)
        except Exception as e:
            logger.warning(f"Schema validation warning: {e}. Building fallback ResumeAnalysis.")
            skills_objs = [
                Skill(name=s.get("name", s) if isinstance(s, dict) else str(s)) 
                for s in parsed_dict.get("skills", [])
            ]
            analysis = ResumeAnalysis(
                parsedText=raw_text[:1500],
                skills=skills_objs,
                education=parsed_dict.get("education", []),
                companies=parsed_dict.get("companies", []),
                experience=parsed_dict.get("experience", "1+ Years"),
                projects=parsed_dict.get("projects", []),
                certifications=parsed_dict.get("certifications", [])
            )

        # 4. Perform ATS Scanning & Quality Evaluation
        skill_names = [s.name for s in analysis.skills]
        ats_results = ATSScanner.scan_resume(
            extracted_text=raw_text,
            ast_data=ast_data,
            parsed_skills=skill_names,
            job_requirements=job_requirements
        )

        score = ResumeScore(
            ats_score=ats_results["ats_score"],
            resume_score=ats_results["resume_quality_score"],
            missing_keywords=ats_results["missing_keywords"]
        )

        result = ResumeAnalysisResult(analysis=analysis, score=score)

        # 5. Persist resume file to Firebase Storage & Document to Firestore.
        # Neither write is needed to return the computed score to the caller, so both run
        # in the background — a slow/quota-limited Firestore or Storage no longer adds
        # its latency to every resume upload request.
        full_persist_data = result.model_dump()
        full_persist_data["atsFormattingScore"] = ats_results["ats_formatting_score"]
        full_persist_data["formattingFlags"] = ats_results["formatting_flags"]

        async def _persist():
            try:
                storage_url = await save_resume_file_to_storage(candidate_id, file_bytes, filename)
                full_persist_data["resumeUrl"] = storage_url
                await save_analysis(candidate_id, full_persist_data)
            except Exception as e:
                logger.warning(f"Background persistence failed for candidate {candidate_id}: {e}")

        asyncio.create_task(_persist())

        # Cache results locally for instant lookup
        try:
            cache_dir = Path(f"backend/temp/candidate_{candidate_id}/resume_agent")
            cache_dir.mkdir(parents=True, exist_ok=True)
            with open(cache_dir / "analysis.json", "w", encoding="utf-8") as f:
                json.dump(full_persist_data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not cache results locally: {e}")

        logger.info(f"Resume analysis complete for {candidate_id}. ATS Score: {score.ats_score}%")
        return result
