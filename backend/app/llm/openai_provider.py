from app.llm.base import BaseLLMProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    @property
    def name(self) -> str:
        return "openai"

    def is_available(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    async def analyze_alert(self, prompt: str) -> dict:
        if not self.is_available():
            raise RuntimeError("OpenAI API key not configured")
        raise NotImplementedError("OpenAI provider not implemented yet - use mock for v1")

    async def chat(self, messages: list[dict]) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI API key not configured")
        raise NotImplementedError("OpenAI provider not implemented yet - use mock for v1")

    async def health_check(self) -> bool:
        return self.is_available()
