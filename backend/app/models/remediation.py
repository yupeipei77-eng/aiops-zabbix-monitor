from sqlalchemy import String, Integer, Boolean, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class RemediationPlan(Base, TimestampMixin):
    __tablename__ = "remediation_plans"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(BigInteger, index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    steps: Mapped[str] = mapped_column(Text, default="[]")
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
