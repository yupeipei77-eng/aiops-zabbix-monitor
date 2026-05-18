from typing import Any

from sqlalchemy import String, Integer, Float, Text, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin
from app.models.types import BIGINT_PK, JSON_FIELD


class AIAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(BigInteger, index=True)
    summary: Mapped[str] = mapped_column(Text)
    possible_causes: Mapped[list[str]] = mapped_column(JSON_FIELD, default=list)
    suggested_actions: Mapped[list[str]] = mapped_column(JSON_FIELD, default=list)
    risk_level: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    need_human_confirm: Mapped[bool] = mapped_column(Boolean, default=False)
    model_used: Mapped[str] = mapped_column(String(50))
    prompt: Mapped[str] = mapped_column(Text, default="")
    raw_response: Mapped[dict[str, Any]] = mapped_column(JSON_FIELD, default=dict)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
