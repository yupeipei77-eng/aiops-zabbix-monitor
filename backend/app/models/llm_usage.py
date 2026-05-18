from sqlalchemy import String, Integer, Boolean, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class LLMUsage(Base, TimestampMixin):
    __tablename__ = "llm_usage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    context: Mapped[str] = mapped_column(String(100), default="alert_analysis")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str] = mapped_column(Text, default="")
    cached: Mapped[bool] = mapped_column(Boolean, default=False)
