import React, { useEffect, useState } from 'react';
import { Card, Descriptions, Spin } from 'antd';
import { fetchDailyReport } from '../api/reports';
import ReactECharts from 'echarts-for-react';
import type { DailyReport } from '../types/common';

const Reports: React.FC = () => {
  const [report, setReport] = useState<DailyReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const resp = await fetchDailyReport();
        if (resp.success) setReport(resp.data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spin />;
  if (!report) return <div>暂无数据</div>;

  const trendOption = {
    title: { text: '告警趋势（按小时）' },
    tooltip: { trigger: 'axis' as const },
    xAxis: { type: 'category' as const, data: report.hourly_trend.map((h) => `${h.hour}:00`) },
    yAxis: { type: 'value' as const },
    series: [{ data: report.hourly_trend.map((h) => h.count), type: 'line' as const, smooth: true, areaStyle: {} }],
  };

  return (
    <div>
      <Card title={`日报 - ${report.date}`}>
        <Descriptions column={3} bordered size="small">
          <Descriptions.Item label="总告警数">{report.total_alerts}</Descriptions.Item>
          <Descriptions.Item label="未处理">{report.unresolved_alerts}</Descriptions.Item>
          <Descriptions.Item label="严重告警">{report.critical_alerts}</Descriptions.Item>
          <Descriptions.Item label="AI 分析次数">{report.ai_analysis_count}</Descriptions.Item>
          <Descriptions.Item label="LLM 调用次数">{report.llm_call_count}</Descriptions.Item>
          <Descriptions.Item label="Token 用量">{report.token_usage}</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card style={{ marginTop: 16 }}>
        <ReactECharts option={trendOption} style={{ height: 350 }} />
      </Card>
    </div>
  );
};

export default Reports;
