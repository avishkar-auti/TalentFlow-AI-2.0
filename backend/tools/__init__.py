from .base import BaseTool, ToolResult, RetryPolicy
from .registry import registry, ToolRegistry

from .firestore_tools import FirestoreReadTool, FirestoreWriteTool, FirestoreQueryTool
from .llm_tools import GroqCompleteTool, GroqCompleteLightweightTool, GeminiCompleteTool, GeminiStreamTool
from .vision_tools import VisionAnalyzeFrameTool
from .pdf_tools import PDFGenerateTool
from .email_tools import SendEmailTool
from .cache_tools import CacheGetTool, CacheSetTool

# Register all tools automatically
_tools_to_register = [
    FirestoreReadTool(),
    FirestoreWriteTool(),
    FirestoreQueryTool(),
    GroqCompleteTool(),
    GroqCompleteLightweightTool(),
    GeminiCompleteTool(),
    GeminiStreamTool(),
    VisionAnalyzeFrameTool(),
    PDFGenerateTool(),
    SendEmailTool(),
    CacheGetTool(),
    CacheSetTool(),
]

for tool in _tools_to_register:
    registry.register(tool)

__all__ = [
    "BaseTool",
    "ToolResult",
    "RetryPolicy",
    "registry",
    "ToolRegistry"
]
