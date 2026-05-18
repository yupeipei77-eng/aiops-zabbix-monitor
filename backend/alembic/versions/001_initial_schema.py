"""initial schema

Revision ID: 001
Revises: None
Create Date: 2025-01-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(50), server_default="zabbix"),
        sa.Column("event_id", sa.String(100), nullable=False),
        sa.Column("trigger_id", sa.String(100), nullable=False),
        sa.Column("trigger_name", sa.String(500), nullable=False),
        sa.Column("host_id", sa.String(100), nullable=False),
        sa.Column("host_name", sa.String(200), nullable=False),
        sa.Column("host_ip", sa.String(50), nullable=False),
        sa.Column("severity", sa.Integer(), server_default="0"),
        sa.Column("severity_label", sa.String(20), nullable=False),
        sa.Column("item_key", sa.String(200), nullable=False),
        sa.Column("item_value", sa.String(500), nullable=False),
        sa.Column("message", sa.Text(), server_default=""),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb")),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_recovery", sa.Boolean(), server_default="false"),
        sa.Column("dedup_key", sa.String(200), server_default=""),
        sa.Column("dedup_count", sa.Integer(), server_default="1"),
        sa.Column("storm_detected", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_event_id", "alerts", ["event_id"])
    op.create_index("ix_alerts_trigger_id", "alerts", ["trigger_id"])
    op.create_index("ix_alerts_host_id", "alerts", ["host_id"])
    op.create_index("ix_alerts_dedup_key", "alerts", ["dedup_key"])

    op.create_table(
        "ai_analyses",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.BigInteger(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("possible_causes", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
        sa.Column("suggested_actions", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="0"),
        sa.Column("need_human_confirm", sa.Boolean(), server_default="false"),
        sa.Column("model_used", sa.String(50), nullable=False),
        sa.Column("prompt", sa.Text(), server_default=""),
        sa.Column("raw_response", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb")),
        sa.Column("latency_ms", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_analyses_alert_id", "ai_analyses", ["alert_id"])

    op.create_table(
        "llm_usage",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("context", sa.String(100), server_default="alert_analysis"),
        sa.Column("prompt_tokens", sa.Integer(), server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), server_default="0"),
        sa.Column("total_tokens", sa.Integer(), server_default="0"),
        sa.Column("latency_ms", sa.Integer(), server_default="0"),
        sa.Column("success", sa.Boolean(), server_default="true"),
        sa.Column("error_message", sa.Text(), server_default=""),
        sa.Column("cached", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source", sa.String(200), server_default="manual"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "remediation_plans",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("risk_level", sa.String(20), server_default="low"),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")),
        sa.Column("dry_run", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_remediation_plans_alert_id", "remediation_plans", ["alert_id"])


def downgrade() -> None:
    op.drop_table("remediation_plans")
    op.drop_table("knowledge_documents")
    op.drop_table("llm_usage")
    op.drop_table("ai_analyses")
    op.drop_table("alerts")
