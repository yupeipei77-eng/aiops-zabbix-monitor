import pytest
import httpx
from sqlalchemy import select

from app.llm.deepseek_provider import DeepSeekProvider
from app.llm.mock_provider import MockLLMProvider
from app.models.ai_analysis import AIAnalysis
from app.models.alert import Alert
from app.models.llm_usage import LLMUsage
from app.services.ai_orchestrator import AIOrchestrator


@pytest.mark.asyncio
async def test_mock_provider_analyze():
    provider = MockLLMProvider()
    result = await provider.analyze_alert("test prompt")
    assert "summary" in result
    assert "possible_causes" in result
    assert "suggested_actions" in result
    assert result["risk_level"] in ["low", "medium", "high", "critical"]
    assert 0 <= result["confidence"] <= 1


@pytest.mark.asyncio
async def test_mock_provider_health():
    provider = MockLLMProvider()
    assert await provider.health_check() is True
    assert provider.is_available() is True


@pytest.mark.asyncio
async def test_deepseek_provider_parses_openai_compatible_json(monkeypatch):
    monkeypatch.setattr("app.llm.deepseek_provider.settings.DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.deepseek_provider.settings.DEEPSEEK_BASE_URL", "https://deepseek.test/v1")
    monkeypatch.setattr("app.llm.deepseek_provider.settings.DEEPSEEK_MODEL", "deepseek-chat")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://deepseek.test/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-key"
        payload = request.read().decode()
        assert "deepseek-chat" in payload
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "summary": "CPU saturation detected",
                              "possible_causes": ["traffic spike", "busy process"],
                              "suggested_actions": ["check top", "scale service"],
                              "risk_level": "high",
                              "confidence": 0.82,
                              "need_human_confirm": true
                            }
                            """
                        }
                    }
                ]
            },
        )

    provider = DeepSeekProvider(transport=httpx.MockTransport(handler))

    result = await provider.analyze_alert("Analyze this alert")

    assert result == {
        "summary": "CPU saturation detected",
        "possible_causes": ["traffic spike", "busy process"],
        "suggested_actions": ["check top", "scale service"],
        "risk_level": "high",
        "confidence": 0.82,
        "need_human_confirm": True,
    }


@pytest.mark.asyncio
async def test_orchestrator_falls_back_to_mock_when_deepseek_call_fails(db_session, monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.ADVANCED_LLM_PROVIDER", "deepseek")
    monkeypatch.setattr("app.llm.deepseek_provider.settings.DEEPSEEK_API_KEY", "test-key")

    async def fail_deepseek(_self, _prompt):
        raise RuntimeError("deepseek timeout")

    monkeypatch.setattr(DeepSeekProvider, "analyze_alert", fail_deepseek)
    alert = Alert(
        source="zabbix",
        event_id="evt-deepseek",
        trigger_id="trg-deepseek",
        trigger_name="CPU usage over 90%",
        host_id="host-deepseek",
        host_name="web-01",
        host_ip="10.0.0.1",
        severity=5,
        severity_label="disaster",
        item_key="system.cpu.util",
        item_value="96",
        message="CPU usage over 90%",
        tags={},
        raw_payload={},
        is_recovery=False,
        dedup_key="zabbix:host-deepseek:trg-deepseek:system.cpu.util",
        dedup_count=1,
        storm_detected=False,
    )
    db_session.add(alert)
    await db_session.flush()

    result = await AIOrchestrator(db_session).analyze_alert(alert.id)

    assert result["success"] is True
    assert result["data"]["model_used"] == "mock"
    assert "deepseek" in result["data"]["fallback_reason"].lower()

    analyses = (await db_session.execute(select(AIAnalysis))).scalars().all()
    usage = (await db_session.execute(select(LLMUsage).order_by(LLMUsage.id))).scalars().all()
    assert len(analyses) == 1
    assert analyses[0].model_used == "mock"
    assert [(row.provider, row.success) for row in usage] == [("deepseek", False), ("mock", True)]
    assert usage[0].model == "deepseek-chat"
