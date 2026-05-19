# 真实 Zabbix 联调指南

本文档指导如何将生产 Zabbix Server 接入 AIOps Zabbix Monitor 平台。

---

## 一、架构概览

```
Zabbix Server
    ↓ (触发器触发)
Zabbix Action
    ↓ (Media Type: Webhook)
POST http://<your-server>:8000/api/v1/webhooks/zabbix
Header: X-API-Key: <WEBHOOK_API_KEY>
    ↓
AIOps Zabbix Monitor 后端
```

---

## 二、Zabbix Media Type Webhook 配置

### 2.1 创建 Media Type

登录 Zabbix 管理界面，进入 **Administration → Media types → Create media type**，按以下参数配置：

| 字段 | 值 |
|------|----|
| Name | `AIOps Zabbix Monitor` |
| Type | `Webhook` |
| Parameters | 见下方 |

### 2.2 Webhook Script

在 Media Type 的 **Script** 编辑器中填入以下 JavaScript：

```javascript
var request = new HttpRequest();
request.addHeader('Content-Type: application/json');
request.addHeader('X-API-Key: ' + params.api_key);

var payload = {
    event_id: event.id,
    trigger_id: event.triggerId,
    trigger_name: event.name,
    host_id: event.tags.host_id || event.host.id,
    host_name: event.host.name,
    host_ip: event.host.ip,
    severity: event.severity,
    item_key: event.item.key,
    item_value: event.item.value,
    event_time: event.time,
    event_value: event.value,
    tags: event.tags,
    raw_payload: event
};

var resp = request.post(
    params.webhook_url,
    JSON.stringify(payload)
);

return resp;
```

### 2.3 Webhook 参数

在 Media Type 的 **Parameters** 选项卡中添加：

| 名称 | 值 | 说明 |
|------|----|------|
| `webhook_url` | `http://your-server:8000/api/v1/webhooks/zabbix` | 后端 Webhook 接收地址 |
| `api_key` | `changeme-webhook-api-key` | 对应后端 `.env` 中的 `WEBHOOK_API_KEY` |

> **安全建议**：使用 Zabbix 宏变量 `#API_KEY` 管理 Key，避免明文写在参数中。

### 2.4 超时与重试

| 配置 | 推荐值 | 说明 |
|------|--------|------|
| Timeout | `30s` | 后端含 AI 分析时可能较慢 |
| Max attempts | `3` | 网络抖动时自动重试 |
| Attempt interval | `10s` | 重试间隔 |

---

## 三、Header X-API-Key 配置

后端通过 `X-API-Key` Header 校验请求合法性，缺失或错误均返回 **HTTP 401**。

### 3.1 后端配置

编辑 `.env` 文件：

```env
WEBHOOK_API_KEY=your-secure-production-key-here
```

### 3.2 安全注意事项

1. **不要在 Zabbix 前端明文暴露 Key**：使用 Zabbix 的宏变量 `{#MACRO}` 功能存储 Key，在 Action 配置中以 `{$WEBHOOK_API_KEY}` 形式引用。
2. **网络层加密**：生产环境应启用 HTTPS（通过反向代理如 Nginx/HAProxy）。
3. **定期轮换**：建议每 90 天更换一次 Key，Zabbix 和后端需同步更新。

### 3.3 后端校验逻辑

```
X-API-Key 缺失  →  401 "Missing API key"
X-API-Key 错误  →  401 "Invalid API key"
X-API-Key 正确  →  正常处理
```

---

## 四、Webhook Payload 模板

后端期望的 JSON 结构对应 `ZabbixWebhookPayload` schema：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `event_id` | string | 是 | Zabbix 事件 ID |
| `trigger_id` | string | 是 | 触发器 ID |
| `trigger_name` | string | 是 | 触发器名称 |
| `host_id` | string | 是 | 主机 ID |
| `host_name` | string | 是 | 主机名 |
| `host_ip` | string | 是 | 主机 IP |
| `severity` | string\|int | 否 | 0-5，默认 `0` |
| `item_key` | string | 是 | 监控项 Key |
| `item_value` | string | 是 | 监控项值 |
| `event_time` | string | 否 | 事件时间 ISO8601 |
| `event_value` | string\|int | 否 | 事件值 |
| `status` | string | 否 | 状态（用于恢复事件） |
| `tags` | object | 否 | 自定义标签 |
| `raw_payload` | object | 否 | 原始 payload |

### Severity 等级映射

| Zabbix 等级 | 数值 | 平台内部名称 |
|-------------|------|-------------|
| Not classified | 0 | LOW |
| Information | 1 | LOW |
| Warning | 2 | LOW |
| Average | 3 | MEDIUM |
| High | 4 | HIGH |
| Disaster | 5 | CRITICAL |

---

## 五、Action 触发条件

在 Zabbix 管理界面配置 Action，决定哪些告警通过 Webhook 上报。

### 5.1 创建 Action

进入 **Configuration → Actions → Trigger actions → Create action**：

| 字段 | 值 |
|------|----|
| Name | `Send to AIOps Monitor` |
| Event source | `Triggers` |
| Active | `No`（先在测试环境验证） |

### 5.2 触发条件示例

仅上报 High 和 Disaster 及以上告警：

```
Trigger severity >= High
```

按主机组过滤：

```
Host group = Production Servers
```

排除特定触发器：

```
Trigger name does not contain "Test"
```

组合条件：

```
Trigger severity >= Warning
AND Host group in [Production, Staging]
AND Trigger name does not contain "Test"
```

### 5.3 操作配置

