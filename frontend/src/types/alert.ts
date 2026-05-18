export interface Alert {
  id: number;
  source: string;
  event_id: string;
  trigger_id: string;
  trigger_name: string;
  host_id: string;
  host_name: string;
  host_ip: string;
  severity: number;
  severity_label: string;
  item_key: string;
  item_value: string;
  message: string;
  tags: Record<string, unknown>;
  raw_payload: Record<string, unknown>;
  is_recovery: boolean;
  dedup_key: string;
  dedup_count: number;
  storm_detected: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertListParams {
  page?: number;
  page_size?: number;
  severity?: number;
  host_name?: string;
}
