from app.schemas.zabbix import ZabbixWebhookPayload
from app.core.logging import get_logger

logger = get_logger(__name__)

SEVERITY_MAP = {
    "not classified": 0,
    "information": 1,
    "warning": 2,
    "average": 3,
    "high": 4,
    "disaster": 5,
}

SEVERITY_LABELS = {0: "not_classified", 1: "information", 2: "warning", 3: "average", 4: "high", 5: "disaster"}


class AlertNormalizer:
    @staticmethod
    def normalize(payload: ZabbixWebhookPayload) -> dict:
        severity = AlertNormalizer._parse_severity(payload.severity)
        severity_label = SEVERITY_LABELS.get(severity, "not_classified")
        is_recovery = AlertNormalizer._detect_recovery(payload)
        tags = AlertNormalizer._normalize_tags(payload.tags)
        import json

        return {
            "source": "zabbix",
            "event_id": payload.event_id,
            "trigger_id": payload.trigger_id,
            "trigger_name": payload.trigger_name,
            "host_id": payload.host_id,
            "host_name": payload.host_name,
            "host_ip": payload.host_ip,
            "severity": severity,
            "severity_label": severity_label,
            "item_key": payload.item_key,
            "item_value": payload.item_value,
            "message": payload.trigger_name,
            "tags": json.dumps(tags, ensure_ascii=False),
            "raw_payload": json.dumps(payload.raw_payload or payload.model_dump(), ensure_ascii=False),
            "is_recovery": is_recovery,
            "dedup_key": f"zabbix:{payload.trigger_id}:{payload.host_id}",
            "dedup_count": 1,
            "storm_detected": False,
        }

    @staticmethod
    def _parse_severity(raw: str) -> int:
        if raw.isdigit():
            return min(max(int(raw), 0), 5)
        return SEVERITY_MAP.get(raw.lower(), 0)

    @staticmethod
    def _detect_recovery(payload: ZabbixWebhookPayload) -> bool:
        name = payload.trigger_name.lower()
        value = payload.item_value.lower()
        recovery_keywords = ["recovery", "resolved", "ok", "up", "normal"]
        return any(kw in name or kw in value for kw in recovery_keywords)

    @staticmethod
    def _normalize_tags(tags: dict | None) -> dict:
        if tags and isinstance(tags, dict):
            return tags
        return {}
