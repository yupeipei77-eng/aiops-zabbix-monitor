import React from 'react';
import { Spin } from 'antd';

interface Props {
  tip?: string;
}

const LoadingState: React.FC<Props> = ({ tip = '加载中...' }) => (
  <div style={{ textAlign: 'center', padding: 40 }}>
    <Spin tip={tip} size="large" />
  </div>
);

export default LoadingState;
