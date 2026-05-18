from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ZabbixWebhookPayload(BaseModel):
    event_id: str = ""
    trigger_id: str = ""
    trigger_name: str = ""
    host_id: str = ""
    host_name: str = ""
    host_ip: str = ""
    severity: str = "0"
    item_key: str = ""
    item_value: str = ""
    event_time: str = ""
    tags: Optional[dict] = None
    raw_payload: Optional[dict] = None
