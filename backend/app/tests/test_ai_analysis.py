import pytest
import httpx
from sqlalchemy import select

from app.llm.deepseek_provider import DeepSeekProvider
from app.llm.gateway_provider import OpenAICompatibleGatewayProvider
from app.llm.mimo_provider import MimoProvider
from app.llm.mock_provider import MockLLMProvider
from app.models.ai_analysis import AIAnalysis
from app.models.alert import Alert
from app.models.llm_usage import LLMUsage
from app.services.ai_orchestrator import AIOrchestrator
from app.services.model_router import ModelRouter


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
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "deepseek")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "deepseek-chat")
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


@pytest.mark.asyncio
async def test_mimo_provider_parses_openai_compatible_json(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_API_KEY", "test-mimo-key")
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_BASE_URL", "https://mimo.test/v1")
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_MODEL", "mimo-test-model")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://mimo.test/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-mimo-key"
        assert request.headers["content-type"] == "application/json"
        payload = request.read().decode()
        assert "mimo-test-model" in payload
        assert "response_format" in payload
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": """
                            ```json
                            {
                              "summary": "Disk usage is high",
                              "possible_causes": "log files are growing",
                              "suggested_actions": "clean old logs",
                              "risk_level": "critical",
                              "confidence": 1.4,
                              "need_human_confirm": true
                            }
                            ```
                            """
                        }
                    }
                ]
            },
        )

    provider = MimoProvider(transport=httpx.MockTransport(handler))

    result = await provider.analyze_alert("Analyze this alert")

    assert result == {
        "summary": "Disk usage is high",
        "possible_causes": ["log files are growing"],
        "suggested_actions": ["clean old logs"],
        "risk_level": "critical",
        "confidence": 1.0,
        "need_human_confirm": True,
    }


@pytest.mark.asyncio
async def test_orchestrator_falls_back_to_mock_when_mimo_call_fails(db_session, monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "mimo")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "mimo-test-model")
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_API_KEY", "test-mimo-key")
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_MODEL", "mimo-test-model")

    async def fail_mimo(_self, _prompt):
        raise RuntimeError("mimo timeout")

    monkeypatch.setattr(MimoProvider, "analyze_alert", fail_mimo)
    alert = Alert(
        source="zabbix",
        event_id="evt-mimo",
        trigger_id="trg-mimo",
        trigger_name="Disk usage over 95%",
        host_id="host-mimo",
        host_name="db-01",
        host_ip="10.0.0.2",
        severity=5,
        severity_label="disaster",
        item_key="vfs.fs.size[/,pused]",
        item_value="97",
        message="Disk usage over 95%",
        tags={},
        raw_payload={},
        is_recovery=False,
        dedup_key="zabbix:host-mimo:trg-mimo:vfs.fs.size[/,pused]",
        dedup_count=1,
        storm_detected=False,
    )
    db_session.add(alert)
    await db_session.flush()

    result = await AIOrchestrator(db_session).analyze_alert(alert.id)

    assert result["success"] is True
    assert result["data"]["model_used"] == "mock"
    assert "mimo" in result["data"]["fallback_reason"].lower()

    analyses = (await db_session.execute(select(AIAnalysis))).scalars().all()
    usage = (await db_session.execute(select(LLMUsage).order_by(LLMUsage.id))).scalars().all()
    assert len(analyses) == 1
    assert analyses[0].model_used == "mock"
    assert [(row.provider, row.success) for row in usage] == [("mimo", False), ("mock", True)]
    assert usage[0].model == "mimo-test-model"


@pytest.mark.asyncio
async def test_gateway_provider_parses_openai_compatible_json(monkeypatch):
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_DEFAULT_MODEL", "deepseek-v4-flash")
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_PROVIDER_NAME", "gateway")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://gateway.test/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer gateway-key"
        assert request.headers["content-type"] == "application/json"
        payload = request.read().decode()
        assert "deepseek-v4-flash" in payload
        assert "response_format" in payload
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "summary": "Gateway analysis",
                              "possible_causes": ["traffic spike"],
                              "suggested_actions": ["scale web tier"],
                              "risk_level": "high",
                              "confidence": 0.91,
                              "need_human_confirm": false
                            }
                            """
                        }
                    }
                ]
            },
        )

    provider = OpenAICompatibleGatewayProvider(transport=httpx.MockTransport(handler))

    result = await provider.analyze_alert("Analyze this alert")

    assert result == {
        "summary": "Gateway analysis",
        "possible_causes": ["traffic spike"],
        "suggested_actions": ["scale web tier"],
        "risk_level": "high",
        "confidence": 0.91,
        "need_human_confirm": False,
    }


