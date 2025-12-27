
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
  ArrowUpRight
} from 'lucide-react';
import { Merchant, LogEntry, WhitelistEntry, ReportRecord, Device } from './types';
import { fetchMerchants, fetchLogs, fetchReports, startPatrol, getPatrolStatus, getPlatforms, getSystemStats, fetchWhitelist, addWhitelistEntry, deleteWhitelistEntry, getNewPatrolLogs, getPatrolLogs } from './src/services/api';
import { MerchantCard } from './components/MerchantCard';
import { PhoneMockup } from './components/PhoneMockup';

type ViewType = 'terminal' | 'summary' | 'settings' | 'devices';

const AUDIT_KEYWORDS = [
  "正版", "授权", "官方", "旗舰店", "全套", "考研", "法考", "公考", "PDF", "电子版",
  "网盘", "秒发", "引流", "微信", "私聊", "低价", "正品", "出版社", "水印", "盗版",
  "翻印", "扫描", "讲义", "真题", "解析", "押题", "专柜", "代购", "包邮", "原装"
];

const MOCK_DEVICES: Device[] = [
  { id: 'dev-001', name: 'Pixel 6 Pro - Node 01', status: 'online', isSelected: true },
  { id: 'dev-002', name: 'Samsung S22 - Node 02', status: 'online', isSelected: false },
  { id: 'dev-003', name: 'Xiaomi 13 - Node 03', status: 'offline', isSelected: false },
  { id: 'dev-004', name: 'Oppo Find X5 - Node 04', status: 'online', isSelected: false },
];

