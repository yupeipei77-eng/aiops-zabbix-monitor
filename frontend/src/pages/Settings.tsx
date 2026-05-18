import React from 'react';
import { Card, Form, Input, Divider, message } from 'antd';

const Settings: React.FC = () => (
  <div>
    <Card title="系统设置（占位）">
      <Form layout="vertical" style={{ maxWidth: 500 }}>
        <Divider orientation="left">Zabbix 配置</Divider>
        <Form.Item label="Zabbix URL" help="Zabbix 服务器地址">
          <Input placeholder="http://zabbix.example.com" disabled />
        </Form.Item>
        <Form.Item label="Webhook API Key" help="用于验证 Zabbix Webhook 请求">
          <Input placeholder="配置在 .env 中" disabled />
        </Form.Item>

        <Divider orientation="left">AI 模型配置</Divider>
        <Form.Item label="默认模型" help="severity < 4 时使用">
          <Input placeholder="mock" disabled />
        </Form.Item>
        <Form.Item label="高级模型" help="severity >= 4 时使用">
          <Input placeholder="mock" disabled />
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
