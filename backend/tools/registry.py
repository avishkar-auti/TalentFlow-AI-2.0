from typing import Dict, List, Optional
from .base import BaseTool

class ToolRegistry:
    """Registry to manage and provide access to tools, including allowlists per agent."""
    
    _tools: Dict[str, BaseTool]
    _agent_allowlists: Dict[str, List[str]]
    
    def __init__(self):
        self._tools = {}
        self._agent_allowlists = {
            "resume_agent": ["firestore_read", "firestore_write", "groq_complete", "cache_get", "cache_set"],
            "matching_agent": ["firestore_read", "firestore_write", "groq_complete", "cache_get", "cache_set"],
            "background_agent": ["firestore_read", "firestore_write", "groq_complete_lightweight", "cache_get", "cache_set"],
            "interview_agent": ["firestore_read", "firestore_write", "gemini_complete", "gemini_stream", "cache_get", "cache_set"],
            "vision_agent": ["vision_analyze_frame", "firestore_write"],
            "speech_agent": ["firestore_read", "firestore_write", "gemini_complete"],
            "technical_agent": ["firestore_read", "firestore_write", "groq_complete"],
            "decision_agent": ["firestore_read", "firestore_write", "groq_complete", "pdf_generate", "cache_get", "cache_set"],
            "notification_agent": ["firestore_read", "send_email"]
        }

    def register(self, tool: BaseTool) -> None:
        """Register a tool into the registry."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieve a specific tool by name."""
        return self._tools.get(name)

    def get_tools_for(self, agent_name: str) -> List[BaseTool]:
        """Get a list of all tools allowed for a given agent."""
        allowed_names = self._agent_allowlists.get(agent_name, [])
        return [self._tools[name] for name in allowed_names if name in self._tools]

    def is_allowed(self, agent_name: str, tool_name: str) -> bool:
        """Check if an agent is allowed to use a specific tool."""
        allowed_names = self._agent_allowlists.get(agent_name, [])
        return tool_name in allowed_names

registry = ToolRegistry()
