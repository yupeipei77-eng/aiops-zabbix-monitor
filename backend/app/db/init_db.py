from app.db.session import async_session_factory
from app.models.base import Base
from app.models.alert import Alert  # noqa: F401
from app.models.ai_analysis import AIAnalysis  # noqa: F401
from app.models.llm_usage import LLMUsage  # noqa: F401
from app.models.knowledge import KnowledgeDocument  # noqa: F401
from app.models.remediation import RemediationPlan  # noqa: F401
from app.db.session import engine


async def init_db() -> None:
    """Development fallback only; production setup must use Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_mock_data() -> None:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    async with async_session_factory() as session:
        from sqlalchemy import select
        from app.models.alert import Alert
        result = await session.execute(select(Alert).limit(1))
        if result.scalars().first():
            logger.info("Data already exists, skip seeding")
            return

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        alerts_data = [
            {
                "source": "zabbix",
                "event_id": "evt-001",
                "trigger_id": "trg-001",
                "trigger_name": "CPU usage over 90% on {HOST.NAME}",
                "host_id": "host-001",
                "host_name": "web-server-01",
                "host_ip": "192.168.1.10",
                "severity": 4,
                "severity_label": "high",
                "item_key": "system.cpu.util",
                "item_value": "95.2",
                "message": "CPU utilization is 95.2%",
                "tags": {"scope": "production", "team": "infra"},
                "raw_payload": {"event_id": "evt-001"},
                "is_recovery": False,
                "dedup_key": "zabbix:host-001:trg-001:system.cpu.util",
                "dedup_count": 1,
                "storm_detected": False,
                "created_at": now,
                "updated_at": now,
            },
            {
                "source": "zabbix",
                "event_id": "evt-002",
                "trigger_id": "trg-002",
                "trigger_name": "Disk space low on {HOST.NAME}",
                "host_id": "host-002",
                "host_name": "db-server-01",
                "host_ip": "192.168.1.20",
                "severity": 3,
                "severity_label": "warning",
                "item_key": "vfs.fs.size[/,pfree]",
                "item_value": "5.1",
                "message": "Free disk space is 5.1%",
                "tags": {"scope": "production", "team": "dba"},
                "raw_payload": {"event_id": "evt-002"},
                "is_recovery": False,
                "dedup_key": "zabbix:host-002:trg-002:vfs.fs.size[/,pfree]",
                "dedup_count": 1,
                "storm_detected": False,
                "created_at": now,
                "updated_at": now,
            },
            {
                "source": "zabbix",
                "event_id": "evt-003",
                "trigger_id": "trg-003",
                "trigger_name": "Interface {IFNAME} down on {HOST.NAME}",
                "host_id": "host-003",
                "host_name": "router-core-01",
                "host_ip": "192.168.1.1",
                "severity": 5,
                "severity_label": "disaster",
                "item_key": "net.if.status[eth0]",
                "item_value": "0",
                "message": "Network interface eth0 is down",
                "tags": {"scope": "production", "team": "network"},
                "raw_payload": {"event_id": "evt-003"},
                "is_recovery": False,
                "dedup_key": "zabbix:host-003:trg-003:net.if.status[eth0]",
                "dedup_count": 1,
                "storm_detected": False,
                "created_at": now,
                "updated_at": now,
            },
        ]

        alerts: list[Alert] = []
        for data in alerts_data:
            alert = Alert(**data)
            session.add(alert)
            alerts.append(alert)

        await session.flush()
        logger.info("Seeded %d mock alerts", len(alerts_data))

        from app.models.ai_analysis import AIAnalysis
        analyses_data = [
            {
                "alert_id": alerts[0].id,
                "summary": "CPU 使用率持续超过 90%，可能存在进程异常或资源不足",
                "possible_causes": ["业务流量突增", "存在 CPU 密集型进程", "应用程序内存泄漏导致频繁 GC"],
                "suggested_actions": ["检查 top/htop 中 CPU 占用最高的进程", "查看近期流量变化趋势", "考虑水平扩容或优化代码性能"],
                "risk_level": "high",
                "confidence": 0.85,
                "need_human_confirm": False,
                "model_used": "mock",
                "prompt": "mock prompt",
                "raw_response": {"summary": "mock response"},
                "latency_ms": 10,
                "created_at": now,
                "updated_at": now,
            },
            {
                "alert_id": alerts[1].id,
                "summary": "磁盘剩余空间不足 10%，需要及时清理或扩容",
                "possible_causes": ["日志文件过大", "临时文件未清理", "数据增长超出预期"],
                "suggested_actions": ["查找大文件并清理", "配置日志轮转策略", "评估扩容磁盘容量"],
                "risk_level": "medium",
                "confidence": 0.80,
                "need_human_confirm": False,
                "model_used": "mock",
                "prompt": "mock prompt",
                "raw_response": {"summary": "mock response"},
                "latency_ms": 8,
                "created_at": now,
                "updated_at": now,
            },
            {
                "alert_id": alerts[2].id,
                "summary": "核心路由器接口宕机，影响范围较大，需紧急处理",
                "possible_causes": ["物理链路故障", "交换机端口故障", "配置变更导致接口 down"],
                "suggested_actions": ["检查物理连接和指示灯状态", "登录设备查看接口日志", "联系网络团队进行应急处理"],
                "risk_level": "critical",
                "confidence": 0.90,
                "need_human_confirm": True,
                "model_used": "mock",
                "prompt": "mock prompt",
                "raw_response": {"summary": "mock response"},
                "latency_ms": 12,
                "created_at": now,
                "updated_at": now,
            },
        ]

        for data in analyses_data:
            analysis = AIAnalysis(**data)
            session.add(analysis)

        await session.commit()
        logger.info("Seeded %d mock AI analyses", len(analyses_data))


if __name__ == "__main__":
    import asyncio
    from app.core.logging import setup_logging
    setup_logging()
    asyncio.run(seed_mock_data())
