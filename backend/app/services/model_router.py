from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.deepseek_provider import DeepSeekProvider
from app.llm.gateway_provider import OpenAICompatibleGatewayProvider
from app.llm.kimi_provider import KimiProvider
from app.llm.mimo_provider import MimoProvider
from app.core.config import settings
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider

logger = get_logger(__name__)

PROVIDER_REGISTRY: dict[str, type[BaseLLMProvider]] = {
    "mock": MockLLMProvider,
    "openai": OpenAIProvider,
    "deepseek": DeepSeekProvider,
    "gateway": OpenAICompatibleGatewayProvider,
    "kimi": KimiProvider,
    "mimo": MimoProvider,
}


class ModelRouter:
    @staticmethod
    def should_analyze(severity: int) -> tuple[bool, str]:
        if not settings.AI_ANALYSIS_ENABLED:
            return False, "AI analysis globally disabled"

        if severity >= 5:
            enabled = settings.LLM_POLICY_CRITICAL_ENABLED
            level = "critical"
        elif severity == 4:
            enabled = settings.LLM_POLICY_HIGH_ENABLED
            level = "high"
        elif severity == 3:
            enabled = settings.LLM_POLICY_MEDIUM_ENABLED
            level = "medium"
        else:
            enabled = settings.LLM_POLICY_LOW_ENABLED
            level = "low"

        if not enabled:
            return False, f"AI disabled for {level} severity"
        return True, ""

    @staticmethod
    def get_provider(
        severity: int,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
    ) -> tuple[BaseLLMProvider, str]:
        if preferred_provider:
            return ModelRouter._build_or_mock(preferred_provider, preferred_model, preferred=True)

        provider_name, model_name = ModelRouter._policy_for_severity(severity)
        if preferred_model:
            model_name = preferred_model
        return ModelRouter._build_or_mock(provider_name, model_name, preferred=False)

    @staticmethod
    def _policy_for_severity(severity: int) -> tuple[str, str | None]:
        if severity >= 5:
            provider_name = settings.LLM_POLICY_CRITICAL_PROVIDER
            model_name = settings.LLM_POLICY_CRITICAL_MODEL
        elif severity == 4:
            provider_name = settings.LLM_POLICY_HIGH_PROVIDER
            model_name = settings.LLM_POLICY_HIGH_MODEL
        elif severity == 3:
            provider_name = settings.LLM_POLICY_MEDIUM_PROVIDER
            model_name = settings.LLM_POLICY_MEDIUM_MODEL
        else:
            provider_name = settings.LLM_POLICY_LOW_PROVIDER
            model_name = settings.LLM_POLICY_LOW_MODEL

        if provider_name == "mock" and model_name == "mock":
            legacy_provider = settings.ADVANCED_LLM_PROVIDER if severity >= 4 else settings.DEFAULT_LLM_PROVIDER
            if legacy_provider != "mock":
                return legacy_provider, None
        return provider_name, model_name

    @staticmethod
    def _build_or_mock(
        provider_name: str,
        model_name: str | None,
        preferred: bool,
    ) -> tuple[BaseLLMProvider, str]:
        label = "preferred provider" if preferred else "provider"
        provider_cls = PROVIDER_REGISTRY.get(provider_name)
        if provider_cls is None:
            fallback_reason = f"{label} '{provider_name}' is not registered"
            logger.warning(fallback_reason + ", falling back to mock")
            return MockLLMProvider(), fallback_reason

        provider = provider_cls(model=model_name) if model_name else provider_cls()

        if provider.is_available():
            return provider, ""

        fallback_reason = f"{label} '{provider_name}' not available"
        logger.warning(fallback_reason + ", falling back to mock")
        return MockLLMProvider(), fallback_reason
