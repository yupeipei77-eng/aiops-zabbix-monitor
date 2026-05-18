# API 文档

## 通用响应格式

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

分页响应：
```json
{
  "success": true,
  "data": [],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "message": ""
}
```

## 接口列表

### GET /api/v1/health

健康检查。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "aiops-zabbix-monitor",
    "version": "0.1.0"
  },
  "message": ""
}
```

### POST /api/v1/webhooks/zabbix

接收 Zabbix Webhook 告警。

**请求头：**
- `X-API-Key`: Webhook API Key（必填）
- `Content-Type`: application/json

**请求体示例：**
```json
{
  "event_id": "zbx-evt-1001",
  "trigger_id": "trg-cpu-high",
  "trigger_name": "CPU usage over 90% on {HOST.NAME}",
  "host_id": "host-web-01",
  "host_name": "web-server-01",
  "host_ip": "192.168.1.10",
  "severity": "4",
  "item_key": "system.cpu.util",
  "item_value": "95.2",
  "event_time": "2025-01-15T10:30:00Z",
  "tags": {"scope": "production"},
  "raw_payload": {}
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "alert_id": 1,
    "is_duplicate": false,
    "storm_detected": false
  },
  "message": "Alert accepted"
}
```

### GET /api/v1/alerts

告警列表，支持分页和筛选。

**查询参数：**
- `page` (int): 页码，默认 1
- `page_size` (int): 每页数量，默认 20
- `severity` (int): 严重级别筛选 (0-5)
- `host_name` (str): 主机名模糊搜索

### GET /api/v1/alerts/{alert_id}

告警详情。

### POST /api/v1/ai/{alert_id}/analyze

触发 AI 分析。

**请求体（可选）：**
```json
{
  "provider": "mock"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "alert_id": 1,
    "summary": "检测到系统资源异常...",
    "possible_causes": ["原因1", "原因2"],
    "suggested_actions": ["建议1", "建议2"],
    "risk_level": "medium",
    "confidence": 0.75,
    "need_human_confirm": false,
    "model_used": "mock"
  }
}
```

### GET /api/v1/ai

AI 分析记录列表。

### GET /api/v1/llm/usage

LLM Token 用量记录。

### GET /api/v1/reports/daily

日报摘要。

### GET /api/v1/reports/dashboard

Dashboard 总览数据。

### GET /api/v1/knowledge

知识库文档列表。

### POST /api/v1/knowledge

创建知识库文档。

**请求体：**
```json
{
  "title": "文档标题",
  "source": "manual",
  "content": "文档内容",
  "tags": ["tag1", "tag2"]
}
```
