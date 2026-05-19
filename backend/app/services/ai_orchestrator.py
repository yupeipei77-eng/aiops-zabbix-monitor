import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.llm.mock_provider import MockLLMProvider
from app.services.model_router import ModelRouter
from app.services.prompt_builder import PromptBuilder
from app.repositories.alert_repo import AlertRepo
from app.repositories.ai_analysis_repo import AIAnalysisRepo
from app.repositories.usage_repo import UsageRepo
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alert_repo = AlertRepo(db)
        self.analysis_repo = AIAnalysisRepo(db)
        self.usage_repo = UsageRepo(db)

    async def analyze_alert(self, alert_id: int, preferred_provider: str | None = None) -> dict:
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            return {"success": False, "data": None, "message": "Alert not found"}

        alert_data = {
            "trigger_name": alert.trigger_name,
            "host_name": alert.host_name,
            "host_ip": alert.host_ip,
            "severity": alert.severity,
            "severity_label": alert.severity_label,
            "item_key": alert.item_key,
            "item_value": alert.item_value,
        }

        prompt = PromptBuilder.build_alert_analysis_prompt(alert_data)

        provider, fallback_reason = ModelRouter.get_provider(alert.severity, preferred_provider)

        return await self._analyze_with_provider(provider, alert_id, prompt, fallback_reason)

    async def _analyze_with_provider(self, provider, alert_id: int, prompt: str, fallback_reason: str) -> dict:
        model_name = getattr(provider, "model", provider.name)
        start = time.time()
        try:
            result = await provider.analyze_alert(prompt)
            latency_ms = int((time.time() - start) * 1000)

            analysis = await self.analysis_repo.create(
                alert_id=alert_id,
                summary=result["summary"],
                possible_causes=result["possible_causes"],
                suggested_actions=result["suggested_actions"],
                risk_level=result["risk_level"],
                confidence=result["confidence"],
                need_human_confirm=result["need_human_confirm"],
                model_used=provider.name,
                prompt=prompt,
                raw_response=result,
                latency_ms=latency_ms,
            )

            await self.usage_repo.create(
                provider=provider.name,
                model=model_name,
                context="alert_analysis",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=latency_ms,
                success=True,
                cached=False,
            )

            return {
                "success": True,
                "data": {
                    "id": analysis.id,
                    "alert_id": alert_id,
                    "summary": result["summary"],
                    "possible_causes": result["possible_causes"],
                    "suggested_actions": result["suggested_actions"],
                    "risk_level": result["risk_level"],
                    "confidence": result["confidence"],
                    "need_human_confirm": result["need_human_confirm"],
                    "model_used": provider.name,
                    "fallback_reason": fallback_reason,
                },
                "message": "",
            }
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            logger.error("AI analysis failed: %s", str(e))
            await self.usage_repo.create(
                provider=provider.name,
                model=model_name,
                context="alert_analysis",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
            )
            if provider.name != "mock":
                mock_fallback_reason = f"{fallback_reason}; provider '{provider.name}' failed: {e}".strip("; ")
                return await self._analyze_with_provider(MockLLMProvider(), alert_id, prompt, mock_fallback_reason)
            return {"success": False, "data": None, "message": str(e)}