const App: React.FC = () => {
  const [activeView, setActiveView] = useState<ViewType>('terminal');
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [selectedMerchant, setSelectedMerchant] = useState<Merchant | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [platform, setPlatform] = useState<'xianyu' | 'xhs'>('xianyu');
  const [searchCount, setSearchCount] = useState<number>(20);
  const [showConfig, setShowConfig] = useState(false);
  const [patrolTaskId, setPatrolTaskId] = useState<string | null>(null);
  const [isPatrolRunning, setIsPatrolRunning] = useState(false);
  const [keyword, setKeyword] = useState<string>(''); // 搜索关键词

  // Fetch initial data from backend
  useEffect(() => {
    const loadData = async () => {
      try {
        const [merchantsData, logsData, whitelistData, reportsData] = await Promise.all([
          fetchMerchants(),
          fetchLogs(),
          fetchWhitelist(),
          fetchReports(),
        ]);
        setMerchants(merchantsData);
        if (merchantsData.length > 0) {
          setSelectedMerchant(merchantsData[0]);
        }
        setLogs(logsData);
        setWhitelist(whitelistData);
        setReports(reportsData);
      } catch (error) {
        console.error('Failed to load initial data:', error);
        // Fallback to empty states
      }
    };
    loadData();
  }, []);

  const [whitelist, setWhitelist] = useState<WhitelistEntry[]>([]);
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

  const removeWhitelistRow = (id: string) => {
    setWhitelist(whitelist.filter(item => item.id !== id));
    const next = new Set(selectedIds);
    next.delete(id);
    setSelectedIds(next);
  };

  const toggleSelect = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  };

  const handleStartSearch = async () => {
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

    // 确定搜索关键词：优先使用手动输入的关键词，否则使用第一个选中白名单条目的商品名称
    let searchKeyword = keyword.trim();
    if (!searchKeyword && activeRows.length > 0) {
      searchKeyword = activeRows[0].productName;
    }
    if (!searchKeyword) {
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'performance',
        message: '操作中断: 请输入搜索关键词或在白名单中指定商品名称。'
      }]);
      return;
    }

    try {
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'action',
        message: `[EXE] 启动自动搜索: 平台=${platform.toUpperCase()}, 关键词=${searchKeyword}, 搜索条数=${searchCount}`
      }]);

      // 调用后端API启动巡查任务
      const response = await startPatrol({
        platform: platform, // 'xianyu' 或 'xhs'
        keyword: searchKeyword,
        max_items: searchCount,
        test_mode: true // 测试模式，不实际举报
      });

      setPatrolTaskId(response.task_id);
      setIsPatrolRunning(true);

      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'info',
        message: `[SYS] 巡查任务已启动，任务ID: ${response.task_id}`
      }]);
    } catch (error) {
      console.error('启动巡查任务失败:', error);
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'performance',
        message: `[ERR] 启动巡查任务失败: ${error instanceof Error ? error.message : String(error)}`
      }]);
    }
  };

  // 轮询巡查任务状态和日志
  useEffect(() => {
    if (!patrolTaskId || !isPatrolRunning) return;

    const pollInterval = setInterval(async () => {
      try {
        // 1. 获取任务状态
        const status = await getPatrolStatus(patrolTaskId);

        // 2. 获取新日志
        try {
          const newLogs = await getNewPatrolLogs(patrolTaskId);
          if (newLogs.length > 0) {
            // 将任务日志转换为前端日志格式
            const formattedLogs: LogEntry[] = newLogs.map((log: any) => ({
              id: log.id,
              timestamp: log.timestamp_display || new Date(log.timestamp).toLocaleTimeString(),
              type: log.level === 'error' ? 'performance' : (log.level === 'warning' ? 'action' : 'info'),
              message: log.message
            }));
            setLogs(prev => [...prev, ...formattedLogs]);
          }
        } catch (logError) {
          console.error('获取任务日志失败:', logError);
          // 不中断轮询，继续获取状态
        }

        // 3. 处理任务完成或失败
        if (status.status === 'completed') {
          setIsPatrolRunning(false);
          clearInterval(pollInterval);

          if (status.result) {
            setLogs(prev => [...prev, {
              id: Date.now().toString(),
              timestamp: new Date().toLocaleTimeString(),
              type: 'info',
              message: `[SYS] 巡查任务完成: 检查商品数=${status.result.checked_count}, 发现疑似盗版=${status.result.piracy_count}, 已举报=${status.result.reported_count}`
            }]);
          }
        } else if (status.status === 'failed') {
          setIsPatrolRunning(false);
          clearInterval(pollInterval);
          setLogs(prev => [...prev, {
            id: Date.now().toString(),
            timestamp: new Date().toLocaleTimeString(),
            type: 'performance',
            message: `[ERR] 巡查任务失败${status.error ? ': ' + status.error : ''}`
          }]);
        }
        // 如果状态是 'pending' 或 'running'，继续轮询
      } catch (error) {
        console.error('轮询任务状态失败:', error);
        // 出错时不停止轮询，可能只是网络暂时问题
      }
    }, 2000); // 每2秒轮询一次

    return () => {
      clearInterval(pollInterval);
    };
  }, [patrolTaskId, isPatrolRunning]);

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
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: '累计扫描节点', value: '14,292', icon: Monitor, color: 'text-blue-600', trend: '+12.5%' },
            { label: '识别违规商家', value: '1,084', icon: AlertTriangle, color: 'text-rose-600', trend: '+4.2%' },
            { label: '挽回资产损失', value: '¥248,500', icon: DollarSign, color: 'text-emerald-600', trend: '+18.1%' },
            { label: '系统拦截效率', value: '98.2%', icon: Zap, color: 'text-indigo-600', trend: '+0.5%' },
          ].map((stat, i) => (
            <div key={i} className="luxoa-card p-6 flex flex-col justify-between">
              <div className="flex items-start justify-between">
                <div className={`p-3 rounded-2xl bg-slate-50 ${stat.color}`}>
                  <stat.icon size={20} />
                </div>
                <span className="text-[10px] font-black text-emerald-500 bg-emerald-50 px-2 py-0.5 rounded-full">{stat.trend}</span>
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
              {[
                { name: '闲鱼 (Xianyu)', val: 65, color: 'bg-yellow-500' },
                { name: '小红书 (XHS)', val: 25, color: 'bg-rose-500' },
                { name: '淘宝/天猫', val: 7, color: 'bg-orange-500' },
                { name: '其他', val: 3, color: 'bg-slate-600' },
              ].map((p, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                    <span className="text-slate-700">{p.name}</span>
                    <span className="text-slate-400">{p.val}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full ${p.color}`} style={{ width: `${p.val}%` }}></div>
                  </div>
                </div>
              ))}
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
                {reports.map((report) => (
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
          <div className="flex p-1 bg-slate-100 rounded-xl w-36 border border-slate-200/50 shadow-inner">
            <button onClick={() => setPlatform('xianyu')} className={`flex-1 py-1.5 text-[9px] font-black rounded-lg transition-all ${platform === 'xianyu' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-400 hover:text-slate-500'}`}>咸鱼</button>
            <button onClick={() => setPlatform('xhs')} className={`flex-1 py-1.5 text-[9px] font-black rounded-lg transition-all ${platform === 'xhs' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-400'}`}>小红书</button>
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

          <div className="flex gap-4 items-end">
            <div className="flex-1 space-y-2">
              <div>
                <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">搜索关键词</p>
                <div className="h-10 bg-slate-50 border border-slate-200 rounded-xl flex items-center px-4 shadow-inner">
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="输入搜索关键词（如：法考资料）"
                    className="w-full h-full bg-transparent border-none focus:ring-0 font-black text-slate-900 text-xs p-0"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <div className="flex-1">
                  <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">平台</p>
                  <div className="h-10 bg-slate-50 border border-slate-200 rounded-xl flex items-center px-4 shadow-inner">
                    <select
                      value={platform}
                      onChange={(e) => setPlatform(e.target.value as 'xianyu' | 'xhs')}
                      className="w-full h-full bg-transparent border-none focus:ring-0 font-black text-slate-900 text-xs p-0"
                    >
                      <option value="xianyu">闲鱼</option>
                      <option value="xhs">小红书</option>
                    </select>
                  </div>
                </div>
                <div className="flex-1">
                  <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">搜索条数</p>
                  <div className="h-10 bg-slate-50 border border-slate-200 rounded-xl flex items-center px-4 shadow-inner">
                    <input
                      type="number"
                      value={searchCount}
                      onChange={(e) => setSearchCount(parseInt(e.target.value) || 0)}
                      className="w-full h-full bg-transparent border-none focus:ring-0 font-black text-slate-900 text-xs p-0"
                    />
                    <span className="text-[9px] font-black text-slate-300 ml-2">ITEMS</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex-[2.5] flex gap-3">
              <button onClick={() => setShowConfig(!showConfig)} className={`h-10 px-4 rounded-xl font-black text-[10px] uppercase border transition-all flex items-center gap-2 ${showConfig ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg' : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'}`}><SlidersHorizontal size={14} /> 审计配置</button>
              <button onClick={handleStartSearch} className="flex-1 h-10 bg-slate-900 text-white rounded-xl font-black text-[10px] uppercase tracking-[0.25em] flex items-center justify-center gap-2 shadow-xl shadow-slate-900/20 active:scale-95 transition-all"><Play size={14} fill="white" /> 启动执行自动搜索</button>
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
