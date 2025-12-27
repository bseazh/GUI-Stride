import { Merchant, LogEntry, ReportRecord, WhitelistEntry } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PatrolRequest {
  platform: string;
  keyword: string;
  max_items: number;
  test_mode: boolean;
}

export interface PatrolResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface PatrolStatus {
  task_id: string;
  status: string;
  started_at: string;
  result: {
    checked_count: number;
    piracy_count: number;
    reported_count: number;
  } | null;
}

export interface SystemStats {
  total_merchants: number;
  pirated_count: number;
  official_count: number;
  total_reports: number;
  total_loss_prevented: number;
}

/**
 * Fetch merchants from backend API
 */
export async function fetchMerchants(platform?: string, limit: number = 20): Promise<Merchant[]> {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (platform) params.append('platform', platform);

  const response = await fetch(`${API_BASE_URL}/api/merchants?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch merchants: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch logs from backend API
 */
export async function fetchLogs(limit: number = 50): Promise<LogEntry[]> {
  const response = await fetch(`${API_BASE_URL}/api/logs?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch logs: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch reports from backend API
 */
export async function fetchReports(limit: number = 50): Promise<ReportRecord[]> {
  const response = await fetch(`${API_BASE_URL}/api/reports?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch reports: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Start a new patrol task
 */
export async function startPatrol(request: PatrolRequest): Promise<PatrolResponse> {
  const response = await fetch(`${API_BASE_URL}/api/patrol`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to start patrol: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get patrol task status
 */
export async function getPatrolStatus(taskId: string): Promise<PatrolStatus> {
  const response = await fetch(`${API_BASE_URL}/api/patrol/${taskId}`);
  if (!response.ok) {
    throw new Error(`Failed to get patrol status: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get supported platforms
 */
export async function getPlatforms(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/platforms`);
  if (!response.ok) {
    throw new Error(`Failed to get platforms: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get system statistics
 */
export async function getSystemStats(): Promise<SystemStats> {
  const response = await fetch(`${API_BASE_URL}/api/stats`);
  if (!response.ok) {
    throw new Error(`Failed to get system stats: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Add a whitelist entry (mock for now)
 */
export async function addWhitelistEntry(entry: WhitelistEntry): Promise<void> {
  // TODO: Implement actual API endpoint
  console.log('Adding whitelist entry:', entry);
  await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
}

/**
 * Delete a whitelist entry (mock for now)
 */
export async function deleteWhitelistEntry(id: string): Promise<void> {
  // TODO: Implement actual API endpoint
  console.log('Deleting whitelist entry:', id);
  await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
}

/**
 * Fetch whitelist entries (mock for now)
 */
export async function fetchWhitelist(): Promise<WhitelistEntry[]> {
  // TODO: Implement actual API endpoint
  await new Promise(resolve => setTimeout(resolve, 300)); // Simulate API call
  return [
    { id: '1', officialMerchantName: '官方出版社', productName: '2025法考全套资料', price: '299', allowedShops: ['官方旗舰店', '正版分销商'] }
  ];
}

/**
 * Get patrol task logs
 */
export async function getPatrolLogs(taskId: string, since: number = 0): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/patrol/${taskId}/logs?since=${since}`);
  if (!response.ok) {
    throw new Error(`Failed to get patrol logs: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get new patrol task logs (for real-time polling)
 */
export async function getNewPatrolLogs(taskId: string): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/patrol/${taskId}/logs/new`);
  if (!response.ok) {
    throw new Error(`Failed to get new patrol logs: ${response.statusText}`);
  }
  return response.json();
}