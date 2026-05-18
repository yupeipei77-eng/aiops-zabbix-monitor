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
    assert result["dedup_key"] == "zabbix:host-100:trg-100:system.cpu.util"


def test_normalize_severity_by_name():
    payload = ZabbixWebhookPayload(
        event_id="evt-101",
        trigger_id="trg-101",
        trigger_name="Host unavailable",
        host_id="host-101",
        host_name="web-02",
        host_ip="10.0.0.2",
        severity="Disaster",
        item_key="agent.ping",
        item_value="0",
    )
    result = AlertNormalizer.normalize(payload)
    assert result["severity"] == 5
    assert result["severity_label"] == "disaster"


def test_normalize_recovery_from_event_value():
    payload = ZabbixWebhookPayload(
        event_id="evt-102",
        trigger_id="trg-102",
        trigger_name="CPU high on web-01",
        host_id="host-102",
        host_name="web-01",
        host_ip="10.0.0.1",
        severity="Warning",
        item_key="system.cpu.util",
        item_value="22.5",
        event_value="0",
    )
    result = AlertNormalizer.normalize(payload)
    assert result["is_recovery"] is True


def test_normalize_recovery_from_status():
    payload = ZabbixWebhookPayload(
        event_id="evt-103",
        trigger_id="trg-103",
        trigger_name="Disk recovered",
        host_id="host-103",
        host_name="db-01",
        host_ip="10.0.0.3",
        severity="Average",
        item_key="vfs.fs.size[/,pfree]",
        item_value="45",
        status="RESOLVED",
    )
    result = AlertNormalizer.normalize(payload)
    assert result["is_recovery"] is True


def test_normalize_tags_accepts_string_and_list():
    string_payload = ZabbixWebhookPayload(
        event_id="evt-104",
        trigger_id="trg-104",
        trigger_name="Packet loss",
        host_id="host-104",
        host_name="app-01",
        host_ip="10.0.0.4",
        severity="Information",
        item_key="net.packet.loss",
        item_value="1.2",
        tags="scope=prod,team=infra",
    )
    list_payload = ZabbixWebhookPayload(
        event_id="evt-105",
        trigger_id="trg-105",
        trigger_name="Memory high",
        host_id="host-105",
        host_name="app-02",
        host_ip="10.0.0.5",
        severity="High",
        item_key="vm.memory.size[pused]",
        item_value="88",
        tags=[{"tag": "scope", "value": "prod"}, {"key": "team", "value": "platform"}],
    )

    assert AlertNormalizer.normalize(string_payload)["tags"] == {"scope": "prod", "team": "infra"}
    assert AlertNormalizer.normalize(list_payload)["tags"] == {"scope": "prod", "team": "platform"}
