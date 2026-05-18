import React, { useEffect, useState } from 'react';
import { Row, Col } from 'antd';
import MetricCard from '../components/MetricCard';
import LoadingState from '../components/LoadingState';
import { fetchDashboardSummary } from '../api/reports';
import { fetchAlerts } from '../api/alerts';
import type { DashboardSummary } from '../types/common';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [chartData, setChartData] = useState<Array<{ name: string; value: number }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [summaryResp, alertsResp] = await Promise.all([fetchDashboardSummary(), fetchAlerts({ page: 1, page_size: 50 })]);
        if (summaryResp.success) setSummary(summaryResp.data);
        if (alertsResp.data) {
          const countByHour: Record<string, number> = {};
          alertsResp.data.forEach((a) => {
            const hour = dayjs(a.created_at).format('HH:00');
            countByHour[hour] = (countByHour[hour] || 0) + 1;
          });
          setChartData(Object.entries(countByHour).map(([name, value]) => ({ name, value })));
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <LoadingState />;

  const chartOption = {
    title: { text: '告警趋势' },
    tooltip: { trigger: 'axis' as const },
    xAxis: { type: 'category' as const, data: chartData.map((d) => d.name) },
    yAxis: { type: 'value' as const },
    series: [{ data: chartData.map((d) => d.value), type: 'bar' as const, itemStyle: { color: '#1890ff' } }],
  };

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={5}>
          <MetricCard title="总告警数" value={summary?.total_alerts || 0} color="#1890ff" />
        </Col>
        <Col span={5}>
          <MetricCard title="未处理告警" value={summary?.unresolved_alerts || 0} color="#faad14" />
        </Col>
        <Col span={5}>
          <MetricCard title="严重告警" value={summary?.critical_alerts || 0} color="#ff4d4f" />
        </Col>
        <Col span={5}>
          <MetricCard title="AI 分析次数" value={summary?.ai_analysis_count || 0} color="#52c41a" />
        </Col>
        <Col span={4}>
          <MetricCard title="LLM 调用次数" value={summary?.llm_call_count || 0} color="#722ed1" />
        </Col>
      </Row>
      <ReactECharts option={chartOption} style={{ height: 350 }} />
    </div>
  );
};

export default Dashboard;
