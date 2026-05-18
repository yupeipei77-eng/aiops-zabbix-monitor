import React from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  AlertOutlined,
  RobotOutlined,
  BookOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/alerts', icon: <AlertOutlined />, label: '告警列表' },
  { key: '/ai-analysis', icon: <RobotOutlined />, label: 'AI 分析' },
  { key: '/knowledge', icon: <BookOutlined />, label: '知识库' },
  { key: '/reports', icon: <FileTextOutlined />, label: '日报' },
  { key: '/settings', icon: <SettingOutlined />, label: '设置' },
];

const LayoutShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} theme="dark">
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 16, fontWeight: 'bold' }}>
          AIOps Monitor
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0', display: 'flex', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: 18 }}>Zabbix + AI 智能运维监控平台</h2>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: '#fff', borderRadius: 8, minHeight: 360 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default LayoutShell;
