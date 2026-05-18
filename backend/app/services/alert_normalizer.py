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
            "tags": tags,
            "raw_payload": payload.raw_payload or payload.model_dump(),
            "is_recovery": is_recovery,
            "dedup_key": f"zabbix:{payload.host_id}:{payload.trigger_id}:{payload.item_key}",
            "dedup_count": 1,
            "storm_detected": False,
        }

    @staticmethod
    def _parse_severity(raw: str | int) -> int:
        raw_text = str(raw).strip()
        if raw_text.isdigit():
            return min(max(int(raw_text), 0), 5)
        return SEVERITY_MAP.get(raw_text.lower(), 0)

    @staticmethod
    def _detect_recovery(payload: ZabbixWebhookPayload) -> bool:
        if str(payload.event_value).strip() == "0":
            return True
        if payload.status and payload.status.strip().upper() == "RESOLVED":
            return True
        name = payload.trigger_name.lower()
        value = payload.item_value.lower()
        recovery_keywords = ["recovery", "resolved", "ok", "up", "normal"]
        return any(kw in name or kw in value for kw in recovery_keywords)

    @staticmethod
    def _normalize_tags(tags) -> dict:
        if not tags:
            return {}
        if isinstance(tags, dict):
            return tags
        if isinstance(tags, str):
            parsed: dict[str, str] = {}
            for part in tags.split(","):
                key, sep, value = part.partition("=")
                if sep and key.strip():
                    parsed[key.strip()] = value.strip()
            return parsed
        if isinstance(tags, list):
            parsed = {}
            for item in tags:
                if isinstance(item, dict):
                    key = item.get("tag") or item.get("key") or item.get("name")
                    value = item.get("value")
                    if key is not None:
                        parsed[str(key)] = "" if value is None else str(value)
                elif isinstance(item, str):
                    key, sep, value = item.partition("=")
                    if sep and key.strip():
                        parsed[key.strip()] = value.strip()
            return parsed
        return {}
