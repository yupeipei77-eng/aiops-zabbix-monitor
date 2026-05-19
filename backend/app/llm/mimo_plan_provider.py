import json
import re
from typing import Any

import httpx

from app.llm.base import BaseLLMProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MimoPlanProvider(BaseLLMProvider):
    def __init__(
        self,
        model: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 30.0,
    ):
        self._model = model or settings.MIMO_PLAN_MODEL
        self._transport = transport
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "mimo_plan"

    @property
    def model(self) -> str:
        return self._model

    def is_available(self) -> bool:
        return bool(settings.MIMO_PLAN_API_KEY) and bool(settings.MIMO_PLAN_BASE_URL)

    async def analyze_alert(self, prompt: str) -> dict:
        if not self.is_available():
            raise RuntimeError("Mimo Plan API key or base URL not configured")
        content = await self._call_plan_api(prompt)
        return self._parse_plan_response(content)

    async def chat(self, messages: list[dict]) -> str:
        if not self.is_available():
            raise RuntimeError("Mimo Plan API key or base URL not configured")
        user_prompt = messages[-1].get("content", "") if messages else ""
        return await self._call_plan_api(user_prompt)

    async def health_check(self) -> bool:
        return self.is_available()

    async def _call_plan_api(self, prompt: str) -> dict:
        base_url = settings.MIMO_PLAN_BASE_URL.rstrip("/")
        endpoint = settings.MIMO_PLAN_ENDPOINT
        url = f"{base_url}{endpoint}"

        async with httpx.AsyncClient(
            timeout=self._timeout,
            transport=self._transport,
        ) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {settings.MIMO_PLAN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_steps": 6,
                    "context": {},
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业 SRE 排障计划助手，请生成可执行的排障计划。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
            )
            response.raise_for_status()
            return response.json()

    def _parse_plan_response(self, payload: dict) -> dict[str, Any]:
        content = self._extract_content(payload)
        if not content:
            raise RuntimeError("Mimo Plan response has no usable content")

        if isinstance(content, list):
            return {
                "summary": "排障计划已生成",
                "possible_causes": [],
                "suggested_actions": [str(step) for step in content],
                "risk_level": "medium",
                "confidence": 0.7,
                "need_human_confirm": True,
            }

        if isinstance(content, str):
            return self._parse_text_content(content)

        raise RuntimeError("Mimo Plan response has no usable content")

    def _extract_content(self, payload: dict) -> str | list | None:
        if choices := payload.get("choices"):
            if isinstance(choices, list) and choices:
                try:
                    return choices[0]["message"]["content"]
                except (KeyError, IndexError, TypeError):
                    pass

        if plan := payload.get("plan"):
            return plan

        if result := payload.get("result"):
            return result

        if output := payload.get("output"):
            return output

        if steps := payload.get("steps"):
            return steps

        if data := payload.get("data"):
            if isinstance(data, dict):
                if plan := data.get("plan"):
                    return plan
                if result := data.get("result"):
                    return result
                if steps := data.get("steps"):
                    return steps

        return None

    def _parse_text_content(self, text: str) -> dict[str, Any]:
        raw = text.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)```", raw, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            raw = fenced.group(1).strip()

        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return self._parse_structured_json(data)
        except json.JSONDecodeError:
            pass

        actions = self._split_actions(raw)
        summary = raw[:120] + "..." if len(raw) > 120 else raw
        if not summary:
            summary = "排障计划已生成"

        return {
            "summary": summary,
            "possible_causes": [],
            "suggested_actions": actions,
            "risk_level": "medium",
            "confidence": 0.7,
            "need_human_confirm": True,
        }

    def _parse_structured_json(self, data: dict) -> dict[str, Any]:
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
            confidence = float(data.get("confidence", 0.7))
        except (TypeError, ValueError):
            confidence = 0.7
        confidence = min(max(confidence, 0.0), 1.0)

        return {
            "summary": str(data.get("summary") or "排障计划已生成"),
            "possible_causes": [str(item) for item in causes],
            "suggested_actions": [str(item) for item in actions],
            "risk_level": risk_level,
            "confidence": confidence,
            "need_human_confirm": bool(data.get("need_human_confirm", True)),
        }

    def _split_actions(self, text: str) -> list[str]:
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if line and not line.isspace():
                cleaned = re.sub(r"^[\d]+[\.\、\)]\s*", "", line)
                cleaned = re.sub(r"^[-*•]\s*", "", cleaned)
                if cleaned:
                    lines.append(cleaned)
        return lines if lines else [text.strip()]
