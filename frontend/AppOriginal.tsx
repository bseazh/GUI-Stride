
import React, { useState } from 'react';
import { Plus, Trash2, Search, Loader2, Info, LayoutGrid, Target, Code, Database, Send, ClipboardCheck } from 'lucide-react';
import { Platform, SearchItem, SearchParams } from './types';
import { performAutomatedSearch } from './services/geminiService';

const App: React.FC = () => {
  const [platform, setPlatform] = useState<Platform>(Platform.XHS);
  const [items, setItems] = useState<SearchItem[]>([
    { id: '1', merchantName: '', productFullName: '', price: '' }
  ]);
  const [focusItemId, setFocusItemId] = useState<string>('1');
  const [searchCount, setSearchCount] = useState<number>(10);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [results, setResults] = useState<string | null>(null);
  const [payloadPreview, setPayloadPreview] = useState<{ structured: string; raw: string } | null>(null);

  const handleAddItem = () => {
    const newId = Math.random().toString(36).substr(2, 9);
    setItems([...items, { id: newId, merchantName: '', productFullName: '', price: '' }]);
  };

  const handleRemoveItem = (id: string) => {
    if (items.length > 1) {
      const newItems = items.filter(item => item.id !== id);
      setItems(newItems);
      if (focusItemId === id) {
        setFocusItemId(newItems[0].id);
      }
    }
  };

  const handleUpdateItem = (id: string, field: keyof SearchItem, value: string) => {
    setItems(items.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const generatePayloadSummary = () => {
    const focusItem = items.find(i => i.id === focusItemId);
    
    // 拼接所有参数的原始字符串
    const rawConcatenation = `PLATFORM[${platform}] | COUNT[${searchCount}] | FOCUS[${focusItem?.productFullName || 'N/A'}] | DATA_STREAM{${items.map(i => `${i.merchantName}:${i.productFullName}:¥${i.price}`).join(' >> ')}}`;

    const structured = `[REQUEST_HEADER]\n` +
                      `Target_Platform: ${platform}\n` +
                      `Search_Limit: ${searchCount} items\n` +
                      `Priority_Focus: ${focusItem?.productFullName || 'None'}\n\n` +
                      `[ITEM_COLLECTION]\n` +
                      items.map((it, idx) => `#${idx + 1} | M:${it.merchantName || '---'} | P:${it.productFullName || '---'} | Price:¥${it.price || '0'}`).join('\n');

    return { structured, raw: rawConcatenation };
  };

  const startSearch = async () => {
    if (items.some(i => !i.productFullName)) {
      alert("请填写完整的商品名称以供搜索");
      return;
    }

    setPayloadPreview(generatePayloadSummary());
    setIsSearching(true);
    setResults(null);
    try {
      const report = await performAutomatedSearch({ platform, items, searchCount, focusItemId });
      setResults(report);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Search failed");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Search className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-800">市场情报自动搜索系统</h1>
          </div>
          <div className="text-xs text-slate-500 font-medium bg-slate-100 px-3 py-1 rounded-full flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            V1.3.0 Standard Payload Ready
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 mt-8 space-y-8">
        {/* Step 1: Platform Selection */}
        <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-sm">01</div>
            <h2 className="text-lg font-semibold tracking-tight">选择数据源平台</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setPlatform(Platform.XHS)}
              className={`flex items-center justify-center gap-3 p-4 rounded-xl border-2 transition-all ${
                platform === Platform.XHS 
                  ? 'border-indigo-600 bg-indigo-50 text-indigo-600 shadow-md ring-2 ring-indigo-100 ring-offset-1' 
                  : 'border-slate-100 bg-slate-50 text-slate-500 hover:border-slate-200'
              }`}
            >
              <span className="text-xl">📕</span>
              <span className="font-semibold">{Platform.XHS}</span>
            </button>
            <button
              onClick={() => setPlatform(Platform.Xianyu)}
              className={`flex items-center justify-center gap-3 p-4 rounded-xl border-2 transition-all ${
                platform === Platform.Xianyu 
                  ? 'border-indigo-600 bg-indigo-50 text-indigo-600 shadow-md ring-2 ring-indigo-100 ring-offset-1' 
                  : 'border-slate-100 bg-slate-50 text-slate-500 hover:border-slate-200'
              }`}
            >
              <span className="text-xl">🐟</span>
              <span className="font-semibold">{Platform.Xianyu}</span>
            </button>
          </div>
        </section>

        {/* Step 2: Dynamic Table */}
        <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-sm">02</div>
              <h2 className="text-lg font-semibold tracking-tight">填写商品参数</h2>
            </div>
            <button
              onClick={handleAddItem}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-indigo-600 hover:bg-indigo-50 transition-colors"
            >
              <Plus className="w-4 h-4" />
              添加商品行
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-separate border-spacing-y-2">
              <thead>
                <tr className="text-left text-[11px] font-bold text-slate-400 uppercase tracking-[0.1em]">
                  <th className="px-4 py-1">商家/品牌</th>
                  <th className="px-4 py-1">商品全称</th>
                  <th className="px-4 py-1">预期单价 (¥)</th>
                  <th className="px-4 py-1 w-10 text-center">状态</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className={`group transition-all ${focusItemId === item.id ? 'bg-indigo-50/60 ring-1 ring-indigo-100' : ''}`}>
                    <td className="px-2">
                      <input
                        type="text"
                        placeholder="商店名称"
                        value={item.merchantName}
                        onChange={(e) => handleUpdateItem(item.id, 'merchantName', e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                      />
                    </td>
                    <td className="px-2">
                      <input
                        type="text"
                        placeholder="商品完整信息"
                        value={item.productFullName}
                        onChange={(e) => handleUpdateItem(item.id, 'productFullName', e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                      />
                    </td>
                    <td className="px-2">
                      <input
                        type="number"
                        placeholder="0.00"
                        value={item.price}
                        onChange={(e) => handleUpdateItem(item.id, 'price', e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                      />
                    </td>
                    <td className="px-2 text-center">
                      <button
                        onClick={() => handleRemoveItem(item.id)}
                        disabled={items.length === 1}
                        className="p-2 text-slate-300 hover:text-red-500 disabled:opacity-0 transition-colors"
                        title="删除此行"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Step 3: Action Controls */}
        <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
           <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-sm">03</div>
            <h2 className="text-lg font-semibold tracking-tight">后端指令配置</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                <Target className="w-3.5 h-3.5 text-indigo-500" />
                优先执行目标行
              </label>
              <select
                value={focusItemId}
                onChange={(e) => setFocusItemId(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all cursor-pointer shadow-sm"
              >
                {items.map((item, index) => (
                  <option key={item.id} value={item.id}>
                    行 {index + 1}: {item.productFullName || '(未填写名称)'}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                <Info className="w-3.5 h-3.5 text-slate-400" />
                后端自动搜索条数
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={searchCount}
                onChange={(e) => setSearchCount(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-sm"
              />
            </div>
          </div>
          
          <button
            onClick={startSearch}
            disabled={isSearching}
            className="w-full px-8 py-5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white rounded-2xl font-bold shadow-xl shadow-indigo-200 transition-all flex items-center justify-center gap-3 text-lg group"
          >
            {isSearching ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin text-indigo-200" />
                <span className="tracking-wide">AI 正在深度检索后端数据...</span>
              </>
            ) : (
              <>
                <Search className="w-6 h-6 group-hover:scale-110 transition-transform" />
                开始执行自动搜索
              </>
            )}
          </button>
        </section>

        {/* Payload Visualization Section */}
        {payloadPreview && (
          <section className="bg-slate-900 rounded-2xl shadow-2xl border border-slate-800 overflow-hidden animate-in fade-in zoom-in duration-500">
            <div className="bg-slate-800/50 px-6 py-3 border-b border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-300">
                <Database className="w-4 h-4 text-emerald-500" />
                <h2 className="text-xs font-mono font-bold uppercase tracking-[0.2em]">Payload Buffer / 数据可视化预览</h2>
              </div>
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/50"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/50"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500"></div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Raw String View */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase">
                  <ClipboardCheck className="w-3 h-3" />
                  Raw Parameters Concatenation / 原始参数拼接
                </div>
                <div className="bg-black/40 p-3 rounded-lg border border-slate-700 font-mono text-xs text-indigo-400 break-all leading-relaxed">
                  {payloadPreview.raw}
                </div>
              </div>

              {/* Structured View */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase">
                  <Code className="w-3 h-3" />
                  Structured Transmission Data / 结构化传输信息
                </div>
                <pre className="font-mono text-xs md:text-sm text-emerald-400 whitespace-pre-wrap overflow-x-auto leading-relaxed bg-black/20 p-4 rounded-lg">
                  {payloadPreview.structured}
                </pre>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
                  <Send className="w-3 h-3 text-emerald-500 animate-pulse" />
                  Status: PUSHING_TO_BACKEND
                </div>
                <div className="text-[10px] text-slate-600 font-mono">
                  TIMESTAMP: {new Date().getTime()}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Results Section */}
        {results && (
          <section className="bg-white p-8 rounded-3xl shadow-xl border border-indigo-100 animate-in fade-in slide-in-from-bottom-6 duration-700">
            <div className="flex items-center gap-3 mb-8 border-b border-slate-50 pb-6">
              <div className="bg-emerald-50 p-2.5 rounded-2xl">
                <LayoutGrid className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-800">智能市场分析报告</h2>
                <p className="text-xs text-slate-400 font-medium">Report generated via Gemini 3 AI Engine</p>
              </div>
            </div>
            <div className="prose prose-indigo max-w-none text-slate-600 whitespace-pre-wrap leading-relaxed font-normal text-sm md:text-base">
              {results}
            </div>
          </section>
        )}
      </main>

      <footer className="fixed bottom-4 left-0 right-0 pointer-events-none flex justify-center">
        <div className="bg-white/90 backdrop-blur-md border border-slate-200/50 py-2.5 px-6 rounded-2xl shadow-2xl pointer-events-auto text-[10px] text-slate-400 flex items-center gap-4">
          <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 bg-indigo-400 rounded-full"></span> 自动检索模式已开启</span>
          <span className="w-px h-3 bg-slate-200"></span>
          <span>© 2025 Market Intel Engine</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
