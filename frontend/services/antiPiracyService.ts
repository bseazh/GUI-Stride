// 反盗版系统API服务
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 类型定义
export interface PatrolParams {
  platform: string; // xiaohongshu/xianyu/taobao
  keyword: string;
  max_items: number;
  test_mode: boolean;
  device_id?: string;
  device_type?: string;
}

export interface DetectionResult {
  title: string;
  shop_name: string;
  price: number;
  is_piracy: boolean;
  confidence: number;
  reasons: string[];
  report_status?: string;
}

export interface PatrolResult {
  checked_count: number;
  piracy_count: number;
  reported_count: number;
  details: DetectionResult[];
  start_time: string;
  end_time?: string;
  error_message?: string;
}

export interface PatrolTask {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  params: PatrolParams;
  result?: PatrolResult;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface PlatformInfo {
  key: string;
  name: string;
  description: string;
  supported: boolean;
}

export interface DeviceStatus {
  connected: boolean;
  device_id?: string;
  device_type?: string;
  status_message: string;
}

export interface DatabaseStats {
  total_products: number;
  platforms: Record<string, number>;
  categories: Record<string, number>;
}

export interface ReportStatistics {
  total_reports: number;
  successful_reports: number;
  failed_reports: number;
  pending_reports: number;
  by_platform: Record<string, number>;
  by_status: Record<string, number>;
  last_7_days: Array<{ date: string; count: number }>;
}

class AntiPiracyService {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || API_BASE_URL;
  }

  // 巡查任务API
  async startPatrol(params: PatrolParams): Promise<PatrolTask> {
    const response = await fetch(`${this.baseUrl}/api/patrol/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '启动巡查失败');
    }

    return response.json();
  }

  async getTaskStatus(taskId: string): Promise<PatrolTask> {
    const response = await fetch(`${this.baseUrl}/api/patrol/${taskId}`);
    if (!response.ok) {
      throw new Error('获取任务状态失败');
    }
    return response.json();
  }

  async getTaskHistory(limit: number = 20): Promise<PatrolTask[]> {
    const response = await fetch(`${this.baseUrl}/api/patrol/?limit=${limit}`);
    if (!response.ok) {
      throw new Error('获取任务历史失败');
    }
    return response.json();
  }

  async cancelTask(taskId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/patrol/${taskId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('取消任务失败');
    }
  }

  // 配置API
  async getSupportedPlatforms(): Promise<PlatformInfo[]> {
    const response = await fetch(`${this.baseUrl}/api/config/platforms`);
    if (!response.ok) {
      throw new Error('获取平台列表失败');
    }
    return response.json();
  }

  async getDeviceStatus(): Promise<DeviceStatus> {
    const response = await fetch(`${this.baseUrl}/api/config/device/status`);
    if (!response.ok) {
      throw new Error('获取设备状态失败');
    }
    return response.json();
  }

  async getSystemConfig(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/config/system`);
    if (!response.ok) {
      throw new Error('获取系统配置失败');
    }
    return response.json();
  }

  // 数据库API
  async getDatabaseStats(): Promise<DatabaseStats> {
    const response = await fetch(`${this.baseUrl}/api/database/stats`);
    if (!response.ok) {
      throw new Error('获取数据库统计失败');
    }
    return response.json();
  }

  // 举报API
  async getReportStatistics(): Promise<ReportStatistics> {
    const response = await fetch(`${this.baseUrl}/api/reports/statistics`);
    if (!response.ok) {
      throw new Error('获取举报统计失败');
    }
    return response.json();
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    if (!response.ok) {
      throw new Error('服务健康检查失败');
    }
    return response.json();
  }

  // 轮询任务状态直到完成
  async pollTaskUntilComplete(
    taskId: string,
    interval: number = 2000,
    timeout: number = 300000 // 5分钟超时
  ): Promise<PatrolTask> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const task = await this.getTaskStatus(taskId);

      if (task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
        return task;
      }

      // 等待指定间隔
      await new Promise(resolve => setTimeout(resolve, interval));
    }

    throw new Error('任务轮询超时');
  }
}

// 创建单例实例
export const antiPiracyService = new AntiPiracyService();

export default AntiPiracyService;