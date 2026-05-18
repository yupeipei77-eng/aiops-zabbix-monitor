import client from './client';
import type { AIAnalysis } from '../types/ai';
import type { PaginatedData } from '../types/common';

export async function fetchAnalyses(page = 1, pageSize = 20) {
  const resp = await client.get<PaginatedData<AIAnalysis>>('/ai', { params: { page, page_size: pageSize } });
  return resp.data;
}

export async function fetchAnalysisForAlert(alertId: number) {
  const resp = await client.get<{ success: boolean; data: AIAnalysis | null; message: string }>(`/ai/alerts/${alertId}`);
  return resp.data;
}
