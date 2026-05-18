export interface ApiResponse<T = unknown> {
  success: boolean;
  data: T;
  message: string;
}

export interface PaginatedData<T = unknown> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  page_size: number;
  message: string;
}

export interface DashboardSummary {
  total_alerts: number;
  unresolved_alerts: number;
  critical_alerts: number;
  ai_analysis_count: number;
  token_usage: number;
}

export interface DailyReport {
  date: string;
  total_alerts: number;
  unresolved_alerts: number;
  critical_alerts: number;
  ai_analysis_count: number;
  token_usage: number;
  severity_distribution: Record<string, number>;
  hourly_trend: Array<{ hour: number; count: number }>;
}
