from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.deepseek_provider import DeepSeekProvider
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
    "kimi": KimiProvider,
    "mimo": MimoProvider,
}


class ModelRouter:
    @staticmethod
    def get_provider(severity: int, preferred: str | None = None) -> tuple[BaseLLMProvider, str]:
        if preferred and preferred in PROVIDER_REGISTRY:
            provider = PROVIDER_REGISTRY[preferred]()
            if provider.is_available():
                return provider, ""
            fallback_reason = f"preferred provider '{preferred}' not available"
            logger.warning(fallback_reason + ", falling back to mock")
            return MockLLMProvider(), fallback_reason

        provider_name = settings.ADVANCED_LLM_PROVIDER if severity >= 4 else settings.DEFAULT_LLM_PROVIDER
        provider_cls = PROVIDER_REGISTRY.get(provider_name, MockLLMProvider)
        provider = provider_cls()

        if provider.is_available():
            return provider, ""

        fallback_reason = f"provider '{provider_name}' not available"
        logger.warning(fallback_reason + ", falling back to mock")
        return MockLLMProvider(), fallback_reason
