from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def analyze_alert(self, prompt: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...

    def is_available(self) -> bool:
        return True
