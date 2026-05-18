from typing import Any

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin
from app.models.types import BIGINT_PK, JSON_FIELD


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), default="zabbix")
    event_id: Mapped[str] = mapped_column(String(100), index=True)
    trigger_id: Mapped[str] = mapped_column(String(100), index=True)
    trigger_name: Mapped[str] = mapped_column(String(500))
    host_id: Mapped[str] = mapped_column(String(100), index=True)
    host_name: Mapped[str] = mapped_column(String(200))
    host_ip: Mapped[str] = mapped_column(String(50))
    severity: Mapped[int] = mapped_column(Integer, default=0)
    severity_label: Mapped[str] = mapped_column(String(20))
    item_key: Mapped[str] = mapped_column(String(200))
    item_value: Mapped[str] = mapped_column(String(500))
    message: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[dict[str, Any]] = mapped_column(JSON_FIELD, default=dict)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON_FIELD, default=dict)
    is_recovery: Mapped[bool] = mapped_column(Boolean, default=False)
    dedup_key: Mapped[str] = mapped_column(String(200), index=True, default="")
    dedup_count: Mapped[int] = mapped_column(Integer, default=1)
    storm_detected: Mapped[bool] = mapped_column(Boolean, default=False)
