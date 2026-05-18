import React from 'react';
import { Tag } from 'antd';
import { getSeverityConfig } from '../utils/severity';

interface Props {
  severity: number;
}

const AlertSeverityTag: React.FC<Props> = ({ severity }) => {
  const config = getSeverityConfig(severity);
  return <Tag color={config.color}>{config.label}</Tag>;
};

export default AlertSeverityTag;
