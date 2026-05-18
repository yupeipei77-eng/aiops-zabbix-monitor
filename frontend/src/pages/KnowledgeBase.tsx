import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Tag } from 'antd';
import client from '../api/client';

interface KnowledgeDoc {
  id: number;
  title: string;
  source: string;
  content: string;
  tags: string;
  created_at: string;
}

const KnowledgeBase: React.FC = () => {
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const resp = await client.get('/knowledge');
      if (resp.data?.success) setDocs(resp.data.data || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (values: { title: string; source: string; content: string; tags?: string[] }) => {
    try {
      await client.post('/knowledge', values);
      message.success('创建成功');
      setModalOpen(false);
      form.resetFields();
      load();
    } catch {
      message.error('创建失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '来源', dataIndex: 'source', key: 'source', width: 120 },
    { title: '内容', dataIndex: 'content', key: 'content', ellipsis: true },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  ];

  return (
    <div>
      <Button type="primary" onClick={() => setModalOpen(true)} style={{ marginBottom: 16 }}>新增文档</Button>
      <Table columns={columns} dataSource={docs} rowKey="id" loading={loading} />
      <Modal title="新增知识文档" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="source" label="来源" initialValue="manual">
            <Select options={[{ label: '手动', value: 'manual' }, { label: '导入', value: 'import' }]} />
          </Form.Item>
          <Form.Item name="content" label="内容" rules={[{ required: true }]}>
            <Input.TextArea rows={6} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default KnowledgeBase;
