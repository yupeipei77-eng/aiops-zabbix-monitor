import dayjs from 'dayjs';

export function formatDateTime(val: string | null | undefined): string {
  if (!val) return '-';
  return dayjs(val).format('YYYY-MM-DD HH:mm:ss');
}

export function formatNumber(val: number | null | undefined): string {
  if (val == null) return '0';
  return val.toLocaleString();
}
