
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    titleBarStyle: 'hiddenInset', // 经典的 MacOS 原生标题栏嵌入效果
    backgroundColor: '#0F172A',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // 加载本地入口文件
  win.loadFile('index.html');

  // 生产环境下关闭开发者工具
  // win.webContents.openDevTools();

  return win;
}

// Python 反盗版系统路径
const PYTHON_SYSTEM_PATH = path.join(__dirname, '../anti_piracy_system');
const MAIN_PYTHON_SCRIPT = path.join(PYTHON_SYSTEM_PATH, 'main_anti_piracy.py');

// 存储运行中的进程
let currentPythonProcess = null;

// 启动 Python 反盗版巡查
function startAntiPiracyPatrol(win, options) {
  if (currentPythonProcess) {
    win.webContents.send('python-log', { type: 'error', message: '已有任务正在运行，请等待完成' });
    return false;
  }

  const args = [
    MAIN_PYTHON_SCRIPT,
    '--platform', options.platform,
    '--keyword', options.keyword,
    '--max-items', options.maxItems.toString()
  ];

  if (options.testMode) {
    args.push('--test-mode');
  }

  if (options.deviceId) {
    args.push('--device-id', options.deviceId);
  }

  win.webContents.send('python-log', { type: 'info', message: `启动 Python 进程: python ${args.join(' ')}` });

  currentPythonProcess = spawn('python', args, {
    cwd: PYTHON_SYSTEM_PATH,
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // 捕获标准输出
  currentPythonProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output) {
      win.webContents.send('python-log', { type: 'output', message: output });
    }
  });

  // 捕获标准错误
  currentPythonProcess.stderr.on('data', (data) => {
    const error = data.toString().trim();
    if (error) {
      win.webContents.send('python-log', { type: 'error', message: error });
    }
  });

  // 进程退出
  currentPythonProcess.on('close', (code) => {
    win.webContents.send('python-log', { type: 'info', message: `进程退出，代码: ${code}` });
    currentPythonProcess = null;
  });

  currentPythonProcess.on('error', (err) => {
    win.webContents.send('python-log', { type: 'error', message: `进程启动失败: ${err.message}` });
    currentPythonProcess = null;
  });

  return true;
}

// 停止当前进程
function stopCurrentProcess(win) {
  if (currentPythonProcess) {
    win.webContents.send('python-log', { type: 'warning', message: '正在停止当前进程...' });
    currentPythonProcess.kill('SIGTERM');
    currentPythonProcess = null;
    return true;
  }
  return false;
}

// 获取正版商品数据库
function getProductDatabase() {
  const dbPath = path.join(PYTHON_SYSTEM_PATH, 'data/genuine_products.json');
  try {
    if (fs.existsSync(dbPath)) {
      const data = fs.readFileSync(dbPath, 'utf-8');
      return JSON.parse(data);
    }
    return {};
  } catch (err) {
    console.error('读取数据库失败:', err);
    return {};
  }
}

