from typing import Any

from pydantic import BaseModel


class ZabbixWebhookPayload(BaseModel):
    event_id: str
    trigger_id: str
    trigger_name: str
    host_id: str
    host_name: str
    host_ip: str
    severity: str | int = "0"
    item_key: str
    item_value: str
    event_time: str = ""
    event_value: str | int | None = None
    status: str | None = None
    tags: Any = None
    raw_payload: dict[str, Any] | None = None
