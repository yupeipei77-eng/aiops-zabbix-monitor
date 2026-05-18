import client from './client';
import type { DashboardSummary, DailyReport } from '../types/common';

export async function fetchDashboardSummary() {
  const resp = await client.get<{ success: boolean; data: DashboardSummary; message: string }>('/reports/dashboard');
  return resp.data;
}

export async function fetchDailyReport(date?: string) {
  const resp = await client.get<{ success: boolean; data: DailyReport; message: string }>('/reports/daily', { params: { date } });
  return resp.data;
}
