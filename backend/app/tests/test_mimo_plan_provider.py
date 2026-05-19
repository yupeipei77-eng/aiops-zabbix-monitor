import pytest
import httpx
from sqlalchemy import select

from app.llm.mimo_plan_provider import MimoPlanProvider
from app.models.ai_analysis import AIAnalysis
from app.models.alert import Alert
from app.models.llm_usage import LLMUsage
from app.services.ai_orchestrator import AIOrchestrator
from app.services.model_router import ModelRouter


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_plan_field(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_MODEL", "mimo-plan-test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://plan.test/plan"
        assert request.headers["authorization"] == "Bearer test-key"
        return httpx.Response(200, json={"plan": "检查主机状态\n查看接口流量\n确认链路状态"})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert result["summary"] == "检查主机状态\n查看接口流量\n确认链路状态"
    assert result["suggested_actions"] == ["检查主机状态", "查看接口流量", "确认链路状态"]
    assert result["possible_causes"] == []
    assert result["risk_level"] == "medium"
    assert result["confidence"] == 0.7
    assert result["need_human_confirm"] is True


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_result_field(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": "1. 检查 CPU 使用率\n2. 查看内存状态\n3. 确认磁盘空间"})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert "检查" in result["summary"]
    assert "检查 CPU 使用率" in result["suggested_actions"]
    assert "查看内存状态" in result["suggested_actions"]


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_output_field(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"output": "排查步骤：检查配置，重启服务"})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert "排查" in result["summary"]
    assert result["suggested_actions"] == ["排查步骤：检查配置，重启服务"]


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_steps_array(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"steps": ["检查主机状态", "查看接口流量", "确认是否存在链路抖动"]})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert result["suggested_actions"] == ["检查主机状态", "查看接口流量", "确认是否存在链路抖动"]
    assert result["summary"] == "排障计划已生成"


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_data_plan(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": {"plan": "第一步：登录服务器\n第二步：检查日志"}})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert "登录服务器" in result["summary"]
    assert "第一步：登录服务器" in result["suggested_actions"]
    assert "第二步：检查日志" in result["suggested_actions"]


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_data_result(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": {"result": "分析结果：需要扩容"}})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert "分析结果" in result["summary"]


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_data_steps(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": {"steps": ["步骤1", "步骤2", "步骤3"]}})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert result["suggested_actions"] == ["步骤1", "步骤2", "步骤3"]


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_openai_compatible(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"summary": "Plan analysis", "suggested_actions": ["step1", "step2"]}'
                        }
                    }
                ]
            }
        )

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert result["summary"] == "Plan analysis"
    assert result["suggested_actions"] == ["step1", "step2"]


def test_mimo_plan_provider_unavailable_without_key_or_base_url(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    assert MimoPlanProvider().is_available() is False

    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "")
    assert MimoPlanProvider().is_available() is False


@pytest.mark.asyncio
async def test_mimo_plan_provider_raises_when_no_content(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))

    with pytest.raises(RuntimeError, match="Mimo Plan response has no usable content"):
        await provider.analyze_alert("测试告警")


@pytest.mark.asyncio
async def test_orchestrator_falls_back_to_mock_when_mimo_plan_fails(db_session, monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "mimo_plan")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "mimo-plan-pro")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_MODEL", "mimo-plan-test")

    async def fail_mimo_plan(_self, _prompt):
        raise RuntimeError("mimo plan timeout")

    monkeypatch.setattr(MimoPlanProvider, "analyze_alert", fail_mimo_plan)
    alert = Alert(
        source="zabbix",
        event_id="evt-mimo-plan",
        trigger_id="trg-mimo-plan",
        trigger_name="Network latency high",
        host_id="host-mimo-plan",
        host_name="network-01",
        host_ip="10.0.0.5",
        severity=5,
        severity_label="disaster",
        item_key="net.if.status[eth0]",
        item_value="high-latency",
        message="Network latency high",
        tags={},
        raw_payload={},
        is_recovery=False,
        dedup_key="zabbix:host-mimo-plan:trg-mimo-plan:net.if.status[eth0]",
        dedup_count=1,
        storm_detected=False,
    )
    db_session.add(alert)
    await db_session.flush()

    result = await AIOrchestrator(db_session).analyze_alert(alert.id)

    assert result["success"] is True
    assert result["data"]["model_used"] == "mock"
    assert "mimo_plan" in result["data"]["fallback_reason"].lower()

    analyses = (await db_session.execute(select(AIAnalysis))).scalars().all()
    usage = (await db_session.execute(select(LLMUsage).order_by(LLMUsage.id))).scalars().all()
    assert len(analyses) == 1
    assert analyses[0].model_used == "mock"
    assert [(row.provider, row.success) for row in usage] == [("mimo_plan", False), ("mock", True)]
    assert usage[0].model == "mimo-plan-pro"


