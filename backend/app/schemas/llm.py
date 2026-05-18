from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LLMUsageResponse(BaseModel):
    id: int
    provider: str
    model: str
    context: str = "alert_analysis"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    success: bool = True
    error_message: str = ""
    cached: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
