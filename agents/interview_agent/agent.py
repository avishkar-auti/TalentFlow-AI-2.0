from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from .models import InterviewSession, InterviewTurn, InterviewerResponse, InterviewResult, SessionStatus, InterviewPhase
from .prompts import INTERVIEWER_SYSTEM_PROMPT, PHASE_PROMPTS
from .utils import build_context_window, format_turn_for_llm
# Assuming tools layer exists as specified
# from tools.llm_tools import generate_text 

logger = logging.getLogger(__name__)

class InterviewAgent:
    def __init__(self):
        # Initialize any required tools or clients here
        pass

    async def start_session(self, interview_id: str, candidate_id: str, job_id: str) -> InterviewSession:
        logger.info(f"Starting interview session {interview_id} for candidate {candidate_id}")
        session = InterviewSession(
            interview_id=interview_id,
            candidate_id=candidate_id,
            job_id=job_id,
            status=SessionStatus.INITIALIZED,
            current_phase=InterviewPhase.CONSENT
        )
        # Store initial session in DB
        return session

    async def process_turn(self, session: InterviewSession, candidate_message: str) -> InterviewerResponse:
        logger.info(f"Processing turn for session {session.interview_id}, phase: {session.current_phase}")
        
        # Add candidate turn
        session.turns.append(InterviewTurn(
            speaker="candidate",
            message=candidate_message,
            phase=session.current_phase
        ))

        # Build context
        context_turns = build_context_window(session.turns, max_turns=3)
        
        # Prepare LLM messages
        messages = [{"role": "system", "content": INTERVIEWER_SYSTEM_PROMPT}]
        
        phase_instruction = PHASE_PROMPTS.get(session.current_phase.value, "")
        if phase_instruction:
             messages.append({"role": "system", "content": f"Current Phase Objective: {phase_instruction}"})

        for turn in context_turns:
            messages.append(format_turn_for_llm(turn))

        # Call LLM tool (mocked for now, assuming tools.llm_tools exists)
        # response_text = await generate_text(messages=messages, model="gemini-1.5-flash")
        response_text = f"Mocked LLM response for phase {session.current_phase}"
        
        # Logic to transition phases based on turn count or LLM extraction could go here
        next_phase = session.current_phase # Keep current phase by default
        
        # Add interviewer turn
        session.turns.append(InterviewTurn(
            speaker="interviewer",
            message=response_text,
            phase=next_phase
        ))
        
        return InterviewerResponse(message=response_text, next_phase=next_phase)

    async def end_session(self, session: InterviewSession) -> InterviewResult:
        logger.info(f"Ending session {session.interview_id}")
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.utcnow()
        session.current_phase = InterviewPhase.ENDED
        
        from .utils import generate_proctoring_summary
        summary = generate_proctoring_summary(session.proctoring.flags)
        
        result = InterviewResult(
            interview_id=session.interview_id,
            status=session.status,
            transcript=session.turns,
            proctoring_summary=summary,
            completion_time=session.end_time
        )
        return result
