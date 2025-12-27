
const { app, BrowserWindow } = require('electron');
const path = require('path');

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
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
