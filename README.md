# GUI-Stride 反盗版自动巡查系统

> **基于 ADB 的智能版权保护系统** —— 自动在小红书等平台识别和举报盗版内容

![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Platform](https://img.shields.io/badge/platform-Android-orange.svg)
![React](https://img.shields.io/badge/frontend-React-blue.svg)
![WebSocket](https://img.shields.io/badge/realtime-WebSocket-purple.svg)

---

## 项目简介

**GUI-Stride** 是一个全自动化的反盗版巡查系统，通过 ADB 控制 Android 手机，在小红书等电商平台上**自动搜索、识别、举报**盗版电子内容。系统提供 Web 界面实时监控检测进度。

---

## 系统架构

![系统架构图](pic/1.%20整体架构%20(System%20Architecture).jpeg)

系统由四个核心部分组成：

| 组件 | 技术栈 | 功能 |
|------|--------|------|
| **前端 Web UI** | React | 实时日志显示、检测控制 |
| **API Server** | Python | WebSocket 通信、任务调度 |
| **Detection Core** | Python | 核心检测逻辑 |
| **Android Phone** | ADB | 执行实际操作 |

**通信方式**：
- 前端 ↔ 后端：WebSocket (实时日志/控制)
- 前端 ↔ 后端：HTTP API (状态查询)
- 后端 → 手机：ADB Commands

---

## 核心检测流程

![主检测流程](pic/2.%20核心检测流程%20(Main%20Detection%20Flow).jpg)

完整的检测流程：

```
开始
  │
  ├─ 1. 检查ADB连接 check_connection()
  │      ↓ 成功
  ├─ 2. 启动小红书App launch()
  │
  ├─ 3. 搜索关键词 search(keyword)
  │      例如："众合法考"
  │
  ├─ 4. 切换商品标签 (循环处理)
  │      │
  │      └─ 6. 点击进入 tap(位置)
  │             │
  │             ├─ 8. 判断店铺信息 is_official?
  │             │      │
  │             │      ├─ 是官方店铺 → 跳过举报 back()
  │             │      │
  │             │      └─ 非官方 → 9. 执行举报流程 report_product
  │             │
  │             └─ 11. 下一个? ─完成─→ 保存报告 → 结束
```

---

## 举报流程详解

![举报流程](pic/3.%20举报流程详解%20(Report%20Flow).jpg)

当检测到盗版商品时，系统自动执行举报：

| 步骤 | 操作 | 说明 |
|------|------|------|
| Step 1 | 点击分享按钮 | 定位到屏幕底部 |
| Step 2 | 滑动找举报按钮 | 在分享面板中查找 |
| Step 3 | 选择举报原因 | 选择低质类型 |
| Step 4 | 选择二级原因 | 细化举报原因 |
| Step 5 | 填写举报描述 | 自动生成三点理由 (0/200字) |
| Step 6 | 上传图片证据 | 最多3张截图 |
| Step 7 | 点击提交 | 完成举报 |

举报完成后自动保存报告。

---

## 代码模块结构

![模块依赖](pic/4.%20模块依赖关系%20(Module%20Dependencies).jpg)

```
run_detection() 主入口函数
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ADBController│  │XiaohongshuCtrl│ │EvidenceManager│
├─────────────┤  ├──────────────┤  ├──────────────┤
│- tap()      │  │- launch()    │  │- get_shop_dir()│
│- swipe()    │  │- search()    │  │- save_*()      │
│- screenshot()│ │- switch_tab()│  │- save_report() │
│- input_text()│ └──────┬───────┘  └───────────────┘
│- dump_ui_xml()│       │
└─────────────┘         ▼
              ┌─────────────────┐
              │ProductExtractor │
              │- extract_from() │
              └────────┬────────┘
                       ▼
              ┌─────────────────────┐
              │extract_single_product│
              │   处理单个商品        │
              └─────────────────────┘
```

---

## 盗版判定逻辑

![判定逻辑](pic/5.%20判定逻辑%20(Detection%20Logic).jpeg)

```
        商品信息
        - 店铺名
        - 商品价格
        - 商品标题
             │
             ▼
    is_official_shop()
       官方店铺判断
        ╱        ╲
       ▼          ▼
┌─────────────┐  ┌─────────────┐
│ 白名单匹配   │  │ 关键词匹配   │
│方圆圆众合教育│  │店铺名包含"官方"│
└──────┬──────┘  └──────┬──────┘
       │                │
       ▼                ▼
  官方店铺           非官方店铺
  跳过举报           执行举报
                       │
                       ▼
            generate_report_text()
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  1. 价格异常     2. 分发违规     3. 资质存疑
```

**判定规则**：
- 白名单店铺（如"方圆圆众合教育"）→ 跳过
- 店铺名包含"官方"关键词 → 跳过
- 其他店铺 → 生成三点举报理由并举报

---

## 证据保存结构

![证据结构](pic/6.%20证据保存结构%20(Evidence%20Structure).jpeg)

每次检测自动保存完整证据：

```
test/evidence/
└── 20251228_143000_众合法考/     ← 时间戳_关键词
    │
    ├── report.json               ← 检测报告 (JSON)
    │   {
    │     "keyword": "众合法考",
    │     "timestamp": "20251228_143000",
    │     "total_shops": 3,
    │     "shops": [
    │       {
    │         "shop_name": "xxx",
    │         "price": 29.9,
    │         "title": "xxx",
    │         "reported": true
    │       }
    │     ]
    │   }
    │
    ├── 店铺A名称/
    │   ├── 1_商品介绍.png        ← 商品标题+价格截图
    │   └── 2_店铺信息.png        ← 店铺名称截图
    │
    └── 店铺C名称/
        ├── 1_商品介绍.png        ← 店铺名称截图
        └── 2_店铺信息.png
```

---

## 前后端通信架构

![前后端通信](pic/7.%20前后端通信%20(Frontend-Backend%20Communication).jpeg)

```
┌─────────────────────────────────────────────────┐
│           前端 (React App.tsx)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │连接状态   │ │控制按钮   │ │日志窗口   │        │
│  │wsConnected│ │Start/Stop│ │logs[]    │        │
│  └─────┬────┘ └────┬─────┘ └────┬─────┘        │
│        │ onopen    │ send()     │ onmessage    │
│        │ onclose   │            │              │
└────────┴───────────┴────────────┴──────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   WebSocket     │
            │ws://localhost:8766│
            └────────┬────────┘
                     │
┌────────────────────┴────────────────────────────┐
│           后端 (api_server.py)                   │
│                                                  │
│  websocket_handler()                            │
│  ┌────────────────────────────────────────┐    │
│  │command: "start_detection" → start_detection()│
│  │command: "stop_detection"  → stop_detection() │
│  │command: "ping"            → pong             │
│  └─────────────────────┬──────────────────┘    │
│                        │                        │
│              subprocess.Popen()                 │
│                        │                        │
│                        ▼                        │
│              ┌─────────────────┐               │
│              │test_detection.py│               │
│              └─────────────────┘               │
└─────────────────────────────────────────────────┘
```

**WebSocket 命令**：
| 命令 | 功能 |
|------|------|
| `start_detection` | 启动检测任务 |
| `stop_detection` | 停止检测任务 |
| `ping` | 心跳检测 |

---

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
cd anti_piracy_system
pip install -r requirements.txt

# 前端依赖
cd front_end
npm install
```

### 2. 连接手机

```bash
# 检查 ADB 连接
adb devices
# 应显示:
# List of devices attached
# 9c00759f    device
```

### 3. 启动服务

```bash
# 终端1: 启动后端 API 服务
cd anti_piracy_system
python api_server.py

# 终端2: 启动前端
cd front_end
npm run dev
```

### 4. 访问 Web 界面

打开浏览器访问 `http://localhost:5173`，点击 "Start Detection" 开始检测。

---

## 项目结构

```
GUI/
├── anti_piracy_system/          # 后端核心
│   ├── api_server.py            # WebSocket API 服务
│   ├── test_detection.py        # 检测主程序
│   ├── adb_controller.py        # ADB 控制器
│   ├── xiaohongshu_controller.py # 小红书操作
│   ├── product_extractor.py     # 商品信息提取
│   └── evidence_manager.py      # 证据管理
│
├── front_end/                   # 前端 React 应用
│   ├── App.tsx                  # 主组件
│   ├── index.html               # 入口页面
│   └── package.json             # 依赖配置
│
└── pic/                         # 流程图
    ├── 1. 整体架构.jpeg
    ├── 2. 核心检测流程.jpg
    ├── 3. 举报流程详解.jpg
    ├── 4. 模块依赖关系.jpg
    ├── 5. 判定逻辑.jpeg
    ├── 6. 证据保存结构.jpeg
    └── 7. 前后端通信.jpeg
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + TypeScript + Vite |
| 通信 | WebSocket (实时) + HTTP API |
| 后端 | Python + asyncio |
| 设备控制 | ADB (Android Debug Bridge) |
| 数据存储 | JSON 文件 |

---

## 注意事项

1. **合法使用**：仅用于保护自有版权内容
2. **测试模式**：首次使用建议先在测试模式下运行
3. **手机配置**：确保开启 USB 调试和 ADB Keyboard

---

## License

MIT License

---

*最后更新: 2025-12-28*
