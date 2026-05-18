import React, { useEffect, useState } from 'react';
import { Table, Tag } from 'antd';
import { fetchAnalyses } from '../api/ai';
import type { AIAnalysis } from '../types/ai';
import { formatDateTime } from '../utils/format';

const AIAnalysisPage: React.FC = () => {
  const [data, setData] = useState<AIAnalysis[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const resp = await fetchAnalyses(page, 20);
        if (resp.data) {
          setData(resp.data);
          setTotal(resp.total);
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [page]);

  const riskColors: Record<string, string> = { low: 'green', medium: 'orange', high: 'red', critical: 'magenta' };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
    { title: '告警 ID', dataIndex: 'alert_id', key: 'alert_id', width: 90 },
    { title: '摘要', dataIndex: 'summary', key: 'summary', ellipsis: true },
    { title: '风险等级', dataIndex: 'risk_level', key: 'risk_level', width: 100, render: (v: string) => <Tag color={riskColors[v] || 'default'}>{v}</Tag> },
    { title: '置信度', dataIndex: 'confidence', key: 'confidence', width: 90, render: (v: number) => `${(v * 100).toFixed(0)}%` },
    { title: '模型', dataIndex: 'model_used', key: 'model_used', width: 100 },
    { title: '人工确认', dataIndex: 'need_human_confirm', key: 'need_human_confirm', width: 100, render: (v: boolean) => v ? <Tag color="red">是</Tag> : <Tag color="green">否</Tag> },
    { title: '耗时', dataIndex: 'latency_ms', key: 'latency_ms', width: 80, render: (v: number) => `${v}ms` },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180, render: (v: string) => formatDateTime(v) },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="id"
      loading={loading}
      pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
    />
  );
};

export default AIAnalysisPage;
