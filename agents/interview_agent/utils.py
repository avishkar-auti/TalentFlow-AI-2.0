from typing import List, Dict, Any
from .models import InterviewTurn

def build_context_window(turns: List[InterviewTurn], max_turns: int = 3) -> List[InterviewTurn]:
    """Returns the last `max_turns` of conversation."""
    return turns[-max_turns:]

def format_turn_for_llm(turn: InterviewTurn) -> Dict[str, str]:
    """Formats a turn for the LLM API."""
    role = "assistant" if turn.speaker == "interviewer" else "user"
    return {"role": role, "content": turn.message}

def generate_proctoring_summary(flags: List[Any]) -> Dict[str, Any]:
    """Summarizes proctoring flags."""
    summary = {}
    for flag in flags:
        summary[flag.flag_type.value] = summary.get(flag.flag_type.value, 0) + 1
    return {
        "total_flags": len(flags),
        "flag_counts": summary
    }
