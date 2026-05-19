from pathlib import Path


def test_initial_migration_creates_required_tables_with_postgres_types():
    migration_path = Path(__file__).resolve().parents[2] / "alembic" / "versions" / "0001_initial.py"
    migration = migration_path.read_text()

    assert 'revision: str = "0001"' in migration
    assert "down_revision: Union[str, None] = None" in migration
    assert "def upgrade() -> None:" in migration
    assert "def downgrade() -> None:" in migration
    for table_name in [
        "alerts",
        "ai_analyses",
        "llm_usage",
        "knowledge_documents",
        "remediation_plans",
    ]:
        assert f'"{table_name}"' in migration

    assert "postgresql.JSONB" in migration
    assert migration.count("sa.DateTime(timezone=True)") >= 10
    assert "ix_llm_usage_created_at" in migration
