# AIOps Zabbix Monitor

面向 Zabbix 告警场景的 AI 智能运维平台。项目把 Zabbix Webhook、告警标准化、去重与风暴检测、LLM 分析、知识库和前端看板整合成一条完整链路，帮助运维人员更快理解告警、定位原因并给出处理建议。

## 一句话定位

这是一个“Zabbix 告警接入 + AI 分析 + 运维可视化”的全栈项目。

## 给大模型的快速理解

### 项目目标

- 接收 Zabbix 通过 Webhook 推送的告警
- 将不同格式的告警统一为标准结构
- 做告警去重，避免重复分析
- 检测短时间内的告警风暴并触发降级策略
- 调用可插拔 LLM Provider 生成告警分析、归因和处置建议
- 将分析结果、用量和知识库内容持久化
- 通过前端 Dashboard / Alerts / AI Analysis / Reports / Knowledge Base 展示结果

### 核心数据流

1. Zabbix Server 发送 Webhook 到后端 `/api/v1/webhooks/zabbix`
2. `AlertNormalizer` 把原始 payload 转成统一告警模型
3. `AlertDeduplicator` 基于 Redis 去重
4. `StormDetector` 判断是否进入告警风暴状态
5. `AIOrchestrator` 选择模型并生成分析结果
6. `ReportService`、仓储层和数据库保存分析、告警和用量数据
7. React 前端读取 REST API 展示告警、分析结论和报表

### 分层架构

- `backend/app/api`：HTTP API 路由
- `backend/app/services`：告警处理、AI 编排、风暴检测、报表和通知
- `backend/app/llm`：LLM Provider 抽象层，支持 Mock、OpenAI、DeepSeek、Kimi、Mimo
- `backend/app/models`：SQLAlchemy 数据模型
- `backend/app/repositories`：数据访问层
- `frontend/src/pages`：Dashboard、Alerts、Alert Detail、AI Analysis、Reports、Settings、Knowledge Base
- `mock/`：模拟 Zabbix payload 和 webhook 测试脚本
- `docs/`：架构、API、Roadmap、Webhook 示例

## 技术栈

- 后端：FastAPI、SQLAlchemy、Alembic、Pydantic、Redis、PostgreSQL
- 前端：React、Vite、TypeScript、Ant Design、ECharts、Zustand
- 部署：Docker Compose
- LLM：可插拔 Provider 设计

## 快速启动

```bash
cp .env.example .env
make up
make migrate
make seed
```

访问：
- 前端：http://localhost:3000
- 后端 API 文档：http://localhost:8000/docs

## 常用命令

```bash
make up           # 启动服务
make down         # 停止服务
make logs         # 查看日志
make migrate      # 运行数据库迁移
make seed         # 填充 Mock 数据
make webhook-test # 测试 Webhook
make test         # 运行所有测试
make backend-test # 运行后端测试
```

## API 入口

- `GET /api/v1/health`
- `POST /api/v1/webhooks/zabbix`
- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{id}`
- `POST /api/v1/ai/{id}/analyze`
- `GET /api/v1/ai`
- `GET /api/v1/llm/usage`
- `GET /api/v1/reports/daily`
- `GET /api/v1/reports/dashboard`
- `GET/POST /api/v1/knowledge`

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://aiops:aiops@postgres:5432/aiops` |
| `REDIS_URL` | Redis 连接串 | `redis://redis:6379/0` |
| `WEBHOOK_API_KEY` | Zabbix Webhook 验证 Key | `changeme-webhook-api-key` |
| `DEFAULT_LLM_PROVIDER` | 默认 LLM 提供商 | `mock` |
| `ADVANCED_LLM_PROVIDER` | 高级 LLM 提供商 | `mock` |

## 目录结构

```text
aiops-zabbix-monitor/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── core/     # 配置、日志、安全、错误处理
│   │   ├── api/      # API 路由
│   │   ├── models/   # SQLAlchemy 模型
│   │   ├── schemas/  # Pydantic 模型
│   │   ├── services/ # 业务逻辑
│   │   ├── llm/      # LLM Provider 抽象
│   │   ├── repositories/ # 数据访问层
│   │   └── db/       # 数据库初始化
│   └── alembic/      # 数据库迁移
├── frontend/         # React 前端
├── mock/             # Mock 数据和测试脚本
├── docs/             # 文档
└── docker-compose.yml
```

## 后续演进

- 阶段 2：接入真实 LLM API，实现流式分析
- 阶段 3：知识库 RAG，自动修复建议
- 阶段 4：多租户、权限控制、审计日志
- 阶段 5：Kubernetes 部署、消息队列、时序数据库
