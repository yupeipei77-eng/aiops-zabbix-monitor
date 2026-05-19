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
- `backend/app/llm`：LLM Provider 抽象层，支持 Mock、OpenAI、DeepSeek、Kimi、Mimo 和 OpenAI-compatible 中转站
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

当前 MVP 默认使用 `mock` LLM Provider，不需要配置任何真实模型 Key 就能跑通 Webhook、入库、Mock AI 分析和前端展示。

```bash
cp .env.example .env
make build
make up
make migrate
make seed
make webhook-test
make test
```

访问：
- 前端：http://localhost:3000
- 后端 API 文档：http://localhost:8000/docs

## 常用命令

```bash
make up           # 启动服务
make build        # 构建镜像
make down         # 停止服务
make logs         # 查看日志
make migrate      # 运行数据库迁移
make seed         # 填充 Mock 数据
make webhook-test # 发送 4 类 Mock Zabbix payload 并查询结果
make test         # 运行所有测试
make backend-test # 运行后端测试
make frontend-test # 构建前端
```

## API 入口

- `GET /api/v1/health`
- `POST /api/v1/webhooks/zabbix`
- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{id}`
- `GET /api/v1/ai`
- `GET /api/v1/ai/alerts/{id}`
- `POST /api/v1/ai/{id}/analyze`
- `GET /api/v1/llm`
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
| `DEEPSEEK_API_KEY` | DeepSeek API Key，留空时不会调用 DeepSeek | 空 |
| `DEEPSEEK_BASE_URL` | DeepSeek OpenAI-compatible API 地址，留空使用 `https://api.deepseek.com` | 空 |
| `DEEPSEEK_MODEL` | DeepSeek 模型名 | `deepseek-chat` |
| `MIMO_API_KEY` | Mimo API Key，留空时不会调用 Mimo | 空 |
| `MIMO_BASE_URL` | Mimo OpenAI-compatible API 地址，留空使用 `https://api.mimo-v2.com/v1` | 空 |
| `MIMO_MODEL` | Mimo 模型名 | `mimo` |
| `GATEWAY_API_KEY` | OpenAI-compatible 中转站 API Key，留空时不可用 | 空 |
| `GATEWAY_BASE_URL` | 中转站 API Base URL，例如 `https://gateway.example.com/v1` | 空 |
| `GATEWAY_DEFAULT_MODEL` | 中转站默认模型 | `deepseek-v4-flash` |
| `GATEWAY_PROVIDER_NAME` | 中转站用量记录里的 provider 名称 | `gateway` |
| `LLM_POLICY_LOW_PROVIDER` / `LLM_POLICY_LOW_MODEL` | severity `0-2` 使用的 provider/model | `mock` / `mock` |
| `LLM_POLICY_MEDIUM_PROVIDER` / `LLM_POLICY_MEDIUM_MODEL` | severity `3` 使用的 provider/model | `mock` / `mock` |
| `LLM_POLICY_HIGH_PROVIDER` / `LLM_POLICY_HIGH_MODEL` | severity `4` 使用的 provider/model | `mock` / `mock` |
| `LLM_POLICY_CRITICAL_PROVIDER` / `LLM_POLICY_CRITICAL_MODEL` | severity `5` 使用的 provider/model | `mock` / `mock` |
| `DEDUP_WINDOW_SECONDS` | 重复告警去重窗口 | `300` |
| `STORM_WINDOW_SECONDS` | 告警风暴统计窗口 | `600` |
| `STORM_THRESHOLD` | 风暴阈值 | `50` |
| `CORS_ORIGINS` | 允许访问后端的前端源 | `http://localhost:3000` |

## 配置 DeepSeek 原生 API

默认配置如下，适合本地无 Key 验收：

```env
DEFAULT_LLM_PROVIDER=mock
ADVANCED_LLM_PROVIDER=mock
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=
DEEPSEEK_MODEL=deepseek-chat
```

如果要让严重告警走 DeepSeek，把 `.env` 改为：

```env
DEEPSEEK_API_KEY=你的 DeepSeek Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

LLM_POLICY_HIGH_PROVIDER=deepseek
LLM_POLICY_HIGH_MODEL=deepseek-v4-pro
LLM_POLICY_CRITICAL_PROVIDER=deepseek
LLM_POLICY_CRITICAL_MODEL=deepseek-v4-pro
```

DeepSeek 调用失败时，`AIOrchestrator` 会记录一条 `success=false` 的 `llm_usage`，然后自动 fallback 到 `mock`，避免 Webhook 主链路因为模型异常而失败。

## 配置 Mimo 原生 API

