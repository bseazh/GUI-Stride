import React, { useState, useEffect } from 'react';
import { Search, Loader2, AlertCircle, CheckCircle, XCircle, Database, BarChart3, Settings, Smartphone, Play, History } from 'lucide-react';
import './index.css';

// 类型定义
interface PatrolTask {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  params: {
    platform: string;
    keyword: string;
    max_items: number;
    test_mode: boolean;
  };
  progress: number;
  result?: {
    checked_count: number;
    piracy_count: number;
    reported_count: number;
    details: Array<{
      title: string;
      shop_name: string;
      price: number;
      is_piracy: boolean;
      confidence: number;
      reasons: string[];
      report_status?: string;
    }>;
  };
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

interface PlatformInfo {
  key: string;
  name: string;
  description: string;
  supported: boolean;
}

interface DeviceStatus {
  connected: boolean;
  device_id?: string;
  device_type?: string;
  status_message: string;
}

const App: React.FC = () => {
  // 平台选择
  const [platform, setPlatform] = useState<string>('xiaohongshu');
  const [platforms, setPlatforms] = useState<PlatformInfo[]>([
    { key: 'xiaohongshu', name: '小红书', description: '小红书电商平台', supported: true },
    { key: 'xianyu', name: '闲鱼', description: '闲鱼二手交易平台', supported: true },
    { key: 'taobao', name: '淘宝', description: '淘宝电商平台', supported: true }
  ]);

  // 巡查参数
  const [keyword, setKeyword] = useState<string>('众合法考');
  const [maxItems, setMaxItems] = useState<number>(10);
  const [testMode, setTestMode] = useState<boolean>(true);

  // 设备状态
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatus>({
    connected: false,
    status_message: '正在检测设备...'
  });

  // 任务状态
  const [currentTask, setCurrentTask] = useState<PatrolTask | null>(null);
  const [isStarting, setIsStarting] = useState<boolean>(false);
  const [taskHistory, setTaskHistory] = useState<PatrolTask[]>([]);

  // 系统配置
  const [apiBaseUrl, setApiBaseUrl] = useState<string>('http://localhost:8000');

  // 加载平台列表
  useEffect(() => {
    fetchPlatforms();
    checkDeviceStatus();
    fetchTaskHistory();
  }, []);

  // 轮询任务状态
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (currentTask && currentTask.status === 'running') {
      interval = setInterval(() => {
        fetchTaskStatus(currentTask.task_id);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [currentTask]);

  const fetchPlatforms = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/config/platforms`);
      if (response.ok) {
        const data = await response.json();
        setPlatforms(data);
      }
    } catch (error) {
      console.error('获取平台列表失败:', error);
    }
  };

  const checkDeviceStatus = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/config/device/status`);
      if (response.ok) {
        const data = await response.json();
        setDeviceStatus(data);
      }
    } catch (error) {
      console.error('检查设备状态失败:', error);
      setDeviceStatus({
        connected: false,
        status_message: '设备连接检查失败，请检查后端服务'
      });
    }
  };

