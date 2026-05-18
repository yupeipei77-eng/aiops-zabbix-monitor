const SEVERITY_CONFIG: Record<number, { label: string; color: string }> = {
  0: { label: '未分类', color: 'default' },
  1: { label: '信息', color: 'blue' },
  2: { label: '警告', color: 'orange' },
  3: { label: '一般', color: 'gold' },
  4: { label: '严重', color: 'red' },
  5: { label: '灾难', color: 'magenta' },
};

export function getSeverityConfig(severity: number) {
  return SEVERITY_CONFIG[severity] || SEVERITY_CONFIG[0];
}

export function getSeverityColor(severity: number): string {
  return getSeverityConfig(severity).color;
}

export function getSeverityLabel(severity: number): string {
  return getSeverityConfig(severity).label;
}