如果要让严重告警走 Mimo，把 `.env` 改为：

```env
MIMO_API_KEY=你的 Mimo Key
MIMO_BASE_URL=你的 Mimo API Base URL
MIMO_MODEL=mimo-v2.5-pro

LLM_POLICY_CRITICAL_PROVIDER=mimo
LLM_POLICY_CRITICAL_MODEL=mimo-v2.5-pro
```

`MimoProvider` 默认按 OpenAI-compatible Chat Completions 调用 `POST {MIMO_BASE_URL}/chat/completions`。如果 `MIMO_BASE_URL` 留空，默认使用 `https://api.mimo-v2.com/v1`。如果你的 Mimo 接口不是 OpenAI-compatible，需要按平台文档修改 `backend/app/llm/mimo_provider.py` 里的 `chat()` 请求格式。

## 配置中转站 API

如果你使用的是 OneAPI、LiteLLM、OpenRouter 或自建 OpenAI-compatible 中转站，可以配置 `gateway` provider：

```env
GATEWAY_API_KEY=你的中转站 Key
GATEWAY_BASE_URL=https://gateway.example.com/v1
GATEWAY_DEFAULT_MODEL=deepseek-v4-flash
GATEWAY_PROVIDER_NAME=gateway
```

`OpenAICompatibleGatewayProvider` 会调用 `POST {GATEWAY_BASE_URL}/chat/completions`，请求体使用 `model`、`messages`、`temperature` 和 `response_format: {"type": "json_object"}`。中转站未配置 Key 或 Base URL 时不可用，路由器会自动 fallback 到 `mock`。

## 按告警等级选择模型

`ModelRouter` 现在按 severity 选择 provider + model：

```env
LLM_POLICY_LOW_PROVIDER=gateway
LLM_POLICY_LOW_MODEL=deepseek-v4-flash

LLM_POLICY_MEDIUM_PROVIDER=deepseek
LLM_POLICY_MEDIUM_MODEL=deepseek-v4-flash

LLM_POLICY_HIGH_PROVIDER=deepseek
LLM_POLICY_HIGH_MODEL=deepseek-v4-pro

LLM_POLICY_CRITICAL_PROVIDER=mimo
LLM_POLICY_CRITICAL_MODEL=mimo-v2.5-pro
```

映射规则：

- severity `0-2`：LOW
- severity `3`：MEDIUM
- severity `4`：HIGH
- severity `5`：CRITICAL

如果 `LLM_POLICY_*` 保持默认 `mock/mock`，旧配置 `DEFAULT_LLM_PROVIDER` / `ADVANCED_LLM_PROVIDER` 仍可兼容使用。无论是 DeepSeek、Mimo 还是中转站，调用失败都会记录 `llm_usage.success=false` 并 fallback 到 `mock`。

## 手动指定 provider + model

手动分析接口可以覆盖策略路由：

```http
POST /api/v1/ai/{alert_id}/analyze
Content-Type: application/json

{
  "provider": "gateway",
  "model": "deepseek-v4-flash"
}
```

也可以直接指定原生 provider：

```json
{
  "provider": "deepseek",
  "model": "deepseek-v4-pro"
}
```

```json
{
  "provider": "mimo",
  "model": "mimo-v2.5-pro"
}
```

## 当前 MVP 行为

- Webhook 使用 `X-API-Key` 校验，缺失或错误返回统一 `401` 响应。
- Zabbix severity 会标准化为 `0-5`，支持 `Disaster`、`High`、`Average`、`Warning`、`Information`、`Not classified`。
- 去重 key 为 `zabbix:{host_id}:{trigger_id}:{item_key}`，Redis key 为 `aiops:dedup:{dedup_key}`，value 记录 `count`、`first_seen`、`last_seen`。
- 重复告警不会新增 `alerts` 行，只更新原告警的 `dedup_count` 和 `updated_at`，也不会重复触发 AI。
- 10 分钟内超过阈值后进入 storm 模式，Webhook 仍入库，但跳过逐条 AI 分析并标记 `storm_detected=true`。
- 默认 LLM provider 为 `mock`；真实 provider 未配置 API Key 时自动 fallback 到 mock。
- 知识库当前只做文档保存与列表展示，暂不做向量检索。

## 本地验收命令

完整 Docker Compose 验收：

```bash
cp .env.example .env
docker compose config
make build
make up
make migrate
make seed
make webhook-test
make test
```

不依赖 Docker 的快速开发验收：

```bash
cd backend
uv sync --extra dev
uv run pytest -q

cd ../frontend
npm ci
npm run build
```

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
