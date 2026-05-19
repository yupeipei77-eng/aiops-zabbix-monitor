from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import Any


class AlertResponse(BaseModel):
    id: int
    source: str = "zabbix"
    event_id: str
    trigger_id: str
    trigger_name: str
    host_id: str
    host_name: str
    host_ip: str
    severity: int
    severity_label: str
    item_key: str
    item_value: str
    message: str = ""
    tags: dict[str, Any] = Field(default_factory=dict)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    is_recovery: bool = False
    dedup_key: str = ""
    dedup_count: int = 1
    storm_detected: bool = False
    ai_analysis_enabled: bool = True
    ai_skip_reason: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AlertListParams(BaseModel):
    page: int = 1
    page_size: int = 20
    severity: Optional[int] = None
    host_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
