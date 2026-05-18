from app.services.alert_normalizer import AlertNormalizer
from app.schemas.zabbix import ZabbixWebhookPayload


def test_normalize_basic():
    payload = ZabbixWebhookPayload(
        event_id="evt-100",
        trigger_id="trg-100",
        trigger_name="CPU high on web-01",
        host_id="host-100",
        host_name="web-01",
        host_ip="10.0.0.1",
        severity="4",
        item_key="system.cpu.util",
        item_value="92.5",
    )
    result = AlertNormalizer.normalize(payload)
    assert result["severity"] == 4
    assert result["severity_label"] == "high"
    assert result["is_recovery"] is False
    assert result["dedup_key"] == "zabbix:trg-100:host-100"


def test_normalize_severity_by_name():
    payload = ZabbixWebhookPayload(severity="disaster")
    result = AlertNormalizer.normalize(payload)
    assert result["severity"] == 5
    assert result["severity_label"] == "disaster"


def test_normalize_recovery():
    payload = ZabbixWebhookPayload(
        trigger_name="CPU recovered on web-01",
        item_value="OK",
    )
    result = AlertNormalizer.normalize(payload)
    assert result["is_recovery"] is True
