import json
import re
from typing import Any

import httpx

from app.llm.base import BaseLLMProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DeepSeekProvider(BaseLLMProvider):
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None, timeout: float = 30.0):
        self._transport = transport
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "deepseek"

    @property
    def model(self) -> str:
        return settings.DEEPSEEK_MODEL

    def is_available(self) -> bool:
        return bool(settings.DEEPSEEK_API_KEY)

    async def analyze_alert(self, prompt: str) -> dict:
        if not self.is_available():
            raise RuntimeError("DeepSeek API key not configured")
        content = await self.chat([
            {
                "role": "system",
                "content": (
                    "你是一个专业 SRE 告警分析助手。请只返回 JSON，不要返回 Markdown。"
                    "JSON 字段必须包含 summary, possible_causes, suggested_actions, "
                    "risk_level, confidence, need_human_confirm。"
                ),
            },
            {"role": "user", "content": prompt},
        ])
        return self._parse_analysis(content)

    async def chat(self, messages: list[dict]) -> str:
        if not self.is_available():
            raise RuntimeError("DeepSeek API key not configured")
        base_url = (settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com").rstrip("/")
        async with httpx.AsyncClient(
            base_url=base_url,
            timeout=self._timeout,
            transport=self._transport,
        ) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": messages,
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            payload = response.json()
        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("DeepSeek response missing choices[0].message.content") from exc

    async def health_check(self) -> bool:
        return self.is_available()

    def _parse_analysis(self, content: str) -> dict[str, Any]:
        raw = content.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)```", raw, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            raw = fenced.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("DeepSeek returned non-JSON content; wrapping as summary")
            data = {"summary": raw}

        causes = data.get("possible_causes") or []
        actions = data.get("suggested_actions") or []
        if isinstance(causes, str):
            causes = [causes]
        if isinstance(actions, str):
            actions = [actions]

        risk_level = str(data.get("risk_level") or "medium").lower()
        if risk_level not in {"low", "medium", "high", "critical"}:
            risk_level = "medium"

        try:
            confidence = float(data.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = min(max(confidence, 0.0), 1.0)

        return {
            "summary": str(data.get("summary") or "DeepSeek completed analysis but did not provide a summary."),
            "possible_causes": [str(item) for item in causes],
            "suggested_actions": [str(item) for item in actions],
            "risk_level": risk_level,
            "confidence": confidence,
            "need_human_confirm": bool(data.get("need_human_confirm", False)),
        }
