import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Button, Spin, message } from 'antd';
import { fetchAlert, analyzeAlert } from '../api/alerts';
import { fetchAnalyses } from '../api/ai';
import AlertSeverityTag from '../components/AlertSeverityTag';
import AIAnalysisPanel from '../components/AIAnalysisPanel';
import LoadingState from '../components/LoadingState';
import type { Alert } from '../types/alert';
import type { AIAnalysis } from '../types/ai';
import { formatDateTime } from '../utils/format';

const AlertDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadAnalysis = async (alertId: number) => {
    try {
      const resp = await fetchAnalyses(1, 1);
      const found = resp.data?.find((a) => a.alert_id === alertId) || null;
      setAnalysis(found);
    } catch {
      // ignore
    }
  };

  const load = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const resp = await fetchAlert(Number(id));
      if (resp.success && resp.data) {
        setAlert(resp.data);
        await loadAnalysis(resp.data.id);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const handleAnalyze = async () => {
    if (!alert) return;
    setAnalyzing(true);
    try {
      const resp = await analyzeAlert(alert.id);
      if (resp.success) {
        message.success('AI 分析完成');
        if (resp.data) {
          setAnalysis({
            id: resp.data.id,
            alert_id: alert.id,
            summary: resp.data.summary,
            possible_causes: JSON.stringify(resp.data.possible_causes),
            suggested_actions: JSON.stringify(resp.data.suggested_actions),
            risk_level: resp.data.risk_level,
            confidence: resp.data.confidence,
            need_human_confirm: resp.data.need_human_confirm,
            model_used: resp.data.model_used,
            prompt: '',
            raw_response: '',
            latency_ms: 0,
            created_at: new Date().toISOString(),
          });
        }
      } else {
        message.error(resp.message || '分析失败');
      }
    } catch {
      message.error('分析请求失败');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) return <LoadingState />;
  if (!alert) return <div>告警不存在</div>;

  return (
    <div>
      <Button onClick={() => navigate('/alerts')} style={{ marginBottom: 16 }}>返回列表</Button>
      <Card title={`告警详情 #${alert.id}`}>
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="事件 ID">{alert.event_id}</Descriptions.Item>
          <Descriptions.Item label="严重级别"><AlertSeverityTag severity={alert.severity} /></Descriptions.Item>
          <Descriptions.Item label="告警名称" span={2}>{alert.trigger_name}</Descriptions.Item>
          <Descriptions.Item label="主机">{alert.host_name}</Descriptions.Item>
          <Descriptions.Item label="IP">{alert.host_ip}</Descriptions.Item>
          <Descriptions.Item label="监控项">{alert.item_key}</Descriptions.Item>
          <Descriptions.Item label="当前值">{alert.item_value}</Descriptions.Item>
          <Descriptions.Item label="去重次数">{alert.dedup_count}</Descriptions.Item>
          <Descriptions.Item label="风暴检测">{alert.storm_detected ? '是' : '否'}</Descriptions.Item>
          <Descriptions.Item label="恢复事件">{alert.is_recovery ? '是' : '否'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatDateTime(alert.created_at)}</Descriptions.Item>
        </Descriptions>
      </Card>
      <div style={{ marginTop: 16 }}>
        <AIAnalysisPanel analysis={analysis} loading={analyzing} onAnalyze={handleAnalyze} />
      </div>
    </div>
  );
};

export default AlertDetail;
