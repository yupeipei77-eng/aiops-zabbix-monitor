import json
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.models.ai_analysis import AIAnalysis
from app.models.alert import Alert
from app.models.llm_usage import LLMUsage
from app.services.alert_deduplicator import AlertDeduplicator
from app.services.storm_detector import StormDetector


class FakeRedis:
    def __init__(self):
        self.values: dict[str, str | int] = {}
        self.expirations: dict[str, int] = {}

    async def get(self, key: str):
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.values[key] = value
        if ex is not None:
            self.expirations[key] = ex
        return True

    async def incr(self, key: str):
        self.values[key] = int(self.values.get(key, 0)) + 1
        return self.values[key]

    async def expire(self, key: str, seconds: int):
        self.expirations[key] = seconds
        return True


def load_payload(name: str) -> dict:
    path = Path(__file__).resolve().parents[3] / "mock" / "zabbix_payloads" / name
    return json.loads(path.read_text())


@pytest.fixture
def fake_redis(monkeypatch):
    import app.api.v1.endpoints.zabbix_webhook as webhook_endpoint

    redis = FakeRedis()
    monkeypatch.setattr(webhook_endpoint, "deduplicator", AlertDeduplicator(redis_client=redis))
    monkeypatch.setattr(webhook_endpoint, "storm_detector", StormDetector(redis_client=redis))
    return redis


@pytest.mark.asyncio
async def test_webhook_missing_api_key_returns_401(client):
    response = await client.post("/api/v1/webhooks/zabbix", json=load_payload("cpu_high.json"))

    assert response.status_code == 401
    assert response.json() == {"success": False, "data": None, "message": "Missing API key"}


@pytest.mark.asyncio
async def test_webhook_invalid_api_key_returns_401(client):
    response = await client.post(
        "/api/v1/webhooks/zabbix",
        json=load_payload("cpu_high.json"),
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401
    assert response.json() == {"success": False, "data": None, "message": "Invalid API key"}


@pytest.mark.asyncio
async def test_webhook_cpu_alert_creates_alert_analysis_usage(client, db_session, fake_redis):
    response = await client.post(
        "/api/v1/webhooks/zabbix",
        json=load_payload("cpu_high.json"),
        headers={"X-API-Key": "changeme-webhook-api-key"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["is_duplicate"] is False

    alert = (await db_session.execute(select(Alert))).scalars().one()
    assert alert.host_name == "web-server-01"
    assert alert.tags == {"scope": "production", "team": "infra", "service": "web"}
    assert alert.dedup_key == "zabbix:host-web-01:trg-cpu-high:system.cpu.util"

    analysis_count = await db_session.scalar(select(func.count(AIAnalysis.id)))
    usage_count = await db_session.scalar(select(func.count(LLMUsage.id)))
    assert analysis_count == 1
    assert usage_count == 1
    assert "aiops:dedup:zabbix:host-web-01:trg-cpu-high:system.cpu.util" in fake_redis.values


@pytest.mark.asyncio
async def test_duplicate_webhook_updates_count_without_new_analysis(client, db_session, fake_redis):
    payload = load_payload("cpu_high.json")
    headers = {"X-API-Key": "changeme-webhook-api-key"}

    first = await client.post("/api/v1/webhooks/zabbix", json=payload, headers=headers)
    second = await client.post("/api/v1/webhooks/zabbix", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["data"]["is_duplicate"] is True
    assert second.json()["data"]["dedup_count"] == 2
    assert second.json()["data"]["alert_id"] == first.json()["data"]["alert_id"]

    alert = (await db_session.execute(select(Alert))).scalars().one()
    alert_count = await db_session.scalar(select(func.count(Alert.id)))
    analysis_count = await db_session.scalar(select(func.count(AIAnalysis.id)))
    assert alert.dedup_count == 2
    assert alert.updated_at >= alert.created_at
    assert alert_count == 1
    assert analysis_count == 1


@pytest.mark.asyncio
async def test_storm_webhook_marks_alert_and_skips_ai(client, db_session, fake_redis, monkeypatch):
    monkeypatch.setattr("app.services.storm_detector.settings.STORM_THRESHOLD", 0)
    response = await client.post(
        "/api/v1/webhooks/zabbix",
        json=load_payload("packet_loss.json"),
        headers={"X-API-Key": "changeme-webhook-api-key"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["storm_detected"] is True

    alert = (await db_session.execute(select(Alert))).scalars().one()
    assert alert.storm_detected is True
    analysis_count = await db_session.scalar(select(func.count(AIAnalysis.id)))
    assert analysis_count == 0


@pytest.mark.asyncio
async def test_alert_list_detail_manual_analyze_and_usage(client, db_session, fake_redis):
    create = await client.post(
        "/api/v1/webhooks/zabbix",
        json=load_payload("disk_full.json"),
        headers={"X-API-Key": "changeme-webhook-api-key"},
    )
    alert_id = create.json()["data"]["alert_id"]

    list_response = await client.get("/api/v1/alerts")
    detail_response = await client.get(f"/api/v1/alerts/{alert_id}")
    analysis_detail_response = await client.get(f"/api/v1/ai/alerts/{alert_id}")
    analyze_response = await client.post(f"/api/v1/ai/{alert_id}/analyze", json={})
    analysis_list_response = await client.get("/api/v1/ai")
    usage_response = await client.get("/api/v1/llm")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert detail_response.json()["data"]["id"] == alert_id
    assert analysis_detail_response.json()["data"]["alert_id"] == alert_id
    assert analyze_response.json()["success"] is True
    assert analysis_list_response.status_code == 200
    assert analysis_list_response.json()["total"] == 2
    assert usage_response.json()["total"] == 2


@pytest.mark.asyncio
async def test_knowledge_create_and_list(client):
    create_response = await client.post(
        "/api/v1/knowledge",
        json={"title": "CPU runbook", "source": "manual", "content": "check top", "tags": ["cpu"]},
    )
    list_response = await client.get("/api/v1/knowledge")

    assert create_response.status_code == 200
    assert create_response.json()["success"] is True
    assert list_response.json()["data"][0]["tags"] == ["cpu"]
