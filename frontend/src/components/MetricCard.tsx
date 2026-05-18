import React from 'react';
import { Card, Statistic } from 'antd';
import type { Color } from 'antd/es/color-picker';

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
