import React from 'react';
import { Card, Statistic } from 'antd';

interface Props {
  title: string;
  value: number;
  suffix?: string;
  color?: string;
}

const MetricCard: React.FC<Props> = ({ title, value, suffix, color }) => (
  <Card>
    <Statistic title={title} value={value} suffix={suffix} valueStyle={{ color }} />
  </Card>
);

export default MetricCard;
