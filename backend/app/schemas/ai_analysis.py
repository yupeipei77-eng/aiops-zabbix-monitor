from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


class AIAnalysisResponse(BaseModel):
    id: int
    alert_id: int
    summary: str
    possible_causes: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    risk_level: str
    confidence: float = 0.0
    need_human_confirm: bool = False
    model_used: str
    prompt: str = ""
    raw_response: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AIAnalysisRequest(BaseModel):
    provider: Optional[str] = None
