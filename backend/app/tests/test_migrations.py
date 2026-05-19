from pathlib import Path


def test_initial_migration_creates_required_tables_with_postgres_types():
    migration = (
        Path(__file__).resolve().parents[2] / "alembic" / "versions" / "001_initial_schema.py"
    ).read_text()

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
