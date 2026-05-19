import client from './client';
import type { Alert, AlertListParams } from '../types/alert';
import type { PaginatedData } from '../types/common';

export interface AnalyzeAlertRequest {
  provider?: string;
  model?: string;
  force?: boolean;
}

export interface AnalyzeAlertResponse {
  id?: number;
  alert_id: number;
  summary?: string;
  possible_causes?: string[];
  suggested_actions?: string[];
  risk_level?: string;
  confidence?: number;
  need_human_confirm?: boolean;
  model_used?: string;
  ai_analysis_skipped?: boolean;
  skipped_reason?: string;
}

export async function fetchAlerts(params?: AlertListParams) {
  const resp = await client.get<PaginatedData<Alert>>('/alerts', { params });
  return resp.data;
}

export async function fetchAlert(id: number) {
  const resp = await client.get<{ success: boolean; data: Alert; message: string }>(`/alerts/${id}`);
  return resp.data;
}

export async function analyzeAlert(id: number, body: AnalyzeAlertRequest = {}) {
  const resp = await client.post<{ success: boolean; data: AnalyzeAlertResponse | null; message: string }>(
    `/ai/${id}/analyze`,
    body
  );
  return resp.data;
}