  const fetchTaskHistory = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/patrol/?limit=10`);
      if (response.ok) {
        const data = await response.json();
        setTaskHistory(data);
      }
    } catch (error) {
      console.error('获取任务历史失败:', error);
    }
  };

  const fetchTaskStatus = async (taskId: string) => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/patrol/${taskId}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentTask(data);
        if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
          fetchTaskHistory(); // 刷新历史记录
        }
      }
    } catch (error) {
      console.error('获取任务状态失败:', error);
    }
  };

  const startPatrol = async () => {
    if (!keyword.trim()) {
      alert('请输入搜索关键词');
      return;
    }

    setIsStarting(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/patrol/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform,
          keyword,
          max_items: maxItems,
          test_mode: testMode,
          device_type: 'adb'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentTask(data);
        setTaskHistory(prev => [data, ...prev]);
      } else {
        const error = await response.json();
        alert(`启动失败: ${error.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('启动巡查失败:', error);
      alert('启动巡查失败，请检查后端服务是否运行');
    } finally {
      setIsStarting(false);
    }
  };

  const cancelTask = async (taskId: string) => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/patrol/${taskId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchTaskStatus(taskId);
      } else {
        alert('取消任务失败');
      }
    } catch (error) {
      console.error('取消任务失败:', error);
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'running': return 'text-blue-600 bg-blue-50';
      case 'failed': return 'text-red-600 bg-red-50';
      case 'cancelled': return 'text-gray-600 bg-gray-50';
      default: return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'running': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'failed': return <XCircle className="w-4 h-4" />;
      case 'cancelled': return <XCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Search className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">反盗版自动巡查系统</h1>
                <p className="text-sm text-gray-500">智能版权保护控制面板</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${deviceStatus.connected ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                <Smartphone className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {deviceStatus.connected ? '设备已连接' : '设备未连接'}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                API: {apiBaseUrl}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧控制面板 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 平台选择 */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                选择目标平台
              </h2>
              <div className="grid grid-cols-3 gap-3">
                {platforms.map((p) => (
                  <button
                    key={p.key}
                    onClick={() => setPlatform(p.key)}
                    className={`p-4 rounded-lg border-2 transition-all ${platform === p.key
                        ? 'border-blue-600 bg-blue-50 text-blue-700 shadow-md'
                        : 'border-gray-200 bg-gray-50 text-gray-700 hover:border-gray-300'
                      }`}
                  >
                    <div className="font-medium">{p.name}</div>
                    <div className="text-xs text-gray-500 mt-1">{p.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* 巡查参数配置 */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <Search className="w-5 h-5 mr-2" />
                巡查参数配置
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    搜索关键词
                  </label>
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="例如：众合法考、得到课程"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      最大检查商品数
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={maxItems}
                      onChange={(e) => setMaxItems(parseInt(e.target.value) || 10)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      运行模式
                    </label>
                    <div className="flex items-center space-x-3">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          checked={testMode}
                          onChange={() => setTestMode(true)}
                          className="mr-2"
                        />
                        <span className="text-sm">测试模式</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          checked={!testMode}
                          onChange={() => setTestMode(false)}
                          className="mr-2"
                        />
                        <span className="text-sm">正式模式</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t">
                <button
                  onClick={startPatrol}
                  disabled={isStarting || !deviceStatus.connected}
                  className={`w-full py-3 px-6 rounded-lg font-medium text-white flex items-center justify-center ${!deviceStatus.connected
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                >
                  {isStarting ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      正在启动巡查...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      开始自动巡查
                    </>
                  )}
                </button>
                {!deviceStatus.connected && (
                  <p className="mt-2 text-sm text-red-600 text-center">
                    设备未连接，请先连接设备
                  </p>
                )}
              </div>
            </div>

            {/* 当前任务状态 */}
            {currentTask && (
              <div className="bg-white rounded-xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center">
                  <Loader2 className="w-5 h-5 mr-2" />
                  当前巡查任务
                </h2>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">任务ID: {currentTask.task_id}</div>
                      <div className="text-sm text-gray-500">
                        创建时间: {formatDateTime(currentTask.created_at)}
                      </div>
                    </div>
                    <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${getStatusColor(currentTask.status)}`}>
                      {getStatusIcon(currentTask.status)}
                      <span className="text-sm font-medium capitalize">{currentTask.status}</span>
                    </div>
                  </div>

                  {currentTask.status === 'running' && (
                    <div>
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>执行进度</span>
                        <span>{Math.round(currentTask.progress * 100)}%</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-600 transition-all duration-300"
                          style={{ width: `${currentTask.progress * 100}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {currentTask.status === 'running' && (
                    <div className="text-center">
                      <button
                        onClick={() => cancelTask(currentTask.task_id)}
                        className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
                      >
                        取消任务
                      </button>
                    </div>
                  )}

                  {currentTask.result && (
                    <div className="pt-4 border-t">
                      <h3 className="font-medium mb-2">巡查结果</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-blue-700">
                            {currentTask.result.checked_count}
                          </div>
                          <div className="text-sm text-blue-600">检查商品</div>
                        </div>
                        <div className="bg-red-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-red-700">
                            {currentTask.result.piracy_count}
                          </div>
                          <div className="text-sm text-red-600">发现盗版</div>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-green-700">
                            {currentTask.result.reported_count}
                          </div>
                          <div className="text-sm text-green-600">成功举报</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {currentTask.error_message && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="text-sm text-red-700">
                        错误: {currentTask.error_message}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* 右侧信息面板 */}
          <div className="space-y-6">
            {/* 设备状态 */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <Smartphone className="w-5 h-5 mr-2" />
                设备状态
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">连接状态</span>
                  <span className={`font-medium ${deviceStatus.connected ? 'text-green-600' : 'text-red-600'}`}>
                    {deviceStatus.connected ? '已连接' : '未连接'}
                  </span>
                </div>
                {deviceStatus.device_id && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">设备ID</span>
                    <span className="font-mono text-sm">{deviceStatus.device_id}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">设备类型</span>
                  <span>{deviceStatus.device_type || '未知'}</span>
                </div>
                <div className="text-sm text-gray-500">
                  {deviceStatus.status_message}
                </div>
                <button
                  onClick={checkDeviceStatus}
                  className="w-full mt-2 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  刷新设备状态
                </button>
              </div>
            </div>

            {/* 任务历史 */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <History className="w-5 h-5 mr-2" />
                最近任务
              </h2>
              <div className="space-y-3">
                {taskHistory.slice(0, 5).map((task) => (
                  <div
                    key={task.task_id}
                    className="p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium text-sm truncate">
                          {task.params.keyword}
                        </div>
                        <div className="text-xs text-gray-500">
                          {task.params.platform} • {task.params.max_items}个商品
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(task.status)}`}>
                        {task.status}
                      </div>
                    </div>
                    {task.result && (
                      <div className="mt-2 grid grid-cols-3 gap-1 text-xs">
                        <div className="text-center">
                          <div className="font-bold">{task.result.checked_count}</div>
                          <div className="text-gray-500">检查</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold">{task.result.piracy_count}</div>
                          <div className="text-gray-500">盗版</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold">{task.result.reported_count}</div>
                          <div className="text-gray-500">举报</div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                {taskHistory.length === 0 && (
                  <div className="text-center py-4 text-gray-500">
                    暂无任务记录
                  </div>
                )}
                {taskHistory.length > 5 && (
                  <button
                    onClick={fetchTaskHistory}
                    className="w-full mt-2 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    查看更多任务
                  </button>
                )}
              </div>
            </div>

            {/* 系统信息 */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                系统信息
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">后端API</span>
                  <span className="font-mono text-sm">{apiBaseUrl}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">前端版本</span>
                  <span>v1.0.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">支持平台</span>
                  <span>{platforms.filter(p => p.supported).length}个</span>
                </div>
                <button
                  onClick={fetchPlatforms}
                  className="w-full mt-2 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  刷新系统信息
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="mt-8 py-4 border-t bg-white">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          <p>反盗版自动巡查系统 © 2025 - 基于 Open-AutoGLM 构建</p>
          <p className="mt-1">注意：请遵守相关法律法规，仅用于合法版权保护用途</p>
        </div>
      </footer>
    </div>
  );
};

export default App;