@pytest.mark.asyncio
async def test_mimo_plan_provider_llm_usage_records_real_model(db_session, monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "mimo_plan")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "mimo-plan-real-model")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_MODEL", "mimo-plan-real-model")

    async def success_mimo_plan(_self, _prompt):
        return {
            "summary": "Plan success",
            "possible_causes": [],
            "suggested_actions": ["action1"],
            "risk_level": "medium",
            "confidence": 0.7,
            "need_human_confirm": True,
        }

    monkeypatch.setattr(MimoPlanProvider, "analyze_alert", success_mimo_plan)
    alert = Alert(
        source="zabbix",
        event_id="evt-mimo-plan-usage",
        trigger_id="trg-mimo-plan-usage",
        trigger_name="Service degraded",
        host_id="host-mimo-plan-usage",
        host_name="svc-01",
        host_ip="10.0.0.6",
        severity=5,
        severity_label="disaster",
        item_key="svc.status",
        item_value="degraded",
        message="Service degraded",
        tags={},
        raw_payload={},
        is_recovery=False,
        dedup_key="zabbix:host-mimo-plan-usage:trg-mimo-plan-usage:svc.status",
        dedup_count=1,
        storm_detected=False,
    )
    db_session.add(alert)
    await db_session.flush()

    result = await AIOrchestrator(db_session).analyze_alert(alert.id)

    usage = (await db_session.execute(select(LLMUsage).order_by(LLMUsage.id))).scalars().all()
    assert len(usage) == 1
    assert usage[0].provider == "mimo_plan"
    assert usage[0].model == "mimo-plan-real-model"
    assert usage[0].success is True
    assert result["success"] is True
    assert result["data"]["model_used"] == "mimo_plan"


@pytest.mark.asyncio
async def test_mimo_plan_provider_model_argument_overrides_settings(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_MODEL", "mimo-plan-default")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(request: httpx.Request) -> httpx.Response:
        payload = request.read().decode()
        assert "mimo-plan-custom" in payload
        assert "mimo-plan-default" not in payload
        return httpx.Response(200, json={"plan": "step1"})

    provider = MimoPlanProvider(model="mimo-plan-custom", transport=httpx.MockTransport(handler))

    assert provider.model == "mimo-plan-custom"
    result = await provider.analyze_alert("test")
    assert "step1" in result["suggested_actions"]


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_numbered_steps(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": "1. 检查配置\n2. 重启服务\n3. 验证恢复"})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert "检查配置" in result["suggested_actions"]
    assert "重启服务" in result["suggested_actions"]
    assert "验证恢复" in result["suggested_actions"]


@pytest.mark.asyncio
async def test_mimo_plan_provider_parses_json_plan_field(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "plan": '{"summary": "Structured plan", "suggested_actions": ["check logs", "restart service"]}'
            }
        )

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.analyze_alert("测试告警")

    assert result["summary"] == "Structured plan"
    assert result["suggested_actions"] == ["check logs", "restart service"]


def test_model_router_can_get_mimo_plan_provider(monkeypatch):
    monkeypatch.setattr("app.services.model_router.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.services.model_router.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_PROVIDER", "mimo_plan")
    monkeypatch.setattr("app.services.model_router.settings.LLM_POLICY_CRITICAL_MODEL", "mimo-plan-pro")

    provider, fallback_reason = ModelRouter.get_provider(5)

    assert fallback_reason == ""
    assert provider.name == "mimo_plan"
    assert provider.model == "mimo-plan-pro"


@pytest.mark.asyncio
async def test_mimo_plan_provider_chat_parses_steps_array(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"steps": ["检查主机状态", "查看接口流量", "确认链路状态"]})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.chat([{"role": "user", "content": "测试告警"}])

    assert result == "检查主机状态\n查看接口流量\n确认链路状态"


@pytest.mark.asyncio
async def test_mimo_plan_provider_chat_parses_plan_field(monkeypatch):
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_API_KEY", "test-key")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_BASE_URL", "https://plan.test")
    monkeypatch.setattr("app.llm.mimo_plan_provider.settings.MIMO_PLAN_ENDPOINT", "/plan")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"plan": "第一步：检查配置\n第二步：重启服务"})

    provider = MimoPlanProvider(transport=httpx.MockTransport(handler))
    result = await provider.chat([{"role": "user", "content": "测试告警"}])

    assert result == "第一步：检查配置\n第二步：重启服务"
