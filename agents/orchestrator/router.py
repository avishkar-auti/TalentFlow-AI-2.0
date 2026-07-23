from typing import Any
from agents.resume_agent.agent import ResumeAgent
from agents.matching_agent.agent import MatchingAgent
from agents.background_agent.agent import BackgroundAgent

class AgentRouter:
    """Maps pipeline stages to the corresponding agents."""
    
    @staticmethod
    def get_agent_for_stage(stage: str) -> Any:
        if stage == 'screening':
            return ResumeAgent()
        elif stage == 'matching':
            return MatchingAgent()
        elif stage == 'background_check':
            return BackgroundAgent()
        return None