| 字段 | 值 |
|------|----|
| Default operation step duration | `60s` |
| Send to User groups | `AIOps Admins` |
| Send only to | `AIOps Zabbix Monitor`（上面创建的 Media Type） |

---

## 六、测试告警方法

### 6.1 方式一：使用本项目提供的测试脚本

```bash
# 确保后端已启动
cd /path/to/aiops-zabbix-monitor

# 方法 1：使用 Makefile
make webhook-test

# 方法 2：直接运行脚本
./scripts/test_zabbix_webhook.sh

# 方法 3：手动发送一条告警
curl -X POST http://localhost:8000/api/v1/webhooks/zabbix \
  -H "Content-Type: application/json" \
  -H "X-API-Key: changeme-webhook-api-key" \
  -d @mock/zabbix_real_payload_example.json
```

### 6.2 方式二：通过 Zabbix 手动触发

1. 进入 **Monitoring → Triggers**，选择一个已知告警
2. 右键选择 **Execute now**，手动触发 Webhook 发送
3. 查看后端日志确认是否接收成功

### 6.3 方式三：使用 Zabbix 内置测试

进入 **Administration → Media types → AIOps Zabbix Monitor → Test**：

1. 填入测试参数
2. 点击 **Test** 发送测试请求
3. 查看返回的 HTTP 状态码和响应内容

### 6.4 验证收到告警

发送后检查：

```bash
# 检查后端日志
docker compose logs --tail=20 backend

# 查询告警列表
curl -s http://localhost:8000/api/v1/alerts | python3 -m json.tool

# 查询特定告警详情
curl -s http://localhost:8000/api/v1/alerts/1 | python3 -m json.tool
```

---

## 七、常见错误排查

### 7.1 HTTP 401 — API Key 错误

**现象**：`{"detail": "Invalid API key"}` 或 `{"detail": "Missing API key"}`

**排查**：

1. 确认 Zabbix Media Type 参数中 `api_key` 的值与后端 `.env` 中 `WEBHOOK_API_KEY` 完全一致
2. 确认 Zabbix 脚本中 `request.addHeader('X-API-Key: ' + params.api_key)` 正确添加 Header
3. 注意 Zabbix 宏变量中可能存在前后空格

### 7.2 HTTP 422 — Payload 校验失败

**现象**：`{"detail": [...]}` 包含字段校验错误

**排查**：

1. 确认 payload 包含必填字段：`event_id`、`trigger_id`、`trigger_name`、`host_id`、`host_name`、`host_ip`、`item_key`、`item_value`
2. `severity` 字段必须是字符串或整数（Zabbix 脚本中 `event.severity` 直接传入即可）
3. 检查 JSON 格式是否合法（使用在线 JSON 校验器）

### 7.3 Connection Refused — 端口不可访问

**现象**：Zabbix 日志中出现 `Connection refused`

**排查**：

1. 确认后端服务正在运行：`docker compose ps`
2. 确认端口映射正确：`docker compose config | grep ports`
3. 确认防火墙/安全组放行 8000 端口
4. 从 Zabbix Server 测试连通性：`curl -v http://your-server:8000/api/v1/health`

### 7.4 Timeout — 请求超时

**现象**：Zabbix 日志中出现 `Timeout while connecting`

**排查**：

1. 增加 Media Type 的 Timeout 设置（建议 30s）
2. 后端含 AI 分析时较慢，可配置 `AI_ANALYSIS_ENABLED=false` 先测试主链路
3. 检查 Zabbix Server 与后端之间的网络延迟

### 7.5 告警未入库

**现象**：Webhook 返回 success 但前端看不到告警

**排查**：

1. 检查去重逻辑：相同 `dedup_key` 的告警只更新 `dedup_count`，不新增行
2. 检查前端是否刷新：`GET /api/v1/alerts` 直接查询 API
3. 检查数据库：`docker compose exec postgres psql -U aiops -c "SELECT * FROM alerts ORDER BY id DESC LIMIT 5;"`

### 7.6 风暴模式误触发

**现象**：大量告警被标记 `storm_detected=true`

**排查**：

1. 检查 `.env` 中的 `STORM_THRESHOLD`（默认 50）是否与实际告警频率匹配
2. 检查 `STORM_WINDOW_SECONDS`（默认 600 = 10 分钟）窗口是否合理

---

## 八、生产部署清单

- [ ] 修改 `.env` 中的 `WEBHOOK_API_KEY` 为随机生成的强密钥
- [ ] 在后端启用 HTTPS（通过 Nginx/HAProxy 反向代理 + Let's Encrypt 证书）
- [ ] 在 Zabbix 中使用宏变量 `{$WEBHOOK_API_KEY}` 存储 API Key
- [ ] 配置防火墙仅允许 Zabbix Server IP 访问后端 Webhook 端口
- [ ] 设置告警风暴阈值与实际告警频率匹配
- [ ] 配置 Zabbix Action 触发条件，过滤测试告警
- [ ] 配置 Zabbix Media Type 超时为 30s，重试次数 3
- [ ] 发送一条真实告警验证全链路正常
- [ ] 配置后端日志持久化，便于故障排查

---

## 九、参考

- [Zabbix 官方文档 — Webhook](https://www.zabbix.com/documentation/current/en/manual/config/notifications/media/webhook)
- [Zabbix 宏变量](https://www.zabbix.com/documentation/current/en/manual/config/macros)
- 项目内参考文档：`docs/ZABBIX_WEBHOOK_EXAMPLE.md`
- 项目内测试脚本：`mock/webhook_test.sh`、`scripts/test_zabbix_webhook.sh`
