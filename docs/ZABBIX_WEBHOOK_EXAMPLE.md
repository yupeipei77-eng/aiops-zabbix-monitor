# Zabbix Webhook 配置示例

## Zabbix Media Type 配置

在 Zabbix 管理界面中创建新的 Media Type：

1. 进入 **Administration → Media types → Create media type**
2. 类型选择 **Webhook**
3. 配置参数：

```javascript
// Zabbix Webhook Script
var request = new HttpRequest();
request.addHeader('Content-Type: application/json');
request.addHeader('X-API-Key: ' + params.api_key);

var payload = {
    event_id: event.id,
    trigger_id: event.triggerId,
    trigger_name: event.tags.trigger_name || event.name,
    host_id: event.tags.host_id || '',
    host_name: event.tags.host_name || '',
    host_ip: event.tags.host_ip || '',
    severity: event.severity,
    item_key: event.tags.item_key || '',
    item_value: event.tags.item_value || '',
    event_time: event.time,
    tags: event.tags,
    raw_payload: event
};

var resp = request.post(
    params.webhook_url,
    JSON.stringify(payload)
);

return resp;
```

4. 配置 Webhook 参数：

| 参数 | 值 |
|------|------|
| webhook_url | http://your-server:8000/api/v1/webhooks/zabbix |
| api_key | your-webhook-api-key |

## Webhook Payload 示例

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
  "tags": {
    "scope": "production",
    "team": "infra"
  }
}
```

## 注意事项

1. **API Key 安全**：不要在 Zabbix 前端暴露 API Key，使用 Zabbix 的宏变量管理
2. **网络连通**：确保 Zabbix Server 能访问后端 Webhook 地址
3. **超时设置**：建议 Webhook 超时设为 10 秒以上
4. **重试策略**：Zabbix 5.0+ 支持 Webhook 重试，建议开启
5. **告警模板**：配置 Zabbix Action 将告警路由到此 Webhook
6. **恢复事件**：恢复事件也会触发 Webhook，系统会自动识别 `is_recovery`
7. **严重级别映射**：Zabbix 0=未分类, 1=信息, 2=警告, 3=一般, 4=严重, 5=灾难
