import pytest
from app.llm.mock_provider import MockLLMProvider


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
