export interface AIAnalysis {
  id: number;
  alert_id: number;
  summary: string;
  possible_causes: string;
  suggested_actions: string;
  risk_level: string;
  confidence: number;
  need_human_confirm: boolean;
  model_used: string;
  prompt: string;
  raw_response: string;
  latency_ms: number;
  created_at: string;
}
