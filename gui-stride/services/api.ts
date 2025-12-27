// 与 Electron 主进程通信的 API 服务

const { ipcRenderer } = window.require('electron');

export interface PatrolOptions {
  platform: string;
  keyword: string;
  maxItems: number;
  testMode: boolean;
  deviceId?: string;
}

export interface ProductData {
  product_id?: string;
  product_name: string;
  shop_name: string;
  official_shops: string[];
  original_price: number;
  platform: string;
  category: string;
  description?: string;
  keywords: string[];
}

export interface PythonLog {
  type: 'info' | 'output' | 'error' | 'warning';
  message: string;
  timestamp?: number;
}

// 启动巡查任务
export function startPatrol(options: PatrolOptions): void {
  ipcRenderer.send('start-patrol', options);
}

// 停止巡查任务
export function stopPatrol(): void {
  ipcRenderer.send('stop-patrol');
}

// 获取正版商品数据库
export async function getProductDatabase(): Promise<Record<string, any>> {
  return await ipcRenderer.invoke('get-product-database');
}

// 添加正版商品
export async function addProduct(productData: ProductData): Promise<{ success: boolean; productId?: string; error?: string }> {
  return await ipcRenderer.invoke('add-product', productData);
}

// 删除正版商品
export async function deleteProduct(productId: string): Promise<{ success: boolean; error?: string }> {
  return await ipcRenderer.invoke('delete-product', productId);
}

// 检查进程状态
export async function checkProcessStatus(): Promise<{ running: boolean }> {
  return await ipcRenderer.invoke('check-process-status');
}

// 监听 Python 日志
export function onPythonLog(callback: (log: PythonLog) => void): () => void {
  const handler = (event: any, log: PythonLog) => {
    callback({
      ...log,
      timestamp: Date.now()
    });
  };

  ipcRenderer.on('python-log', handler);

  // 返回清理函数
  return () => {
    ipcRenderer.removeListener('python-log', handler);
  };
}

// 类型定义
export interface ReportRecord {
  report_id: string;
  platform: string;
  target_title: string;
  target_shop: string;
  target_price: number;
  target_url?: string;
  detection_result?: any;
  report_reason: string;
  report_status: string;
  evidence_screenshots: string[];
  reported_at: string;
  notes?: string;
}

export interface Statistics {
  product_stats: {
    total_products: number;
    platforms: Record<string, number>;
    categories: Record<string, number>;
  };
  report_stats: {
    total_reports: number;
    by_platform: Record<string, number>;
    by_status: Record<string, number>;
  };
}

export interface SystemConfig {
  platforms: Record<string, { name: string; enabled: boolean }>;
}

export interface ExportResult {
  success: boolean;
  data?: string;
  format?: string;
  path?: string;
  error?: string;
}

// 获取举报记录数据库
export async function getReportDatabase(): Promise<Record<string, ReportRecord>> {
  return await ipcRenderer.invoke('get-report-database');
}

// 获取系统统计信息
export async function getStatistics(): Promise<Statistics> {
  return await ipcRenderer.invoke('get-statistics');
}

// 导出举报记录
export async function exportReports(format: 'json' | 'txt' = 'json', outputPath?: string): Promise<ExportResult> {
  return await ipcRenderer.invoke('export-reports', { format, outputPath });
}

// 获取系统配置
export async function getSystemConfig(): Promise<SystemConfig> {
  return await ipcRenderer.invoke('get-system-config');
}