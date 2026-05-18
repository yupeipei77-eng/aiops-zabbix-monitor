import React, { useEffect, useState } from 'react';
import { Table, Select, Input, Tag } from 'antd';
import { useNavigate } from 'react-router-dom';
import { fetchAlerts } from '../api/alerts';
import AlertSeverityTag from '../components/AlertSeverityTag';
import type { Alert } from '../types/alert';
import { formatDateTime } from '../utils/format';

const Alerts: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [severity, setSeverity] = useState<number | undefined>();
  const [hostName, setHostName] = useState('');
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const resp = await fetchAlerts({ page, page_size: 20, severity, host_name: hostName || undefined });
      if (resp.data) {
        setAlerts(resp.data);
        setTotal(resp.total);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [page, severity]);

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
    { title: '严重级别', dataIndex: 'severity', key: 'severity', width: 100, render: (v: number) => <AlertSeverityTag severity={v} /> },
    { title: '告警名称', dataIndex: 'trigger_name', key: 'trigger_name', ellipsis: true },
    { title: '主机', dataIndex: 'host_name', key: 'host_name', width: 150 },
    { title: 'IP', dataIndex: 'host_ip', key: 'host_ip', width: 140 },
    { title: '当前值', dataIndex: 'item_value', key: 'item_value', width: 100 },
    { title: '去重次数', dataIndex: 'dedup_count', key: 'dedup_count', width: 90 },
    { title: '风暴', dataIndex: 'storm_detected', key: 'storm_detected', width: 80, render: (v: boolean) => v ? <Tag color="red">是</Tag> : <Tag>否</Tag> },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180, render: (v: string) => formatDateTime(v) },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 12 }}>
        <Select
          placeholder="严重级别"
          allowClear
          style={{ width: 140 }}
          value={severity}
          onChange={(v) => { setSeverity(v); setPage(1); }}
          options={[
            { label: '未分类', value: 0 },
            { label: '信息', value: 1 },
            { label: '警告', value: 2 },
            { label: '一般', value: 3 },
            { label: '严重', value: 4 },
            { label: '灾难', value: 5 },
          ]}
        />
        <Input.Search
          placeholder="搜索主机名"
          style={{ width: 250 }}
          onSearch={(v) => { setHostName(v); setPage(1); load(); }}
          allowClear
        />
      </div>
      <Table
        columns={columns}
        dataSource={alerts}
        rowKey="id"
        loading={loading}
        pagination={{ current: page, total, pageSize: 20, onChange: setPage }}
        onRow={(record) => ({ onClick: () => navigate(`/alerts/${record.id}`), style: { cursor: 'pointer' } })}
      />
    </div>
  );
};

export default Alerts;
