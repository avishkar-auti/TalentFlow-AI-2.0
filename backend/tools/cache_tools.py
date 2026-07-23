import os
import json
from typing import Any, Dict, Optional
from pydantic import BaseModel
import aiofiles
from .base import BaseTool, ToolResult

CACHE_BASE_DIR = os.path.join("backend", "temp")

class CacheGetInput(BaseModel):
    candidate_id: str
    agent: str
    filename: str

class CacheGetOutput(BaseModel):
    data: Optional[Dict[str, Any]]

class CacheGetTool(BaseTool):
    name = "cache_get"
    description = "Read JSON from candidate agent cache"
    input_schema = CacheGetInput
    output_schema = CacheGetOutput

    async def execute(self, input_data: CacheGetInput) -> ToolResult:
        path = os.path.join(CACHE_BASE_DIR, f"candidate_{input_data.candidate_id}", input_data.agent, f"{input_data.filename}.json")
        if not os.path.exists(path):
            return ToolResult(success=True, data={"data": None})
            
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return ToolResult(success=True, data={"data": json.loads(content)})

class CacheSetInput(BaseModel):
    candidate_id: str
    agent: str
    filename: str
    data: Dict[str, Any]

class CacheSetOutput(BaseModel):
    success: bool

class CacheSetTool(BaseTool):
    name = "cache_set"
    description = "Write JSON to candidate agent cache"
    input_schema = CacheSetInput
    output_schema = CacheSetOutput

    async def execute(self, input_data: CacheSetInput) -> ToolResult:
        dir_path = os.path.join(CACHE_BASE_DIR, f"candidate_{input_data.candidate_id}", input_data.agent)
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path, f"{input_data.filename}.json")
        
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(input_data.data, indent=2))
            
        return ToolResult(success=True, data={"success": True})
