
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  LayoutDashboard,
  ShieldCheck,
  Settings,
  Terminal,
  Plus,
  Trash2,
  User,
  Monitor,
  Play,
  FileSpreadsheet,
  Activity,
  Zap,
  X,
  SlidersHorizontal,
  Tags,
  Info,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  ArrowUpRight,
  StopCircle,
  RefreshCw
} from 'lucide-react';
import { Merchant, LogEntry, WhitelistEntry, ReportRecord } from './types';
import { MOCK_MERCHANTS, INITIAL_LOGS, MOCK_REPORTS } from './constants';
import { MerchantCard } from './components/MerchantCard';
import { PhoneMockup } from './components/PhoneMockup';
import { startPatrol, stopPatrol, getProductDatabase, addProduct, deleteProduct, checkProcessStatus, onPythonLog, getStatistics, exportReports, type PatrolOptions, type ProductData, type Statistics } from './services/api';

type ViewType = 'terminal' | 'summary' | 'settings';

const AUDIT_KEYWORDS = [
  "正版", "授权", "官方", "旗舰店", "全套", "考研", "法考", "公考", "PDF", "电子版", 
  "网盘", "秒发", "引流", "微信", "私聊", "低价", "正品", "出版社", "水印", "盗版", 
  "翻印", "扫描", "讲义", "真题", "解析", "押题", "专柜", "代购", "包邮", "原装"
];

