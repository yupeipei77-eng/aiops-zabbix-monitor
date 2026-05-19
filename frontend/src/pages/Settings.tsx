import React from 'react';
import { Alert, Card, Form, Input, Divider } from 'antd';

const Settings: React.FC = () => (
  <div>
    <Card title="系统设置（占位）">
      <Alert
        message="AI 仅作为辅助分析，不影响 Zabbix 监控、告警入库和展示。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      <Form layout="vertical" style={{ maxWidth: 500 }}>
        <Divider orientation="left">Zabbix 配置</Divider>
        <Form.Item label="Zabbix URL" help="Zabbix 服务器地址">
          <Input placeholder="http://zabbix.example.com" disabled />
        </Form.Item>
        <Form.Item label="Webhook API Key" help="用于验证 Zabbix Webhook 请求">
          <Input placeholder="配置在 .env 中" disabled />
        </Form.Item>

        <Divider orientation="left">AI 模型配置</Divider>
        <Form.Item label="AI 总开关" help="关闭后系统仍按普通 Zabbix 告警平台运行">
          <Input placeholder="AI_ANALYSIS_ENABLED=true" disabled />
        </Form.Item>
        <Form.Item label="按等级启用" help="LOW/MEDIUM/HIGH/CRITICAL 可分别启停 AI">
          <Input placeholder="LOW=false, MEDIUM=false, HIGH=true, CRITICAL=true" disabled />
        </Form.Item>
        <Form.Item label="模型策略" help="每个等级可单独配置 provider 和 model">
          <Input placeholder="LLM_POLICY_HIGH_PROVIDER=deepseek" disabled />
        </Form.Item>
        <Form.Item label="中转站模型" help="OpenAI-compatible Gateway">
          <Input placeholder="GATEWAY_DEFAULT_MODEL=deepseek-v4-flash" disabled />
        </Form.Item>

        <Divider orientation="left">API Key（配置在 .env 中）</Divider>
        <Form.Item label="OpenAI API Key">
          <Input.Password placeholder="sk-..." disabled />
        </Form.Item>
        <Form.Item label="DeepSeek API Key">
          <Input.Password placeholder="sk-..." disabled />
        </Form.Item>
        <Form.Item label="Kimi API Key">
          <Input.Password placeholder="sk-..." disabled />
        </Form.Item>
        <Form.Item label="Mimo API Key">
          <Input.Password placeholder="sk-..." disabled />
        </Form.Item>
      </Form>
      <p style={{ color: '#999', marginTop: 16 }}>提示：所有配置通过 .env 文件管理，请在后端 .env 中修改。</p>
    </Card>
  </div>
);

export default Settings;