// 添加正版商品到数据库
function addProductToDatabase(productData) {
  const dbPath = path.join(PYTHON_SYSTEM_PATH, 'data/genuine_products.json');
  try {
    let database = {};
    if (fs.existsSync(dbPath)) {
      const data = fs.readFileSync(dbPath, 'utf-8');
      database = JSON.parse(data);
    }

    const productId = productData.product_id || `product_${Date.now()}`;
    const product = {
      product_id: productId,
      product_name: productData.product_name,
      shop_name: productData.shop_name,
      official_shops: productData.official_shops || [],
      original_price: parseFloat(productData.original_price) || 0,
      platform: productData.platform || '其他',
      category: productData.category || '其他',
      description: productData.description || '',
      keywords: productData.keywords || [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    database[productId] = product;

    fs.writeFileSync(dbPath, JSON.stringify(database, null, 2), 'utf-8');
    return { success: true, productId };
  } catch (err) {
    console.error('添加商品失败:', err);
    return { success: false, error: err.message };
  }
}

// 删除正版商品
function deleteProductFromDatabase(productId) {
  const dbPath = path.join(PYTHON_SYSTEM_PATH, 'data/genuine_products.json');
  try {
    if (!fs.existsSync(dbPath)) {
      return { success: false, error: '数据库不存在' };
    }

    const data = fs.readFileSync(dbPath, 'utf-8');
    const database = JSON.parse(data);

    if (!database[productId]) {
      return { success: false, error: '商品不存在' };
    }

    delete database[productId];
    fs.writeFileSync(dbPath, JSON.stringify(database, null, 2), 'utf-8');
    return { success: true };
  } catch (err) {
    console.error('删除商品失败:', err);
    return { success: false, error: err.message };
  }
}

// 获取举报记录数据库
function getReportDatabase() {
  const reportPath = path.join(PYTHON_SYSTEM_PATH, 'logs/report_history.json');
  try {
    if (fs.existsSync(reportPath)) {
      const data = fs.readFileSync(reportPath, 'utf-8');
      return JSON.parse(data);
    }
    return {};
  } catch (err) {
    console.error('读取举报记录失败:', err);
    return {};
  }
}

// 获取系统统计信息
function getSystemStatistics() {
  try {
    const productDb = getProductDatabase();
    const reportDb = getReportDatabase();

    // 产品数据库统计
    const productStats = {
      total_products: Object.keys(productDb).length,
      platforms: {},
      categories: {}
    };

    Object.values(productDb).forEach(product => {
      productStats.platforms[product.platform] = (productStats.platforms[product.platform] || 0) + 1;
      productStats.categories[product.category] = (productStats.categories[product.category] || 0) + 1;
    });

    // 举报记录统计
    const reportStats = {
      total_reports: Object.keys(reportDb).length,
      by_platform: {},
      by_status: {}
    };

    Object.values(reportDb).forEach(report => {
      reportStats.by_platform[report.platform] = (reportStats.by_platform[report.platform] || 0) + 1;
      reportStats.by_status[report.report_status] = (reportStats.by_status[report.report_status] || 0) + 1;
    });

    return {
      product_stats: productStats,
      report_stats: reportStats
    };
  } catch (err) {
    console.error('获取统计信息失败:', err);
    return { product_stats: {}, report_stats: {} };
  }
}

// 导出举报记录
function exportReports(format = 'json', outputPath = null) {
  try {
    const reportDb = getReportDatabase();

    if (outputPath) {
      if (format === 'json') {
        fs.writeFileSync(outputPath, JSON.stringify(reportDb, null, 2), 'utf-8');
      } else if (format === 'txt') {
        let txtContent = '';
        Object.values(reportDb).forEach(report => {
          txtContent += `=== 举报摘要 ===\n`;
          txtContent += `举报ID: ${report.report_id}\n`;
          txtContent += `平台: ${report.platform}\n`;
          txtContent += `商品标题: ${report.target_title}\n`;
          txtContent += `店铺名称: ${report.target_shop}\n`;
          txtContent += `商品价格: ¥${report.target_price}\n`;
          txtContent += `举报状态: ${report.report_status}\n`;
          txtContent += `举报时间: ${report.reported_at}\n\n`;
          txtContent += `举报理由:\n${report.report_reason}\n\n`;
          txtContent += `证据截图数量: ${report.evidence_screenshots ? report.evidence_screenshots.length : 0}\n`;
          txtContent += '='.repeat(50) + '\n\n';
        });
        fs.writeFileSync(outputPath, txtContent, 'utf-8');
      }
      return { success: true, path: outputPath };
    } else {
      // 返回数据供前端下载
      if (format === 'json') {
        return { success: true, data: JSON.stringify(reportDb, null, 2), format: 'json' };
      } else {
        let txtContent = '';
        Object.values(reportDb).forEach(report => {
          txtContent += `=== 举报摘要 ===\n`;
          txtContent += `举报ID: ${report.report_id}\n`;
          txtContent += `平台: ${report.platform}\n`;
          txtContent += `商品标题: ${report.target_title}\n`;
          txtContent += `店铺名称: ${report.target_shop}\n`;
          txtContent += `商品价格: ¥${report.target_price}\n`;
          txtContent += `举报状态: ${report.report_status}\n`;
          txtContent += `举报时间: ${report.reported_at}\n\n`;
          txtContent += `举报理由:\n${report.report_reason}\n\n`;
          txtContent += `证据截图数量: ${report.evidence_screenshots ? report.evidence_screenshots.length : 0}\n`;
          txtContent += '='.repeat(50) + '\n\n';
        });
        return { success: true, data: txtContent, format: 'txt' };
      }
    }
  } catch (err) {
    console.error('导出举报记录失败:', err);
    return { success: false, error: err.message };
  }
}

// 获取系统配置（支持的平台等）
function getSystemConfig() {
  const configPath = path.join(PYTHON_SYSTEM_PATH, 'config_anti_piracy.py');
  try {
    // 读取配置文件并提取支持的平台信息
    if (fs.existsSync(configPath)) {
      const data = fs.readFileSync(configPath, 'utf-8');
      // 简单解析支持的平台
      const platforms = {
        xiaohongshu: { name: '小红书', enabled: true },
        xianyu: { name: '闲鱼', enabled: true },
        taobao: { name: '淘宝', enabled: true }
      };
      return { platforms };
    }
    return { platforms: {} };
  } catch (err) {
    console.error('读取系统配置失败:', err);
    return { platforms: {} };
  }
}

// 设置 IPC 通信
function setupIPC(win) {
  // 启动巡查任务
  ipcMain.on('start-patrol', (event, options) => {
    startAntiPiracyPatrol(win, options);
  });

  // 停止巡查任务
  ipcMain.on('stop-patrol', () => {
    stopCurrentProcess(win);
  });

  // 获取数据库
  ipcMain.handle('get-product-database', () => {
    return getProductDatabase();
  });

  // 添加商品
  ipcMain.handle('add-product', (event, productData) => {
    return addProductToDatabase(productData);
  });

  // 删除商品
  ipcMain.handle('delete-product', (event, productId) => {
    return deleteProductFromDatabase(productId);
  });

  // 检查进程状态
  ipcMain.handle('check-process-status', () => {
    return { running: currentPythonProcess !== null };
  });

  // 获取举报记录数据库
  ipcMain.handle('get-report-database', () => {
    return getReportDatabase();
  });

  // 获取系统统计信息
  ipcMain.handle('get-statistics', () => {
    return getSystemStatistics();
  });

  // 导出举报记录
  ipcMain.handle('export-reports', (event, { format, outputPath }) => {
    return exportReports(format, outputPath);
  });

  // 获取系统配置
  ipcMain.handle('get-system-config', () => {
    return getSystemConfig();
  });
}

app.whenReady().then(() => {
  const win = createWindow();
  setupIPC(win);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      const newWin = createWindow();
      setupIPC(newWin);
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
