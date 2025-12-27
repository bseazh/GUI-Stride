
# GUI-Stride 界面行者 - 桌面审计终端

GUI-Stride (界面行者) 是一款专为 MacOS 设计的高端自动化审计与维权监控桌面应用。它集成了实时终端日志、设备状态预览、本地白名单管理以及自动化的审计报告生成功能。

## 🚀 技术栈
- **Frontend:** React 19, Tailwind CSS
- **Icons:** Lucide React
- **Runtime:** Electron (支持 MacOS 原生标题栏融合)
- **AI Engine:** Google Gemini API (可选在线模式)

## 📂 项目结构
- `main.js`: Electron 主进程配置，处理窗口管理。
- `index.html`: 入口 HTML，配置了 Import Map 及核心样式。
- `App.tsx`: 核心业务逻辑与界面布局。
- `constants.tsx`: 预设的 Mock 数据。
- `types.ts`: 全局 TypeScript 接口定义。

## 🛠️ 本地开发环境配置

### 1. 安装依赖
```bash
npm install
```

### 2. 启动开发模式
```bash
npm start
```

### 3. 构建 MacOS 应用 (DMG/Zip)
```bash
npm run dist
```

## 🍎 MacOS 特性说明
- **窗口样式:** 采用了 `hiddenInset` 标题栏，完美适配 MacOS 交通灯按钮。
- **快捷键:** 支持标准 MacOS 剪贴板及窗口快捷键。
- **性能:** 针对 Metal 渲染优化了大量动画平滑度。
