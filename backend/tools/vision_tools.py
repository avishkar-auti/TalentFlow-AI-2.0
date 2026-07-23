from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from .base import BaseTool, ToolResult
from agents.interview_agent.vision import VisionProctoring

class VisionAnalyzeFrameInput(BaseModel):
    frame_data: str # base64 encoded image
    reference_photo: Optional[str] = None # base64

class VisionAnalyzeFrameOutput(BaseModel):
    face_detected: bool
    face_count: int
    gaze_direction: str
    gaze_offset: float
    head_pose: Dict[str, Any]
    ear_value: float
    flags: List[Dict[str, Any]]

class VisionAnalyzeFrameTool(BaseTool):
    name = "vision_analyze_frame"
    description = "Analyze a video frame using OpenCV and MediaPipe for proctoring & gaze/head pose estimation"
    input_schema = VisionAnalyzeFrameInput
    output_schema = VisionAnalyzeFrameOutput

    def __init__(self):
        super().__init__()
        self._proctoring_engine = VisionProctoring()

    async def execute(self, input_data: VisionAnalyzeFrameInput) -> ToolResult:
        res = await self._proctoring_engine.analyze_frame(
            frame_base64=input_data.frame_data,
            reference_photo_base64=input_data.reference_photo
        )
        return ToolResult(success=True, data=res)
