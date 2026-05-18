import React, { useState } from 'react';
import { Card, Descriptions, Tag, Button, Spin, Alert as AntAlert } from 'antd';
import type { AIAnalysis } from '../types/ai';

interface Props {
  analysis: AIAnalysis | null;
  loading?: boolean;
  onAnalyze?: () => void;
}

const AIAnalysisPanel: React.FC<Props> = ({ analysis, loading, onAnalyze }) => {
  if (loading) {
    return (
      <Card title="AI 分析">
        <Spin tip="AI 分析中..." />
      </Card>
    );
  }

  if (!analysis) {
    return (
      <Card title="AI 分析">
        <AntAlert message="暂无 AI 分析结果" type="info" showIcon />
        {onAnalyze && (
          <Button type="primary" onClick={onAnalyze} style={{ marginTop: 16 }}>
            触发 AI 分析
          </Button>
        )}
      </Card>
    );
  }

  const causes = typeof analysis.possible_causes === 'string' ? JSON.parse(analysis.possible_causes) : analysis.possible_causes;
  const actions = typeof analysis.suggested_actions === 'string' ? JSON.parse(analysis.suggested_actions) : analysis.suggested_actions;

  const riskColors: Record<string, string> = {
    low: 'green',
    medium: 'orange',
    high: 'red',
    critical: 'magenta',
  };

  return (
    <Card title={`AI 分析 (${analysis.model_used})`}>
      <Descriptions column={1} bordered size="small">
        <Descriptions.Item label="摘要">{analysis.summary}</Descriptions.Item>
        <Descriptions.Item label="风险等级">
          <Tag color={riskColors[analysis.risk_level] || 'default'}>{analysis.risk_level}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="置信度">{(analysis.confidence * 100).toFixed(1)}%</Descriptions.Item>
        <Descriptions.Item label="可能原因">
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {Array.isArray(causes) && causes.map((c: string, i: number) => <li key={i}>{c}</li>)}
          </ul>
        </Descriptions.Item>
        <Descriptions.Item label="建议操作">
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {Array.isArray(actions) && actions.map((a: string, i: number) => <li key={i}>{a}</li>)}
          </ul>
        </Descriptions.Item>
        <Descriptions.Item label="需人工确认">
          {analysis.need_human_confirm ? <Tag color="red">是</Tag> : <Tag color="green">否</Tag>}
        </Descriptions.Item>
        <Descriptions.Item label="耗时">{analysis.latency_ms}ms</Descriptions.Item>
      </Descriptions>
    </Card>
  );
};

export default AIAnalysisPanel;
