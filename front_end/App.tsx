
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  LayoutDashboard, 
  ShieldCheck, 
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
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  ArrowUpRight,
  Download,
  Smartphone,
  Circle,
  Link2,
  FileText,
  ChevronDown,
  Award,
  Calendar,
  Package,
  Loader2,
  Store,
  CheckCircle
} from 'lucide-react';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import JSZip from 'jszip';
import { Merchant, LogEntry, WhitelistEntry, Device } from './types';
import { MOCK_MERCHANTS, INITIAL_LOGS, MOCK_REPORTS } from './constants';
import { MerchantCard } from './components/MerchantCard';
import { PhoneMockup } from './components/PhoneMockup';

type ViewType = 'terminal' | 'summary' | 'devices';

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
  const [merchants] = useState<Merchant[]>(MOCK_MERCHANTS);
  const [selectedMerchant, setSelectedMerchant] = useState<Merchant | null>(MOCK_MERCHANTS[0]);
  const [logs, setLogs] = useState<LogEntry[]>(INITIAL_LOGS);
  const [platform, setPlatform] = useState<'xianyu' | 'xhs'>('xianyu');
  const [searchCount, setSearchCount] = useState<number>(20);
  const [showConfig, setShowConfig] = useState(false);
  const [devices, setDevices] = useState<Device[]>(MOCK_DEVICES);
  const [reportMenuOpen, setReportMenuOpen] = useState(false);
  const [isProcessingExport, setIsProcessingExport] = useState(false);
  
  const [whitelist, setWhitelist] = useState<WhitelistEntry[]>([
    { id: '1', officialMerchantName: '官方出版社', productName: '2025法考全套资料', price: '299', allowedShops: ['官方旗舰店', '正版分销商', '法律社直营'] }
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

  const exportToExcel = () => {
    const headers = ["单号", "违规商家", "涉及商品", "违规判定理由", "日期", "状态"];
    const rows = MOCK_REPORTS.map(r => [
      r.reportNumber,
      r.merchantName,
      r.productName,
      r.reason.replace(/,/g, ' '),
      r.date,
      "已提交下架"
    ]);
    
    const csvContent = [headers, ...rows].map(e => e.join(",")).join("\n");
    const blob = new Blob(["\ufeff" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `审计维权流水_${new Date().toLocaleDateString()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setLogs(prev => [...prev, {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      type: 'action',
      message: '系统提示: 维权流水数据已成功导出为 Excel (CSV) 文件。'
    }]);
    setReportMenuOpen(false);
  };

  const generateBatchZip = async () => {
    setIsProcessingExport(true);
    setReportMenuOpen(false);
    setLogs(prev => [...prev, {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      type: 'info',
      message: '存证引擎: 正在初始化批量导出任务，按 3 小时步长分拣归档...'
    }]);

    try {
      const zip = new JSZip();
      const mockReportsWithTime = MOCK_REPORTS.map((r, i) => ({
        ...r,
        mockHour: (10 + (i * 3)) % 24 
      }));

      for (const report of mockReportsWithTime) {
        const intervalStart = Math.floor(report.mockHour / 3) * 3;
        const intervalEnd = intervalStart + 3;
        const intervalFolderName = `${report.date}_${String(intervalStart).padStart(2, '0')}h-${String(intervalEnd).padStart(2, '0')}h`;
        const reportFolder = zip.folder(intervalFolderName)?.folder(report.reportNumber);
        
        // 这里的图片会根据 constants 中的 evidenceImages 模拟
        const imageUrls = report.screenshots || [];

        for (let j = 0; j < imageUrls.length; j++) {
          try {
            const response = await fetch(imageUrls[j]);
            const blob = await response.blob();
            reportFolder?.file(`evidence_0${j + 1}.png`, blob);
          } catch (e) {
            reportFolder?.file(`evidence_0${j + 1}.txt`, "Placeholder content");
          }
        }
      }

      const content = await zip.generateAsync({ type: "blob" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(content);
      link.download = `Batch_Evidence_${new Date().toISOString().slice(0, 10)}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'action',
        message: '存证引擎: 批量存证压缩包已成功构建并开始下载。'
      }]);
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessingExport(false);
    }
  };

  const generatePDFReport = async (type: 'weekly' | 'monthly') => {
    setIsProcessingExport(true);
    setReportMenuOpen(false);
    setLogs(prev => [...prev, {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      type: 'info',
      message: `报告引擎: 正在构建可视化${type === 'weekly' ? '周' : '月'}报模版...`
    }]);

    const templateContainer = document.getElementById('pdf-template-container');
    if (!templateContainer) return;

    templateContainer.innerHTML = `
      <div style="background: white; color: #1e293b; font-family: sans-serif; padding: 40px; border: 1px solid #e2e8f0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; border-bottom: 4px solid #4f46e5; padding-bottom: 20px;">
          <div>
            <h1 style="font-size: 32px; font-weight: 900; color: #4f46e5; margin: 0;">GUI-Stride Report</h1>
            <p style="font-size: 14px; font-weight: bold; color: #64748b; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 2px;">
              ${type === 'weekly' ? 'Weekly' : 'Monthly'} Audit Intelligence
            </p>
          </div>
          <div style="text-align: right;">
            <p style="font-size: 12px; font-weight: bold; color: #94a3b8; margin: 0;">REPORT ID: STRIDE-${Date.now()}</p>
            <p style="font-size: 12px; font-weight: bold; color: #94a3b8; margin: 0;">DATE: ${new Date().toLocaleDateString()}</p>
          </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px;">
          <div style="background: #f8fafc; padding: 20px; border-radius: 16px; border-left: 4px solid #4f46e5;">
            <p style="font-size: 10px; font-weight: 900; color: #64748b; margin-bottom: 5px;">TOTAL NODES</p>
            <h2 style="font-size: 24px; font-weight: 900; color: #1e293b; margin: 0;">14,292</h2>
          </div>
          <div style="background: #f8fafc; padding: 20px; border-radius: 16px; border-left: 4px solid #ef4444;">
            <p style="font-size: 10px; font-weight: 900; color: #64748b; margin-bottom: 5px;">PIRATES CAUGHT</p>
            <h2 style="font-size: 24px; font-weight: 900; color: #1e293b; margin: 0;">1,084</h2>
          </div>
          <div style="background: #f8fafc; padding: 20px; border-radius: 16px; border-left: 4px solid #10b981;">
            <p style="font-size: 10px; font-weight: 900; color: #64748b; margin-bottom: 5px;">LOSS PREVENTED</p>
            <h2 style="font-size: 24px; font-weight: 900; color: #1e293b; margin: 0;">¥248,500</h2>
          </div>
        </div>
        <h3 style="font-size: 14px; font-weight: 900; color: #1e293b; margin-bottom: 15px; text-transform: uppercase;">Recent Enforcement Actions</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
          <thead>
            <tr style="background: #f1f5f9; text-align: left;">
              <th style="padding: 10px; border: 1px solid #e2e8f0;">编号</th>
              <th style="padding: 10px; border: 1px solid #e2e8f0;">违规商家</th>
              <th style="padding: 10px; border: 1px solid #e2e8f0;">状态</th>
            </tr>
          </thead>
          <tbody>
            ${MOCK_REPORTS.map(r => `
              <tr>
                <td style="padding: 10px; border: 1px solid #e2e8f0;">${r.reportNumber}</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">${r.merchantName}</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; color: #10b981;">已存证下架</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    try {
      const canvas = await html2canvas(templateContainer, { scale: 2, useCORS: true, backgroundColor: '#ffffff' });
      const imgData = canvas.toDataURL('image/png');
      const doc = new jsPDF('p', 'mm', 'a4');
      const pageWidth = doc.internal.pageSize.getWidth();
      const imgWidth = pageWidth - 20;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      doc.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight);
      doc.save(`GUI_Stride_${type}_Report_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessingExport(false);
      templateContainer.innerHTML = '';
    }
  };

  const toggleDeviceSelection = (deviceId: string) => {
    setDevices(prev => prev.map(d => 
      d.id === deviceId ? { ...d, isSelected: !d.isSelected } : d
    ));
    const device = devices.find(d => d.id === deviceId);
    if (device) {
      setLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString(),
        type: 'info',
        message: `设备交互: ${!device.isSelected ? '已连接' : '已断开'} 设备 ${device.name}`
      }]);
    }
  };

  const addWhitelistRow = () => {
    const newEntry: WhitelistEntry = { id: Math.random().toString(36).substr(2, 9), officialMerchantName: '', productName: '', price: '', allowedShops: [] };
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

  const handleStartSearch = () => {
    const activeRows = whitelist.filter(row => selectedIds.has(row.id));
    const activeDevices = devices.filter(d => d.isSelected && d.status === 'online');
    if (activeRows.length === 0 || activeDevices.length === 0) return;
    setLogs(prev => [...prev, {
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString(),
      type: 'action',
      message: `[EXE] 启动自动搜索: 平台=${platform.toUpperCase()}, 任务数=${activeRows.length}, 活跃设备=${activeDevices.length}, 条数=${searchCount}`
    }]);
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
          <div className="flex items-center gap-4">
             <div className="relative">
                <button 
                  onClick={() => setReportMenuOpen(!reportMenuOpen)}
                  disabled={isProcessingExport}
                  className="bg-white border border-slate-200 text-slate-700 px-5 py-2.5 rounded-xl shadow-sm flex items-center gap-2 text-[11px] font-black uppercase tracking-widest transition-all hover:bg-slate-50 active:scale-95 disabled:opacity-50"
                >
                  {isProcessingExport ? <Loader2 size={16} className="animate-spin text-indigo-500" /> : <FileText size={16} />} 
                  {isProcessingExport ? '处理中...' : '导出报告'} 
                  <ChevronDown size={14} className={`transition-transform duration-300 ${reportMenuOpen ? 'rotate-180' : ''}`} />
                </button>
                {reportMenuOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setReportMenuOpen(false)}></div>
                    <div className="absolute top-full right-0 mt-2 w-64 bg-white border border-slate-100 rounded-2xl shadow-2xl z-50 overflow-hidden py-2 animate-in slide-in-from-top-2 duration-200">
                      <button onClick={exportToExcel} className="w-full text-left px-4 py-3 text-[10px] font-black text-slate-600 uppercase tracking-widest hover:bg-indigo-50 hover:text-indigo-600 transition-colors flex items-center gap-3">
                         <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-sm"><FileSpreadsheet size={16} /></div>
                         <div>
                            <div>维权流水 (Excel)</div>
                            <div className="text-[8px] opacity-60 font-medium lowercase">Export raw data as CSV</div>
                         </div>
                      </button>
                      <div className="h-px bg-slate-50 mx-4 my-1"></div>
                      <button onClick={generateBatchZip} className="w-full text-left px-4 py-3 text-[10px] font-black text-indigo-600 uppercase tracking-widest hover:bg-indigo-50 hover:text-indigo-600 transition-colors flex items-center gap-3">
                         <div className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shadow-sm"><Package size={16} /></div>
                         <div>
                            <div>批量导出存证 (ZIP)</div>
                            <div className="text-[8px] opacity-60 font-medium lowercase">Grouped by 3-hour intervals</div>
                         </div>
                      </button>
                      <div className="h-px bg-slate-50 mx-4 my-1"></div>
                      <button onClick={() => generatePDFReport('weekly')} className="w-full text-left px-4 py-3 text-[10px] font-black text-slate-600 uppercase tracking-widest hover:bg-indigo-50 hover:text-indigo-600 transition-colors flex items-center gap-3">
                         <div className="w-8 h-8 rounded-xl bg-slate-50 text-slate-600 flex items-center justify-center shadow-sm"><Calendar size={16} /></div>
                         <div>
                            <div>生成周报 (PDF)</div>
                            <div className="text-[8px] opacity-60 font-medium lowercase">Weekly visual document</div>
                         </div>
                      </button>
                      <button onClick={() => generatePDFReport('monthly')} className="w-full text-left px-4 py-3 text-[10px] font-black text-slate-600 uppercase tracking-widest hover:bg-indigo-50 hover:text-indigo-600 transition-colors flex items-center gap-3">
                         <div className="w-8 h-8 rounded-xl bg-slate-50 text-slate-600 flex items-center justify-center shadow-sm"><Award size={16} /></div>
                         <div>
                            <div>生成月报 (PDF)</div>
                            <div className="text-[8px] opacity-60 font-medium lowercase">Monthly summary insights</div>
                         </div>
                      </button>
                    </div>
                  </>
                )}
             </div>
             <div className="bg-white border border-slate-200 px-4 py-2.5 rounded-xl shadow-sm flex items-center gap-3">
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
                <div className={`p-3 rounded-2xl bg-slate-50 ${stat.color}`}><stat.icon size={20} /></div>
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
              <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest flex items-center gap-2"><TrendingUp size={16} className="text-indigo-600" /> 7日防护趋势分析</h3>
              <div className="flex gap-2">
                 <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
                 <span className="text-[9px] font-black text-slate-400 uppercase">每日拦截数</span>
              </div>
            </div>
            <div className="h-64 flex items-end justify-between gap-4">
              {[60, 80, 45, 95, 70, 85, 100].map((h, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-4 group">
                  <div className="w-full bg-slate-50 rounded-xl relative overflow-hidden"><div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-xl transition-all duration-1000 group-hover:from-indigo-500" style={{ height: `${h}%` }}></div></div>
                  <span className="text-[9px] font-black text-slate-400">05-{20+i}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="luxoa-card p-8 bg-white border border-slate-200">
            <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest mb-8 flex items-center gap-2"><ShieldCheck size={16} className="text-emerald-500" /> 平台风险分布</h3>
            <div className="space-y-6">
              {[
                { name: '闲鱼 (Xianyu)', val: 65, color: 'bg-yellow-500' },
                { name: '小红书 (XHS)', val: 25, color: 'bg-rose-500' },
                { name: '淘宝/天猫', val: 7, color: 'bg-orange-500' },
                { name: '其他', val: 3, color: 'bg-slate-600' },
              ].map((p, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex justify-between text-[10px] font-black uppercase tracking-widest"><span className="text-slate-700">{p.name}</span><span className="text-slate-400">{p.val}%</span></div>
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden"><div className={`h-full ${p.color}`} style={{ width: `${p.val}%` }}></div></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDevices = () => (
    <div className="flex-1 bg-slate-50 p-10 overflow-y-auto scrollbar-thin animate-in fade-in duration-500">
      <div className="max-w-4xl mx-auto space-y-10">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-black text-indigo-600 uppercase tracking-widest mb-1"><Smartphone size={14} /> Multi-Device Hub</div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">设备管理列表</h1>
          <p className="text-slate-400 font-bold text-xs uppercase tracking-widest mt-1">管理并连接当前集群中的审计终端</p>
        </div>
        <div className="luxoa-card overflow-hidden">
          <table className="w-full text-left text-[11px]">
            <thead className="bg-slate-50 text-slate-400 font-black uppercase tracking-widest"><tr><th className="px-8 py-5 w-40 text-center">审计连接</th><th className="px-8 py-5">可用设备名称 / 标识符</th></tr></thead>
            <tbody className="divide-y divide-slate-50 text-slate-700 font-medium">{devices.map((device) => (
                <tr key={device.id} className="hover:bg-slate-50/30 transition-colors">
                  <td className="px-8 py-6 text-center">
                    <button onClick={() => toggleDeviceSelection(device.id)} className={`mx-auto flex items-center justify-center gap-2 px-4 py-1.5 rounded-full font-black text-[9px] uppercase tracking-widest border transition-all ${device.status === 'online' ? (device.isSelected ? 'bg-emerald-500 text-white border-emerald-500' : 'border-emerald-100 bg-emerald-50 text-emerald-600 hover:bg-emerald-100') : 'border-rose-100 bg-rose-50 text-rose-500'}`}><Circle size={8} fill="currentColor" className={device.status === 'online' ? 'animate-pulse' : ''} />{device.status === 'online' ? (device.isSelected ? '已连接' : '待命') : '离线'}</button>
                  </td>
                  <td className="px-8 py-6"><div className="flex flex-col"><span className="text-[13px] font-black text-slate-900">{device.name}</span><span className="text-[9px] font-black text-slate-300 uppercase mt-0.5 tracking-widest">{device.id}</span></div></td>
                </tr>
            ))}</tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderTerminal = () => (
    <div className="flex-1 flex overflow-hidden animate-in fade-in duration-300 no-select">
      {/* 左侧监测面板 */}
      <aside className="border-r border-slate-100 bg-white flex flex-col overflow-hidden shrink-0" style={{ width: `${leftWidth}px` }}>
        <div className="flex-1 flex flex-col p-6 border-b border-slate-50 min-h-0">
          <div className="mb-4">
            <div className="flex items-center gap-2 text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-1"><Zap size={14} fill="currentColor" /> MONITORING NODE</div>
            <h2 className="text-xl font-black text-slate-900 tracking-tight">监测中心</h2>
          </div>
          <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[11px] font-black text-slate-400 uppercase tracking-widest">已审队列 (滑动手卡)</h3>
              <span className="text-[9px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-black">LIVE</span>
            </div>
            <div className="flex-1 overflow-x-auto overflow-y-hidden pb-4 scrollbar-thin flex gap-4 items-center">
              {merchants.map(m => (
                <MerchantCard key={m.id} merchant={m} isSelected={selectedMerchant?.id === m.id} onSelect={setSelectedMerchant} />
              ))}
            </div>
          </div>
        </div>
        <div className="flex-1 flex flex-col p-6 min-h-0">
          <div className="mb-4">
            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2"><Activity size={14} className="text-indigo-500" /> AI 推理 & 存证截图</h3>
          </div>
          <div className="flex-1 flex flex-col min-h-0">
            <div className="flex-shrink-0 w-full luxoa-card p-5 border-indigo-100 bg-indigo-50/20 flex flex-col mb-4">
               <div className="flex items-center justify-between mb-3">
                  <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">判定链 (Reasoning)</p>
                  {selectedMerchant?.status === 'official' && <div className="bg-emerald-500 text-white p-1 rounded-lg shadow-sm"><CheckCircle size={14} /></div>}
               </div>
               {selectedMerchant ? (
                 selectedMerchant.status === 'official' ? (
                   <div className="flex flex-col items-center justify-center py-4 space-y-2 border-2 border-dashed border-emerald-200 rounded-2xl bg-white">
                      <p className="text-[13px] font-black text-emerald-600 uppercase tracking-wider">正版官方渠道</p>
                      <p className="text-[11px] font-bold text-slate-400">检测状态：合规 · 无需举报</p>
                   </div>
                 ) : (
                   <p className="text-[12px] leading-relaxed text-slate-700 font-medium italic serif overflow-y-auto max-h-[100px] scrollbar-thin">“{selectedMerchant.reasoning}”</p>
                 )
               ) : <p className="text-slate-300 italic text-[11px]">等待选择节点...</p>}
            </div>
            
            <div className="flex-1 overflow-x-auto overflow-y-hidden flex gap-4 items-stretch pb-4 scrollbar-thin">
              {selectedMerchant?.evidenceImages?.map((img, i) => (
                <div key={i} className="flex-shrink-0 w-64 rounded-2xl bg-slate-100 overflow-hidden border border-slate-200 shadow-sm relative group">
                  <img src={img} className={`w-full h-full object-cover transition-all duration-300 ${selectedMerchant.status === 'official' ? 'opacity-90' : 'grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100'}`} />
                  <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm px-2 py-0.5 rounded text-[8px] font-black text-slate-900 uppercase">Evidence #{i+1}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </aside>

      <div onMouseDown={() => setIsResizingLeft(true)} className={`resizer-v ${isResizingLeft ? 'active' : ''}`} />

      {/* 中间手机预览 */}
      <main className="flex-1 bg-[#F8FAFC] flex items-center justify-center relative overflow-hidden border-r border-slate-100"><div className="scale-90"><PhoneMockup /></div></main>

      <div onMouseDown={() => setIsResizingRight(true)} className={`resizer-v ${isResizingRight ? 'active' : ''}`} />

      {/* 右侧控制面板 */}
      <aside className="bg-white flex flex-col p-8 overflow-y-auto scrollbar-thin shrink-0" style={{ width: `${rightWidth}px` }}>
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center text-white shadow-lg"><User size={20} /></div>
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
            <div className="bg-slate-50 rounded-2xl border border-slate-200 p-6 animate-in slide-in-from-top-4 duration-300 space-y-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[10px] font-black text-slate-800 uppercase tracking-widest flex items-center gap-2"><Smartphone size={14} /> 活跃审计端连接</h3>
                <button onClick={() => setShowConfig(false)} className="text-slate-400 hover:text-slate-900"><X size={16} /></button>
              </div>
              <div className="bg-white border border-slate-100 rounded-xl overflow-hidden shadow-inner">
                 <table className="w-full text-[10px]">
                    <thead className="bg-slate-50 text-slate-400 font-black uppercase tracking-widest"><tr><th className="px-4 py-2 text-center w-24">选中</th><th className="px-4 py-2 text-left">设备名称</th></tr></thead>
                    <tbody className="divide-y divide-slate-50">{devices.map(d => (
                      <tr key={d.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-4 py-2 text-center">
                           <button onClick={() => toggleDeviceSelection(d.id)} className={`px-3 py-1 rounded-full text-[8px] font-black border transition-all ${d.status === 'online' ? (d.isSelected ? 'bg-emerald-500 text-white border-emerald-500' : 'bg-white text-emerald-600 border-emerald-100') : 'bg-slate-50 text-slate-300 cursor-not-allowed opacity-50'}`}>{d.status === 'online' ? (d.isSelected ? '已连' : '连接') : '离线'}</button>
                        </td>
                        <td className="px-4 py-2 font-black text-slate-700">{d.name}</td>
                      </tr>
                    ))}</tbody>
                 </table>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <Terminal size={12} /> 审计任务对照表 (TASK MATRIX)
              </h3>
              <button onClick={addWhitelistRow} className="text-[10px] font-black text-indigo-600 uppercase flex items-center gap-1 hover:text-indigo-800 transition-colors">
                <Plus size={12} /> 新增扫描项
              </button>
            </div>
            <div className="border border-slate-100 rounded-2xl overflow-hidden bg-white shadow-sm overflow-x-auto">
              <table className="w-full text-[11px] min-w-[800px]">
                <thead className="bg-slate-50 text-slate-400 font-black uppercase tracking-widest">
                  <tr>
                    <th className="px-4 py-4 w-10 text-center">
                      <input type="checkbox" onChange={(e) => { if (e.target.checked) setSelectedIds(new Set(whitelist.map(w => w.id))); else setSelectedIds(new Set()); }} checked={whitelist.length > 0 && selectedIds.size === whitelist.length} className="rounded border-slate-300 text-indigo-600 h-3.5 w-3.5" />
                    </th>
                    <th className="px-4 py-4 text-left">正版商家</th>
                    <th className="px-4 py-4 text-left">监测商品</th>
                    <th className="px-4 py-4 text-left w-20">单价</th>
                    <th className="px-4 py-4 text-left min-w-[200px]">商家子表 (白名单)</th>
                    <th className="px-4 py-4 w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {whitelist.map(item => (
                    <tr key={item.id} className={`hover:bg-slate-50/30 transition-colors ${selectedIds.has(item.id) ? 'bg-indigo-50/20' : ''}`}>
                      <td className="px-4 py-4 text-center">
                        <input type="checkbox" checked={selectedIds.has(item.id)} onChange={() => toggleSelect(item.id)} className="rounded border-slate-300 text-indigo-600 h-3.5 w-3.5" />
                      </td>
                      <td className="px-4 py-4">
                        <input type="text" placeholder="官方主体..." value={item.officialMerchantName} onChange={(e) => updateWhitelist(item.id, 'officialMerchantName', e.target.value)} className="w-full bg-transparent border-none focus:ring-0 font-medium text-slate-700 p-0 placeholder:font-normal placeholder:text-slate-300" />
                      </td>
                      <td className="px-4 py-4">
                        <input type="text" placeholder="商品关键词..." value={item.productName} onChange={(e) => updateWhitelist(item.id, 'productName', e.target.value)} className="w-full bg-transparent border-none focus:ring-0 font-bold text-slate-900 p-0 placeholder:font-normal placeholder:text-slate-300" />
                      </td>
                      <td className="px-4 py-4">
                        <input type="text" placeholder="¥" value={item.price} onChange={(e) => updateWhitelist(item.id, 'price', e.target.value)} className="w-full bg-transparent border-none focus:ring-0 font-black text-rose-500 p-0" />
                      </td>
                      <td className="px-4 py-4">
                        <div className="flex flex-wrap gap-1.5 items-center">
                          {item.allowedShops.map((shop, idx) => (
                            <span key={idx} className="bg-indigo-50/50 text-indigo-600 px-2 py-0.5 rounded-md text-[9px] font-black border border-indigo-100/50 flex items-center gap-1 group">
                              <Store size={10} className="opacity-60" />
                              {shop}
                              <button 
                                onClick={() => updateWhitelist(item.id, 'allowedShops', item.allowedShops.filter((_, i) => i !== idx))}
                                className="text-indigo-300 hover:text-rose-500 transition-colors"
                              >
                                <X size={10} />
                              </button>
                            </span>
                          ))}
                          <div className="flex items-center gap-1 border-b border-dashed border-slate-200">
                             <Plus size={10} className="text-slate-300" />
                             <input 
                                type="text" 
                                placeholder="回车添加允许商家" 
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') {
                                    const val = (e.target as HTMLInputElement).value.trim();
                                    if (val) updateWhitelist(item.id, 'allowedShops', [...item.allowedShops, val]);
                                    (e.target as HTMLInputElement).value = '';
                                  }
                                }} 
                                className="text-[9px] bg-transparent border-none focus:ring-0 p-0 w-24 placeholder:text-slate-300 font-bold" 
                             />
                          </div>
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
              <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">搜索深度 (条数)</p>
              <div className="h-10 bg-slate-50 border border-slate-200 rounded-xl flex items-center px-4 shadow-inner">
                 <input type="number" value={searchCount} onChange={(e) => setSearchCount(parseInt(e.target.value) || 0)} className="w-full h-full bg-transparent border-none focus:ring-0 font-black text-slate-900 text-xs p-0" />
                 <span className="text-[9px] font-black text-slate-300 ml-2">ITEMS</span>
              </div>
            </div>
            <div className="flex-[2.5] flex gap-3">
              <button onClick={() => setShowConfig(!showConfig)} className={`h-10 px-4 rounded-xl font-black text-[10px] uppercase border transition-all flex items-center gap-2 ${showConfig ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg' : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'}`}><SlidersHorizontal size={14} /> 审计配置</button>
              <button onClick={handleStartSearch} className="flex-1 h-10 bg-slate-900 text-white rounded-xl font-black text-[10px] uppercase tracking-[0.25em] flex items-center justify-center gap-2 active:scale-95 transition-all shadow-xl shadow-slate-900/10"><Play size={14} fill="white" /> 启动执行自动搜索</button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between"><h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">REALTIME STREAM</h3><button onClick={() => setLogs([])} className="text-[9px] text-slate-300 font-black hover:text-rose-500 transition-colors uppercase tracking-widest">Flush Logs</button></div>
            <div className="h-44 bg-slate-50 rounded-2xl p-5 overflow-y-auto mono text-[10px] space-y-2 border border-slate-100 scrollbar-thin shadow-inner">
              {logs.map(log => (
                <div key={log.id} className="text-slate-500 leading-relaxed"><span className="opacity-40">[{log.timestamp}]</span> <span className={log.type === 'action' ? 'text-indigo-600 font-bold' : log.type === 'performance' ? 'text-rose-500' : ''}>{log.message}</span></div>
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
          <button onClick={() => setActiveView('terminal')} className={`p-3 rounded-xl transition-all flex flex-col items-center gap-1 ${activeView === 'terminal' ? 'bg-indigo-50 text-indigo-600 shadow-sm' : 'text-slate-300 hover:text-slate-500'}`}><LayoutDashboard size={22} /><span className="text-[7px] font-black uppercase tracking-tighter">终端</span></button>
          <button onClick={() => setActiveView('summary')} className={`p-3 rounded-xl transition-all flex flex-col items-center gap-1 ${activeView === 'summary' ? 'bg-indigo-50 text-indigo-600 shadow-sm' : 'text-slate-300 hover:text-slate-500'}`}><Activity size={22} /><span className="text-[7px] font-black uppercase tracking-tighter">概览</span></button>
        </div>
        <button onClick={() => setActiveView('devices')} className={`p-3 rounded-xl transition-all flex flex-col items-center gap-1 ${activeView === 'devices' ? 'bg-indigo-50 text-indigo-600 shadow-sm' : 'text-slate-300 hover:text-slate-500'}`}><Smartphone size={22} /><span className="text-[7px] font-black uppercase tracking-tighter">设备</span></button>
      </nav>
      {activeView === 'terminal' ? renderTerminal() : activeView === 'summary' ? renderSummary() : renderDevices()}
    </div>
  );
};

export default App;