@pytest.mark.asyncio
async def test_gateway_provider_parses_fenced_json(monkeypatch):
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": """
                            ```json
                            {
                              "summary": "Fenced response",
                              "possible_causes": "disk logs growing",
                              "suggested_actions": "rotate logs",
                              "risk_level": "critical",
                              "confidence": 1.5,
                              "need_human_confirm": true
                            }
                            ```
                            """
                        }
                    }
                ]
            },
        )

    result = await OpenAICompatibleGatewayProvider(transport=httpx.MockTransport(handler)).analyze_alert("Analyze")

    assert result["summary"] == "Fenced response"
    assert result["possible_causes"] == ["disk logs growing"]
    assert result["suggested_actions"] == ["rotate logs"]
    assert result["risk_level"] == "critical"
    assert result["confidence"] == 1.0
    assert result["need_human_confirm"] is True


@pytest.mark.asyncio
async def test_gateway_provider_wraps_non_json_as_summary(monkeypatch):
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Plain text analysis"}}]},
        )

    result = await OpenAICompatibleGatewayProvider(transport=httpx.MockTransport(handler)).analyze_alert("Analyze")

    assert result["summary"] == "Plain text analysis"
    assert result["possible_causes"] == []
    assert result["suggested_actions"] == []
    assert result["risk_level"] == "medium"
    assert result["confidence"] == 0.5


def test_gateway_provider_unavailable_without_key_or_base_url(monkeypatch):
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_API_KEY", "")
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")
    assert OpenAICompatibleGatewayProvider().is_available() is False

    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.llm.gateway_provider.settings.GATEWAY_BASE_URL", "")
    assert OpenAICompatibleGatewayProvider().is_available() is False


def test_model_router_uses_policy_provider_and_model_by_severity(monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")
    monkeypatch.setattr("app.services.model_router.settings.DEEPSEEK_API_KEY", "deepseek-key")
    monkeypatch.setattr("app.services.model_router.settings.MIMO_API_KEY", "mimo-key")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_LOW_PROVIDER", "gateway")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_LOW_MODEL", "deepseek-v4-flash")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_MEDIUM_PROVIDER", "deepseek")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_MEDIUM_MODEL", "deepseek-v4-flash")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_HIGH_PROVIDER", "deepseek")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_HIGH_MODEL", "deepseek-v4-pro")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "mimo")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "mimo-v2.5-pro")

    low_provider, _ = ModelRouter.get_provider(2)
    medium_provider, _ = ModelRouter.get_provider(3)
    high_provider, _ = ModelRouter.get_provider(4)
    critical_provider, _ = ModelRouter.get_provider(5)

    assert (low_provider.name, low_provider.model) == ("gateway", "deepseek-v4-flash")
    assert (medium_provider.name, medium_provider.model) == ("deepseek", "deepseek-v4-flash")
    assert (high_provider.name, high_provider.model) == ("deepseek", "deepseek-v4-pro")
    assert (critical_provider.name, critical_provider.model) == ("mimo", "mimo-v2.5-pro")


def test_model_router_should_analyze_honors_global_switch(monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.AI_ANALYSIS_ENABLED", False)

    should_analyze, reason = ModelRouter.should_analyze(5)

    assert should_analyze is False
    assert reason == "AI analysis globally disabled"


def test_model_router_should_analyze_honors_severity_switches(monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.AI_ANALYSIS_ENABLED", True)
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_LOW_ENABLED", False)
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_MEDIUM_ENABLED", False)
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_HIGH_ENABLED", True)
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_ENABLED", True)

    assert ModelRouter.should_analyze(2) == (False, "AI disabled for low severity")
    assert ModelRouter.should_analyze(3) == (False, "AI disabled for medium severity")
    assert ModelRouter.should_analyze(4) == (True, "")
    assert ModelRouter.should_analyze(5) == (True, "")


def test_model_router_prefers_manual_provider_and_model(monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "mimo")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "mimo-v2.5-pro")

    provider, fallback_reason = ModelRouter.get_provider(
        5,
        preferred_provider="gateway",
        preferred_model="manual-gateway-model",
    )

    assert fallback_reason == ""
    assert provider.name == "gateway"
    assert provider.model == "manual-gateway-model"


@pytest.mark.asyncio
async def test_deepseek_provider_model_argument_overrides_settings(monkeypatch):
    monkeypatch.setattr("app.llm.deepseek_provider.settings.DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.deepseek_provider.settings.DEEPSEEK_BASE_URL", "https://deepseek.test/v1")
    monkeypatch.setattr("app.llm.deepseek_provider.settings.DEEPSEEK_MODEL", "deepseek-default")

    def handler(request: httpx.Request) -> httpx.Response:
        payload = request.read().decode()
        assert "deepseek-v4-pro" in payload
        assert "deepseek-default" not in payload
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    provider = DeepSeekProvider(model="deepseek-v4-pro", transport=httpx.MockTransport(handler))

    assert provider.model == "deepseek-v4-pro"
    assert await provider.chat([{"role": "user", "content": "hello"}]) == "{}"


@pytest.mark.asyncio
async def test_mimo_provider_model_argument_overrides_settings(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_BASE_URL", "https://mimo.test/v1")
    monkeypatch.setattr("app.llm.mimo_provider.settings.MIMO_MODEL", "mimo-default")

    def handler(request: httpx.Request) -> httpx.Response:
        payload = request.read().decode()
        assert "mimo-v2.5-pro" in payload
        assert "mimo-default" not in payload
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    provider = MimoProvider(model="mimo-v2.5-pro", transport=httpx.MockTransport(handler))

    assert provider.model == "mimo-v2.5-pro"
    assert await provider.chat([{"role": "user", "content": "hello"}]) == "{}"


@pytest.mark.asyncio
async def test_gateway_failure_falls_back_to_mock_and_records_real_model(db_session, monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "gateway")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "gateway-deepseek-v4-flash")

    async def fail_gateway(_self, _prompt):
        raise RuntimeError("gateway timeout")

    monkeypatch.setattr(OpenAICompatibleGatewayProvider, "analyze_alert", fail_gateway)
    alert = Alert(
        source="zabbix",
        event_id="evt-gateway",
        trigger_id="trg-gateway",
        trigger_name="Memory usage over 95%",
        host_id="host-gateway",
        host_name="app-01",
        host_ip="10.0.0.3",
        severity=5,
        severity_label="disaster",
        item_key="vm.memory.size[pused]",
        item_value="98",
        message="Memory usage over 95%",
        tags={},
        raw_payload={},
        is_recovery=False,
        dedup_key="zabbix:host-gateway:trg-gateway:vm.memory.size[pused]",
        dedup_count=1,
        storm_detected=False,
    )
    db_session.add(alert)
    await db_session.flush()

    result = await AIOrchestrator(db_session).analyze_alert(alert.id)

    usage = (await db_session.execute(select(LLMUsage).order_by(LLMUsage.id))).scalars().all()
    assert result["success"] is True
    assert result["data"]["model_used"] == "mock"
    assert "gateway" in result["data"]["fallback_reason"].lower()
    assert [(row.provider, row.model, row.success) for row in usage] == [
        ("gateway", "gateway-deepseek-v4-flash", False),
        ("mock", "mock", True),
    ]


@pytest.mark.asyncio
async def test_orchestrator_manual_provider_model_overrides_policy(db_session, monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_API_KEY", "gateway-key")
    monkeypatch.setattr("app.services.model_router.settings.GATEWAY_BASE_URL", "https://gateway.test/v1")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_HIGH_PROVIDER", "mock")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_HIGH_MODEL", "mock")

    async def gateway_success(_self, _prompt):
        return {
            "summary": "Manual gateway analysis",
            "possible_causes": ["manual model selected"],
            "suggested_actions": ["keep monitoring"],
            "risk_level": "high",
            "confidence": 0.88,
            "need_human_confirm": False,
        }

    monkeypatch.setattr(OpenAICompatibleGatewayProvider, "analyze_alert", gateway_success)
    alert = Alert(
        source="zabbix",
        event_id="evt-manual",
        trigger_id="trg-manual",
        trigger_name="Interface down",
        host_id="host-manual",
        host_name="switch-01",
        host_ip="10.0.0.4",
        severity=4,
        severity_label="high",
        item_key="net.if.status[eth0]",
        item_value="down",
        message="Interface down",
        tags={},
        raw_payload={},
        is_recovery=False,
        dedup_key="zabbix:host-manual:trg-manual:net.if.status[eth0]",
        dedup_count=1,
        storm_detected=False,
    )
    db_session.add(alert)
    await db_session.flush()

    result = await AIOrchestrator(db_session).analyze_alert(
        alert.id,
        preferred_provider="gateway",
        preferred_model="manual-deepseek-v4-flash",
    )

    usage = (await db_session.execute(select(LLMUsage).order_by(LLMUsage.id))).scalars().all()
    assert result["success"] is True
    assert result["data"]["summary"] == "Manual gateway analysis"
    assert usage[0].provider == "gateway"
    assert usage[0].model == "manual-deepseek-v4-flash"
