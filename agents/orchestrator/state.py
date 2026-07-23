import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.repositories.base_repository import BaseRepository

class PipelineState(BaseModel):
    candidate_id: str
    job_id: str
    current_stage: str = 'applied'
    stage_results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    def update_stage(self, new_stage: str, result: Any = None):
        self.stage_results[self.current_stage] = result
        self.current_stage = new_stage
        self.updated_at = datetime.datetime.utcnow()
        
    def add_error(self, stage: str, error: str):
        self.errors.append({
            'stage': stage,
            'error': error,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })

class PipelineStateRepository(BaseRepository[PipelineState]):
    def __init__(self):
        super().__init__('pipeline_states', PipelineState)
        
    async def get_state(self, candidate_id: str, job_id: str) -> Optional[PipelineState]:
        states = await self.query([
            ('candidate_id', '==', candidate_id),
            ('job_id', '==', job_id)
        ], limit=1)
        return states[0] if states else None
        
    async def save_state(self, state: PipelineState) -> PipelineState:
        doc_id = f"{state.candidate_id}_{state.job_id}"
        return await self.create(doc_id, state)