const App: React.FC = () => {
  const [activeView, setActiveView] = useState<ViewType>('terminal');
  const [merchants] = useState<Merchant[]>(MOCK_MERCHANTS);
  const [selectedMerchant, setSelectedMerchant] = useState<Merchant | null>(MOCK_MERCHANTS[0]);
  const [logs, setLogs] = useState<LogEntry[]>(INITIAL_LOGS);
  const [platform, setPlatform] = useState<'xiaohongshu' | 'xianyu' | 'taobao'>('xiaohongshu');
  const [searchCount, setSearchCount] = useState<number>(20);
  const [showConfig, setShowConfig] = useState(false);
  const [testMode, setTestMode] = useState<boolean>(true);
  const [isProcessRunning, setIsProcessRunning] = useState<boolean>(false);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [keyword, setKeyword] = useState<string>('得到');

  const [whitelist, setWhitelist] = useState<WhitelistEntry[]>([
    { id: '1', officialMerchantName: '官方出版社', productName: '2025法考全套资料', price: '299', allowedShops: ['官方旗舰店', '正版分销商'] }
  ]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set(['1']));

  const [leftWidth, setLeftWidth] = useState(380);
  const [rightWidth, setRightWidth] = useState(680);
  const [isResizingLeft, setIsResizingLeft] = useState(false);
  const [isResizingRight, setIsResizingRight] = useState(false);

  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isResizingLeft) {
      const newWidth = e.clientX - 80;
      if (newWidth > 300 && newWidth < 600) setLeftWidth(newWidth);
    }
    if (isResizingRight) {
      const newWidth = window.innerWidth - e.clientX;
      if (newWidth > 450 && newWidth < 950) setRightWidth(newWidth);
    }
  }, [isResizingLeft, isResizingRight]);

  const stopResizing = useCallback(() => {
    setIsResizingLeft(false);
    setIsResizingRight(false);
  }, []);

  useEffect(() => {
    if (isResizingLeft || isResizingRight) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', stopResizing);
    } else {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', stopResizing);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', stopResizing);
    };
  }, [isResizingLeft, isResizingRight, handleMouseMove, stopResizing]);

  // 监听 Python 进程日志
  useEffect(() => {
    const cleanup = onPythonLog((log) => {
      const logType = log.type === 'error' ? 'performance' :
                     log.type === 'warning' ? 'performance' : 'info';

      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: logType,
        message: `[Python] ${log.message}`
      }]);

      // 更新进程状态
      if (log.message.includes('进程退出') || log.message.includes('启动失败')) {
        setIsProcessRunning(false);
      } else if (log.message.includes('启动 Python 进程')) {
        setIsProcessRunning(true);
      }
    });

    // 检查当前进程状态
    checkProcessStatus().then(status => {
      setIsProcessRunning(status.running);
    });

    // 加载数据库
    loadProductDatabase();

    // 加载统计信息
    loadStatistics();

    return cleanup;
  }, []);

  // 加载统计信息
  const loadStatistics = async () => {
    try {
      const stats = await getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('加载统计信息失败:', error);
    }
  };

  // 加载正版商品数据库
  const loadProductDatabase = async () => {
    try {
      const db = await getProductDatabase();
      const entries: WhitelistEntry[] = Object.values(db).map((product: any) => ({
        id: product.product_id,
        officialMerchantName: product.shop_name,
        productName: product.product_name,
        price: product.original_price.toString(),
        allowedShops: product.official_shops || []
      }));
      setWhitelist(entries);
    } catch (error) {
      console.error('加载数据库失败:', error);
    }
  };

  const addWhitelistRow = () => {
    const newEntry: WhitelistEntry = {
      id: Math.random().toString(36).substr(2, 9),
      officialMerchantName: '',
      productName: '',
      price: '',
      allowedShops: []
    };
    setWhitelist([...whitelist, newEntry]);
  };

  const updateWhitelist = (id: string, field: keyof WhitelistEntry, value: any) => {
    setWhitelist(whitelist.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const removeWhitelistRow = async (id: string) => {
    try {
      const result = await deleteProduct(id);
      if (result.success) {
        setWhitelist(whitelist.filter(item => item.id !== id));
        const next = new Set(selectedIds);
        next.delete(id);
        setSelectedIds(next);
        setLogs(prev => [...prev, {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString(),
          type: 'info',
          message: `已从数据库删除商品: ${id}`
        }]);
      } else {
        setLogs(prev => [...prev, {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString(),
          type: 'performance',
          message: `删除商品失败: ${result.error}`
        }]);
      }
    } catch (error) {
      console.error('删除商品失败:', error);
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'performance',
        message: `删除商品时出错: ${error}`
      }]);
    }
  };

  const toggleSelect = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  };

  const handleStartSearch = () => {
    if (isProcessRunning) {
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'performance',
        message: '已有任务正在运行，请等待完成或停止当前任务。'
      }]);
      return;
    }

    const activeRows = whitelist.filter(row => selectedIds.has(row.id));
    if (activeRows.length === 0) {
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'performance',
        message: '操作中断: 请在对照表中勾选需要执行的任务。'
      }]);
      return;
    }

    // 使用第一个选中的白名单项作为关键词（实际应该使用所有，这里简化）
    const firstRow = activeRows[0];
    const searchKeyword = firstRow.productName || keyword;

    const options: PatrolOptions = {
      platform: platform,
      keyword: searchKeyword,
      maxItems: searchCount,
      testMode: testMode
    };

    setLogs(prev => [...prev, {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      type: 'action',
      message: `[EXE] 启动 Python 巡查: 平台=${platform}, 关键词="${searchKeyword}", 数量=${searchCount}, 模式=${testMode ? '测试' : '正式'}`
    }]);

    startPatrol(options);
    setIsProcessRunning(true);
  };

  const handleStopSearch = () => {
    if (!isProcessRunning) {
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'performance',
        message: '没有正在运行的任务。'
      }]);
      return;
    }

    stopPatrol();
    setLogs(prev => [...prev, {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      type: 'action',
      message: '[EXE] 停止当前巡查任务'
    }]);
    setIsProcessRunning(false);
  };

  const renderSummary = () => (
    <div className="flex-1 bg-slate-50 p-10 overflow-y-auto scrollbar-thin animate-in fade-in duration-500">
      <div className="max-w-7xl mx-auto space-y-10">
        <div className="flex items-end justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-black text-indigo-600 uppercase tracking-widest mb-1">
              <Activity size={14} /> Data Visualization Center
            </div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">数据大屏</h1>
            <p className="text-slate-400 font-bold text-xs uppercase tracking-widest mt-1">系统全量监控与防护统计</p>
          </div>
          <div className="flex items-center gap-3">
             <div className="bg-white border border-slate-200 px-4 py-2 rounded-xl shadow-sm flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">System Online</span>
             </div>
             <button
               onClick={async () => {
                 try {
                   const result = await exportReports('json');
                   if (result.success && result.data) {
                     const blob = new Blob([result.data], { type: 'application/json' });
                     const url = URL.createObjectURL(blob);
                     const a = document.createElement('a');
                     a.href = url;
                     a.download = `reports_${new Date().toISOString().split('T')[0]}.json`;
                     document.body.appendChild(a);
                     a.click();
                     document.body.removeChild(a);
                     URL.revokeObjectURL(url);

                     setLogs(prev => [...prev, {
                       id: Date.now().toString(),
                       timestamp: new Date().toLocaleTimeString(),
                       type: 'info',
                       message: '举报记录已导出为JSON文件'
                     }]);
                   } else {
                     setLogs(prev => [...prev, {
                       id: Date.now().toString(),
                       timestamp: new Date().toLocaleTimeString(),
                       type: 'performance',
                       message: `导出失败: ${result.error || '未知错误'}`
                     }]);
                   }
                 } catch (error) {
                   console.error('导出失败:', error);
                   setLogs(prev => [...prev, {
                     id: Date.now().toString(),
                     timestamp: new Date().toLocaleTimeString(),
                     type: 'performance',
                     message: `导出出错: ${error}`
                   }]);
                 }
               }}
               className="bg-white border border-slate-200 px-4 py-2 rounded-xl shadow-sm flex items-center gap-2 hover:bg-slate-50 transition-colors"
             >
               <FileSpreadsheet size={14} className="text-slate-600" />
               <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">导出报告</span>
             </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: '正版商品总数', value: statistics ? statistics.product_stats.total_products.toString() : '0', icon: Monitor, color: 'text-blue-600', trend: '' },
            { label: '总举报数量', value: statistics ? statistics.report_stats.total_reports.toString() : '0', icon: AlertTriangle, color: 'text-rose-600', trend: '' },
            { label: '平台分布', value: statistics ? Object.keys(statistics.report_stats.by_platform).length.toString() + '个' : '0个', icon: DollarSign, color: 'text-emerald-600', trend: '' },
            { label: '系统状态', value: isProcessRunning ? '运行中' : '就绪', icon: Zap, color: isProcessRunning ? 'text-emerald-600' : 'text-indigo-600', trend: '' },
          ].map((stat, i) => (
            <div key={i} className="luxoa-card p-6 flex flex-col justify-between">
              <div className="flex items-start justify-between">
                <div className={`p-3 rounded-2xl bg-slate-50 ${stat.color}`}>
                  <stat.icon size={20} />
                </div>
                {stat.trend && <span className="text-[10px] font-black text-emerald-500 bg-emerald-50 px-2 py-0.5 rounded-full">{stat.trend}</span>}
              </div>
              <div className="mt-6">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{stat.label}</p>
                <h3 className="text-2xl font-black text-slate-900">{stat.value}</h3>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 luxoa-card p-8">
            <div className="flex items-center justify-between mb-10">
              <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest flex items-center gap-2">
                <TrendingUp size={16} className="text-indigo-600" /> 7日防护趋势分析
              </h3>
              <div className="flex gap-2">
                 <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
                 <span className="text-[9px] font-black text-slate-400 uppercase">每日拦截数</span>
              </div>
            </div>
            
            <div className="h-64 flex items-end justify-between gap-4">
              {[60, 80, 45, 95, 70, 85, 100].map((h, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-4 group">
                  <div className="w-full bg-slate-50 rounded-xl relative overflow-hidden" style={{ height: '100%' }}>
                    <div 
                      className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-xl transition-all duration-1000 group-hover:from-indigo-500" 
                      style={{ height: `${h}%` }}
                    ></div>
                  </div>
                  <span className="text-[9px] font-black text-slate-400">05-{20+i}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="luxoa-card p-8 bg-white border border-slate-200">
            <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest mb-8 flex items-center gap-2">
              <ShieldCheck size={16} className="text-emerald-500" /> 平台风险分布
            </h3>
            <div className="space-y-6">
              {statistics && Object.keys(statistics.report_stats.by_platform).length > 0 ? (
                (() => {
                  const platformData = statistics.report_stats.by_platform;
                  const total = Object.values(platformData).reduce((sum, val) => sum + val, 0);
                  const colors = ['bg-yellow-500', 'bg-rose-500', 'bg-orange-500', 'bg-slate-600', 'bg-blue-500', 'bg-green-500'];
                  let colorIndex = 0;
                  return Object.entries(platformData).map(([platformName, count], i) => {
                    const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                    const color = colors[colorIndex % colors.length];
                    colorIndex++;
                    return (
                      <div key={i} className="space-y-2">
                        <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                          <span className="text-slate-700">{platformName}</span>
                          <span className="text-slate-400">{percentage}% ({count})</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                          <div className={`h-full ${color}`} style={{ width: `${percentage}%` }}></div>
                        </div>
                      </div>
                    );
                  });
                })()
              ) : (
                <div className="text-center py-4 text-slate-400 text-sm">
                  暂无举报数据
                </div>
              )}
            </div>
            <div className="mt-12 p-5 bg-slate-50 rounded-2xl border border-slate-100">
              <p className="text-[10px] font-bold text-slate-500 leading-relaxed italic">
                “当前闲鱼平台的侵权密度最高，主要集中在法考、考研类目。建议加大关键词‘PDF’、‘秒发’的实时检索频率。”
              </p>
            </div>
          </div>
        </div>

        <div className="luxoa-card overflow-hidden">
          <div className="p-8 border-b border-slate-50 flex items-center justify-between">
             <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest flex items-center gap-2">
                <FileSpreadsheet size={16} className="text-indigo-600" /> 近期维权存证记录
             </h3>
             <button className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1 hover:text-indigo-600 transition-colors">
                查看全量报告 <ArrowUpRight size={14} />
             </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[11px]">
              <thead className="bg-slate-50 text-slate-400 font-black uppercase tracking-widest">
                <tr>
                  <th className="px-8 py-4">单号</th>
                  <th className="px-8 py-4">违规商家</th>
                  <th className="px-8 py-4">涉及商品</th>
                  <th className="px-8 py-4">违规判定理由</th>
                  <th className="px-8 py-4">日期</th>
                  <th className="px-8 py-4">状态</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 text-slate-700 font-medium">
                {MOCK_REPORTS.map((report) => (
                  <tr key={report.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-8 py-5 mono text-indigo-600 font-bold">{report.reportNumber}</td>
                    <td className="px-8 py-5 font-black text-slate-900">{report.merchantName}</td>
                    <td className="px-8 py-5">{report.productName}</td>
                    <td className="px-8 py-5 max-w-xs truncate text-slate-400">{report.reason}</td>
                    <td className="px-8 py-5 text-slate-400">{report.date}</td>
                    <td className="px-8 py-5">
                       <span className="flex items-center gap-1.5 text-emerald-600 font-black">
                         <CheckCircle2 size={14} /> 已提交下架
                       </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTerminal = () => (
    <div className="flex-1 flex overflow-hidden animate-in fade-in duration-300 no-select">
      {/* LEFT SIDEBAR: Split into two independent horizontal sections */}
      <aside 
        className="border-r border-slate-100 bg-white flex flex-col overflow-hidden shrink-0"
        style={{ width: `${leftWidth}px` }}
      >
        {/* TOP SECTION: Queue */}
        <div className="flex-1 flex flex-col p-6 border-b border-slate-50 min-h-0">
          <div className="mb-4">
            <div className="flex items-center gap-2 text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-1">
              <Zap size={14} fill="currentColor" /> MONITORING NODE
            </div>
            <h2 className="text-xl font-black text-slate-900 tracking-tight">监测中心</h2>
          </div>

          <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[11px] font-black text-slate-400 uppercase tracking-widest">已审队列 (滑动手卡)</h3>
              <span className="text-[9px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-black">LIVE</span>
            </div>
            <div className="flex-1 overflow-x-auto overflow-y-hidden pb-4 scrollbar-thin flex gap-4 items-center">
              {merchants.map(m => (
                <MerchantCard 
                  key={m.id} 
                  merchant={m} 
                  isSelected={selectedMerchant?.id === m.id} 
                  onSelect={setSelectedMerchant} 
                />
              ))}
            </div>
          </div>
        </div>

        {/* BOTTOM SECTION: Reasoning + Screenshots */}
        <div className="flex-1 flex flex-col p-6 min-h-0">
          <div className="mb-4">
            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
              <Activity size={14} className="text-indigo-500" /> AI 推理 & 存证截图 (滑动手卡)
            </h3>
          </div>
          
          <div className="flex-1 overflow-x-auto overflow-y-hidden flex gap-4 items-stretch pb-4 scrollbar-thin">
            {/* Reasoning Card */}
            <div className="flex-shrink-0 w-64 luxoa-card p-5 border-indigo-100 bg-indigo-50/20 flex flex-col">
               <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-3">判定链</p>
               {selectedMerchant ? (
                 <p className="text-[12px] leading-relaxed text-slate-700 font-medium italic serif overflow-y-auto">
                   “{selectedMerchant.reasoning}”
                 </p>
               ) : <p className="text-slate-300 italic text-[11px]">等待选择节点...</p>}
            </div>

            {/* Evidence Screenshots */}
            {selectedMerchant?.evidenceImages?.map((img, i) => (
              <div key={i} className="flex-shrink-0 w-64 rounded-2xl bg-slate-100 overflow-hidden border border-slate-200 shadow-sm relative group">
                <img src={img} className="w-full h-full object-cover grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-300" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none"></div>
                <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm px-2 py-0.5 rounded text-[8px] font-black text-slate-900 uppercase">
                  Evidence #{i+1}
                </div>
              </div>
            ))}
          </div>
        </div>
      </aside>

      <div onMouseDown={() => setIsResizingLeft(true)} className={`resizer-v ${isResizingLeft ? 'active' : ''}`} />

      {/* CENTER: Preview */}
      <main className="flex-1 bg-[#F8FAFC] flex items-center justify-center relative overflow-hidden border-r border-slate-100">
        <div className="absolute top-10 flex items-center gap-6 px-6 py-2 bg-white/70 backdrop-blur rounded-full border border-white shadow-sm z-10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-slate-300"></div>
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">放置引导位 (WIRE FRAME)</span>
          </div>
        </div>
        <div className="scale-90"><PhoneMockup /></div>
      </main>

      <div onMouseDown={() => setIsResizingRight(true)} className={`resizer-v ${isResizingRight ? 'active' : ''}`} />

      {/* RIGHT: Audit Table and Operations */}
      <aside 
        className="bg-white flex flex-col p-8 overflow-y-auto scrollbar-thin shrink-0"
        style={{ width: `${rightWidth}px` }}
      >
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center text-white shadow-lg">
              <User size={20} />
            </div>
            <div>
              <h4 className="text-xs font-black text-slate-900 uppercase tracking-tight">AUDITOR · 张三</h4>
              <span className="text-[9px] font-black text-emerald-500 uppercase tracking-[0.2em]">OPERATOR ONLINE</span>
            </div>
          </div>
          <div className="flex p-1 bg-slate-100 rounded-xl w-48 border border-slate-200/50 shadow-inner">
            <button onClick={() => setPlatform('xiaohongshu')} className={`flex-1 py-1.5 text-[9px] font-black rounded-lg transition-all ${platform === 'xiaohongshu' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-400 hover:text-slate-500'}`}>小红书</button>
            <button onClick={() => setPlatform('xianyu')} className={`flex-1 py-1.5 text-[9px] font-black rounded-lg transition-all ${platform === 'xianyu' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-400 hover:text-slate-500'}`}>闲鱼</button>
            <button onClick={() => setPlatform('taobao')} className={`flex-1 py-1.5 text-[9px] font-black rounded-lg transition-all ${platform === 'taobao' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-400 hover:text-slate-500'}`}>淘宝</button>
          </div>
        </div>

        <div className="space-y-8">
          {showConfig && (
            <div className="bg-slate-50 rounded-2xl border border-slate-200 p-6 animate-in slide-in-from-top-4 duration-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[10px] font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
                  <SlidersHorizontal size={14} /> 审计策略配置 (系统预设)
                </h3>
                <button onClick={() => setShowConfig(false)} className="text-slate-400 hover:text-slate-900"><X size={16} /></button>
              </div>
              <div>
                <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-1">
                  <Tags size={12} /> 特征词库 (30)
                </p>
                <div className="flex flex-wrap gap-2 p-4 bg-white border border-slate-100 rounded-2xl max-h-[140px] overflow-y-auto scrollbar-thin shadow-inner">
                  {AUDIT_KEYWORDS.map((k, idx) => (
                    <span key={idx} className="bg-indigo-50/50 text-indigo-600/80 px-2.5 py-1 rounded-lg text-[9px] font-black border border-indigo-100/50 cursor-default">{k}</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">TASK MATRIX (审计对照表)</h3>
              <button onClick={addWhitelistRow} className="text-[10px] font-black text-indigo-600 uppercase flex items-center gap-1 hover:text-indigo-800 transition-colors">
                <Plus size={12} /> 新增扫描项
              </button>
            </div>
            <div className="border border-slate-100 rounded-2xl overflow-hidden bg-white shadow-sm overflow-x-auto">
              <table className="w-full text-[11px] min-w-[650px]">
                <thead className="bg-slate-50 text-slate-400 font-black uppercase tracking-widest">
                  <tr>
                    <th className="px-4 py-4 w-10 text-center">
                      <input 
                        type="checkbox" 
                        onChange={(e) => {
                          if (e.target.checked) setSelectedIds(new Set(whitelist.map(w => w.id)));
                          else setSelectedIds(new Set());
                        }}
                        checked={whitelist.length > 0 && selectedIds.size === whitelist.length}
                        className="rounded border-slate-300 text-indigo-600 h-3.5 w-3.5"
                      />
                    </th>
                    <th className="px-4 py-4 text-left">正版商家名称</th>
                    <th className="px-4 py-4 text-left">商品全名</th>
                    <th className="px-4 py-4 text-left w-20">价格</th>
                    <th className="px-4 py-4 text-left">商家白名单</th>
                    <th className="px-4 py-4 w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {whitelist.map(item => (
                    <tr key={item.id} className={`hover:bg-slate-50/30 transition-colors ${selectedIds.has(item.id) ? 'bg-indigo-50/20' : ''}`}>
                      <td className="px-4 py-4 text-center">
                        <input 
                          type="checkbox" 
                          checked={selectedIds.has(item.id)} 
                          onChange={() => toggleSelect(item.id)} 
                          className="rounded border-slate-300 text-indigo-600 h-3.5 w-3.5" 
                        />
                      </td>
                      <td className="px-4 py-4">
                        <input type="text" placeholder="官方商家..." value={item.officialMerchantName} onChange={(e) => updateWhitelist(item.id, 'officialMerchantName', e.target.value)} className="w-full bg-transparent border-none focus:ring-0 font-medium text-slate-700 p-0" />
                      </td>
                      <td className="px-4 py-4">
                        <input type="text" placeholder="商品全称..." value={item.productName} onChange={(e) => updateWhitelist(item.id, 'productName', e.target.value)} className="w-full bg-transparent border-none focus:ring-0 font-bold text-slate-900 p-0" />
                      </td>
                      <td className="px-4 py-4">
                        <input type="text" placeholder="¥" value={item.price} onChange={(e) => updateWhitelist(item.id, 'price', e.target.value)} className="w-full bg-transparent border-none focus:ring-0 font-black text-rose-500 p-0" />
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex flex-wrap gap-1.5 items-center">
                          {item.allowedShops.map((shop, idx) => (
                            <span key={idx} className="bg-slate-100 px-2 py-0.5 rounded-md text-[9px] font-bold text-slate-600 flex items-center gap-1 border border-slate-200/50">
                              {shop}
                              <button onClick={() => updateWhitelist(item.id, 'allowedShops', item.allowedShops.filter((_, i) => i !== idx))} className="hover:text-rose-500"><X size={10} /></button>
                            </span>
                          ))}
                          <input type="text" placeholder="+ 新增" onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              const val = (e.target as HTMLInputElement).value.trim();
                              if (val) updateWhitelist(item.id, 'allowedShops', [...item.allowedShops, val]);
                              (e.target as HTMLInputElement).value = '';
                            }
                          }} className="text-[9px] bg-transparent border-none focus:ring-0 p-0 w-20 placeholder:text-slate-300" />
                        </div>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <button onClick={() => removeWhitelistRow(item.id)} className="text-slate-300 hover:text-rose-500 transition-colors"><Trash2 size={14} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="space-y-2">
              <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">搜索关键词</p>
              <div className="h-10 bg-slate-50 border border-slate-200 rounded-xl flex items-center px-4 shadow-inner">
                <input type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)} className="w-full h-full bg-transparent border-none focus:ring-0 font-black text-slate-900 text-xs p-0" placeholder="输入关键词..." />
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">运行模式</p>
              <div className="flex p-1 bg-slate-100 rounded-xl border border-slate-200/50 shadow-inner h-10">
                <button onClick={() => setTestMode(true)} className={`flex-1 text-[9px] font-black rounded-lg transition-all ${testMode ? 'bg-white shadow-sm text-slate-900' : 'text-slate-400 hover:text-slate-500'}`}>测试模式</button>
                <button onClick={() => setTestMode(false)} className={`flex-1 text-[9px] font-black rounded-lg transition-all ${!testMode ? 'bg-white shadow-sm text-slate-900' : 'text-slate-400 hover:text-slate-500'}`}>正式模式</button>
              </div>
            </div>
          </div>

          <div className="flex gap-4 items-end">
            <div className="flex-1 space-y-2">
              <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">自动搜索条数</p>
              <div className="h-10 bg-slate-50 border border-slate-200 rounded-xl flex items-center px-4 shadow-inner">
                 <input type="number" value={searchCount} onChange={(e) => setSearchCount(parseInt(e.target.value) || 0)} className="w-full h-full bg-transparent border-none focus:ring-0 font-black text-slate-900 text-xs p-0" />
                 <span className="text-[9px] font-black text-slate-300 ml-2">ITEMS</span>
              </div>
            </div>
            <div className="flex-[2.5] flex gap-3">
              <button onClick={() => setShowConfig(!showConfig)} className={`h-10 px-4 rounded-xl font-black text-[10px] uppercase border transition-all flex items-center gap-2 ${showConfig ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg' : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'}`}><SlidersHorizontal size={14} /> 审计配置</button>
              {isProcessRunning ? (
                <button onClick={handleStopSearch} className="flex-1 h-10 bg-rose-600 text-white rounded-xl font-black text-[10px] uppercase tracking-[0.25em] flex items-center justify-center gap-2 shadow-xl shadow-rose-900/20 active:scale-95 transition-all"><StopCircle size={14} fill="white" /> 停止任务</button>
              ) : (
                <button onClick={handleStartSearch} className="flex-1 h-10 bg-slate-900 text-white rounded-xl font-black text-[10px] uppercase tracking-[0.25em] flex items-center justify-center gap-2 shadow-xl shadow-slate-900/20 active:scale-95 transition-all"><Play size={14} fill="white" /> 启动执行自动搜索</button>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">REALTIME STREAM</h3>
              <button onClick={() => setLogs([])} className="text-[9px] text-slate-300 font-black uppercase tracking-widest hover:text-rose-500 transition-colors">Flush</button>
            </div>
            <div className="h-44 bg-slate-50 rounded-2xl p-5 overflow-y-auto mono text-[10px] space-y-2 border border-slate-100 scrollbar-thin shadow-inner">
              {logs.map(log => (
                <div key={log.id} className="text-slate-500 leading-relaxed">
                  <span className="opacity-40">[{log.timestamp}]</span> <span className={log.type === 'action' ? 'text-indigo-600 font-bold' : log.type === 'performance' ? 'text-rose-500 font-bold' : ''}>{log.message}</span>
                </div>
              ))}
              <div ref={logEndRef} />
            </div>
          </div>
        </div>
      </aside>
    </div>
  );

  return (
    <div className="flex h-screen bg-white overflow-hidden select-none">
      <nav className="w-20 sidebar-rect flex flex-col items-center py-10 shrink-0 z-50">
        <div className="flex flex-col items-center mb-12">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white mb-2 shadow-lg shadow-indigo-200"><ShieldCheck size={22} strokeWidth={2.5} /></div>
          <div className="text-[7px] font-black text-slate-900 uppercase tracking-tighter text-center leading-none">GUI-Stride<br/>界面行者</div>
        </div>
        <div className="flex flex-col gap-6 flex-1">
          <button 
            onClick={() => setActiveView('terminal')} 
            className={`p-3 rounded-xl transition-all flex flex-col items-center gap-1 ${activeView === 'terminal' ? 'bg-indigo-50 text-indigo-600 shadow-sm' : 'text-slate-300 hover:text-slate-500'}`}
          >
            <LayoutDashboard size={22} />
            <span className="text-[7px] font-black uppercase tracking-tighter">终端</span>
          </button>
          <button 
            onClick={() => setActiveView('summary')} 
            className={`p-3 rounded-xl transition-all flex flex-col items-center gap-1 ${activeView === 'summary' ? 'bg-indigo-50 text-indigo-600 shadow-sm' : 'text-slate-300 hover:text-slate-500'}`}
          >
            <Activity size={22} />
            <span className="text-[7px] font-black uppercase tracking-tighter">概览</span>
          </button>
        </div>
        <button 
          onClick={() => setActiveView('settings')} 
          className={`p-3 rounded-xl transition-all flex flex-col items-center gap-1 ${activeView === 'settings' ? 'bg-indigo-50 text-indigo-600 shadow-sm' : 'text-slate-300 hover:text-slate-500'}`}
        >
          <Settings size={22} />
          <span className="text-[7px] font-black uppercase tracking-tighter">设置</span>
        </button>
      </nav>
      {activeView === 'terminal' ? renderTerminal() : activeView === 'summary' ? renderSummary() : renderTerminal()}
    </div>
  );
};

export default App;
