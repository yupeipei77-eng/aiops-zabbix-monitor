# 架构文档

## 总体架构

```
Zabbix Server
    │
    │ Webhook (HTTP POST)
    ▼
┌──────────────────────────────┐
│        Backend (FastAPI)      │
│  ┌────────────────────────┐  │
│  │  Webhook Endpoint      │  │
│  │        ↓               │  │
│  │  AlertNormalizer       │  │
│  │        ↓               │  │
│  │  AlertDeduplicator     │  │──→ Redis (去重/风暴检测)
│  │        ↓               │  │
│  │  StormDetector         │  │
│  │        ↓               │  │
│  │  AIOrchestrator        │  │
│  │    ├─ PromptBuilder    │  │
│  │    ├─ ModelRouter      │  │
│  │    └─ LLM Provider     │  │──→ OpenAI/DeepSeek/Kimi/Mimo/Mock
│  │        ↓               │  │
│  │  Save Results          │  │──→ PostgreSQL
│  └────────────────────────┘  │
└──────────────────────────────┘
    │
    │ REST API
    ▼
┌──────────────────────────────┐
│     Frontend (React + Vite)   │
│  Dashboard / Alerts / AI     │
│  Knowledge / Reports         │
└──────────────────────────────┘
```

## 数据流

1. **Zabbix 告警接收**：Zabbix 通过 Webhook 将告警推送到后端
2. **告警标准化**：将 Zabbix severity、tags、恢复状态和原始 payload 统一为内部 Alert 结构
3. **告警去重**：基于 Redis 在 5 分钟窗口内去重，重复告警只更新 `dedup_count`，不重复调用 AI
4. **风暴检测**：10 分钟内超过阈值触发降级策略，告警继续入库但跳过逐条 AI 分析
5. **AI 分析**：通过 ModelRouter 选择 LLM Provider，默认使用 Mock，真实 Provider 未配置 API Key 时 fallback 到 Mock
6. **结果存储**：告警、AI 分析、LLM 用量、知识库和修复计划存入 PostgreSQL，结构化字段使用 JSONB
7. **前端展示**：通过 REST API 展示告警、分析结果、报表

## 后端分层

- `api/v1/endpoints`：只处理 HTTP 参数、依赖和响应。
- `services`：承载标准化、去重、风暴检测、Prompt 构建、AI 编排和报表逻辑。
- `repositories`：封装 SQLAlchemy 查询和写入。
- `models`：SQLAlchemy 持久化模型，JSON 结构在 PostgreSQL 中使用 JSONB。
- `schemas`：Pydantic 请求/响应模型，和数据库模型分离。

## 数据库与启动

后端启动不再自动 `create_all`，schema 由 Alembic 管理。标准启动顺序是：

```bash
cp .env.example .env
make up
make migrate
make seed
```

这样可以避免应用启动时提前建表，导致后续迁移重复创建表。

## Redis Key

- 去重：`aiops:dedup:{dedup_key}`，value 为 JSON，包含 `count`、`first_seen`、`last_seen`。
- 风暴：`aiops:storm:counter`，按 `STORM_WINDOW_SECONDS` 过期。

## 后续演进路线

- **阶段 2**：接入真实 LLM API，实现流式分析
- **阶段 3**：知识库 RAG，自动修复建议
- **阶段 4**：多租户、权限控制、审计日志
- **阶段 5**：Kubernetes 部署、消息队列、时序数据库
