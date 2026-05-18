from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AIAnalysisResponse(BaseModel):
    id: int
    alert_id: int
    summary: str
    possible_causes: str = "[]"
    suggested_actions: str = "[]"
    risk_level: str
    confidence: float = 0.0
    need_human_confirm: bool = False
    model_used: str
    prompt: str = ""
    raw_response: str = ""
    latency_ms: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AIAnalysisRequest(BaseModel):
    provider: Optional[str] = None
