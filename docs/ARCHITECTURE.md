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
2. **告警标准化**：将不同格式的 Zabbix 告警统一为 NormalizedAlert
3. **告警去重**：基于 Redis 在时间窗口内去重，避免重复分析
4. **风暴检测**：监控告警频率，超过阈值触发降级策略
5. **AI 分析**：通过 LLM Provider 对告警进行智能分析
6. **结果存储**：分析结果、用量数据存入 PostgreSQL
7. **前端展示**：通过 REST API 展示告警、分析结果、报表

## 后续演进路线

- **阶段 2**：接入真实 LLM API，实现流式分析
- **阶段 3**：知识库 RAG，自动修复建议
- **阶段 4**：多租户、权限控制、审计日志
- **阶段 5**：Kubernetes 部署、消息队列、时序数据库
