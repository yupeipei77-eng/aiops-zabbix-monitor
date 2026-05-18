import client from './client';
import type { Alert, AlertListParams } from '../types/alert';
import type { PaginatedData } from '../types/common';

export async function fetchAlerts(params?: AlertListParams) {
  const resp = await client.get<PaginatedData<Alert>>('/alerts', { params });
  return resp.data;
}

export async function fetchAlert(id: number) {
  const resp = await client.get<{ success: boolean; data: Alert; message: string }>(`/alerts/${id}`);
  return resp.data;
}

export async function analyzeAlert(id: number, provider?: string) {
  const resp = await client.post(`/ai/${id}/analyze`, { provider });
  return resp.data;
}
