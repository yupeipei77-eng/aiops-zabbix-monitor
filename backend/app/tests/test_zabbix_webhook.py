import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_zabbix_webhook_requires_api_key():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/webhooks/zabbix",
            json={"event_id": "test-001", "trigger_name": "Test"},
        )
    assert resp.status_code == 401
    assert resp.json()["message"] == "Missing API key"


@pytest.mark.asyncio
async def test_zabbix_webhook_invalid_api_key():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/webhooks/zabbix",
            json={"event_id": "test-001", "trigger_name": "Test"},
            headers={"X-API-Key": "wrong-key"},
        )
    assert resp.status_code == 401
    assert resp.json()["message"] == "Invalid API key"
