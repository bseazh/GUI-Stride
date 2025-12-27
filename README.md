# GUI-Stride 反盗版自动巡查系统

> **基于 ADB 的智能版权保护系统** —— 自动在小红书等平台识别和举报盗版电子内容

![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Platform](https://img.shields.io/badge/platform-Android-orange.svg)
![React](https://img.shields.io/badge/frontend-React-blue.svg)
![WebSocket](https://img.shields.io/badge/realtime-WebSocket-purple.svg)

---

## 项目简介

**GUI-Stride** 是一个全自动化的反盗版巡查系统。随着数字内容盗版问题日益严重，传统的人工巡查不仅效率低下，而且成本高昂。本系统通过 ADB（Android Debug Bridge）技术控制 Android 手机，能够在小红书等电商平台上**自动搜索、智能识别、一键举报**盗版电子内容。

**核心优势**：
- **全自动化**：从搜索到举报，全程无需人工干预
- **实时监控**：Web 界面实时显示检测进度和日志
- **智能判定**：基于白名单和关键词的双重验证机制
- **证据留存**：自动截图保存，生成结构化举报报告

---

## 一、系统架构

![系统架构图](pic/1.%20整体架构%20(System%20Architecture).jpeg)

GUI-Stride 采用**前后端分离 + 设备控制**的三层架构设计：

### 1.1 前端层 (React Web UI)

前端使用 React + TypeScript 构建，提供用户交互界面：
- **连接状态指示器**：实时显示 WebSocket 连接状态
- **控制面板**：Start/Stop 按钮控制检测任务
- **日志窗口**：滚动显示实时检测日志

### 1.2 后端层 (Python API Server)

后端基于 Python asyncio 实现，负责：
- **WebSocket 服务**：监听 `ws://localhost:8766`，处理前端命令
- **任务调度**：管理检测任务的启动、停止和状态
- **进程管理**：通过 subprocess 启动检测核心程序

### 1.3 设备控制层 (ADB + Android)

通过 ADB 命令直接控制 Android 手机：
- **tap(x, y)**：模拟点击操作
- **swipe()**：模拟滑动操作
- **input_text()**：输入文字（支持中文）
- **screenshot()**：截取屏幕
- **dump_ui_xml()**：获取界面元素树

### 1.4 通信协议

| 通信路径 | 协议 | 用途 |
|---------|------|------|
| 前端 ↔ 后端 | WebSocket | 实时日志推送、命令下发 |
| 前端 → 后端 | HTTP API | 状态查询 |
| 后端 → 手机 | ADB | 设备控制命令 |

---

## 二、核心检测流程

![主检测流程](pic/2.%20核心检测流程%20(Main%20Detection%20Flow).jpg)

系统的核心检测流程分为以下几个阶段：

### 2.1 初始化阶段

1. **检查 ADB 连接** (`check_connection()`)
   - 执行 `adb devices` 确认手机已连接
   - 检测连接状态，失败则终止流程

2. **启动目标 App** (`launch()`)
   - 通过包名启动小红书：`com.xingin.xhs`
   - 等待 App 完全加载

### 2.2 搜索阶段

3. **搜索关键词** (`search(keyword)`)
   - 点击搜索框，输入关键词（如"众合法考"）
   - 使用 ADB Keyboard 解决中文输入问题

4. **切换商品标签**
   - 小红书默认显示笔记，需切换到"商品"标签
   - 通过 UI 元素定位或坐标点击

### 2.3 检测循环

5. **遍历商品列表**
   - 依次点击进入每个商品详情页
   - 提取商品信息：标题、价格、店铺名

6. **判断是否为官方店铺** (`is_official?`)
   - 白名单匹配：检查是否在授权店铺列表中
   - 关键词匹配：店铺名是否包含"官方"字样

7. **执行相应操作**
   - **官方店铺**：跳过，返回列表继续下一个
   - **非官方店铺**：执行举报流程

### 2.4 收尾阶段

8. **保存报告**
   - 生成 JSON 格式的检测报告
   - 包含所有检测商品的详细信息

---

## 三、举报流程详解

![举报流程](pic/3.%20举报流程详解%20(Report%20Flow).jpg)

当系统判定某商品为疑似盗版时，将自动执行以下举报流程：

### 3.1 进入举报入口

**Step 1: 点击分享按钮**
- 在商品详情页底部找到分享按钮
- 通过坐标 `(width, bottom())` 定位并点击

**Step 2: 滑动找举报按钮**
- 分享面板中的举报按钮通常不在首屏
- 需要向左滑动找到"举报"选项

### 3.2 填写举报信息

**Step 3: 选择举报类型**
- 选择"低质/违规商品"类别
- 调用 `report_product` 函数处理

**Step 4: 选择二级原因**
- 进一步细化举报原因
- 如"涉嫌侵权"、"虚假宣传"等

**Step 5: 填写举报描述** (0/200字)
- 调用 `generate_text()` 自动生成三点理由：
  1. **价格异常**：售价远低于正版价格
  2. **分发违规**：未经授权销售数字内容
  3. **资质存疑**：店铺无官方授权证明

### 3.3 提交举报

**Step 6: 上传图片证据**
- 最多上传 3 张截图作为证据
- 包括商品页面、价格信息、店铺信息

**Step 7: 点击提交**
- 确认信息后提交举报
- 系统记录举报状态

举报完成后，系统自动保存报告并返回列表继续检测下一个商品。

---

## 四、代码模块结构

![模块依赖](pic/4.%20模块依赖关系%20(Module%20Dependencies).jpg)

系统采用模块化设计，各模块职责清晰：

### 4.1 主入口 (`run_detection()`)

主函数负责协调各模块，控制整体检测流程。

### 4.2 ADBController

底层设备控制模块，封装所有 ADB 操作：

| 方法 | 功能 |
|------|------|
| `tap(x, y)` | 点击指定坐标 |
| `swipe(x1, y1, x2, y2)` | 滑动操作 |
| `screenshot()` | 截取屏幕 |
| `input_text(text)` | 输入文字 |
| `dump_ui_xml()` | 获取 UI 元素树 |

### 4.3 XiaohongshuCtrl

小红书平台专用控制器，封装平台特定操作：

| 方法 | 功能 |
|------|------|
| `launch()` | 启动小红书 App |
| `search(keyword)` | 搜索关键词 |
| `switch_tab()` | 切换到商品标签 |

### 4.4 ProductExtractor

商品信息提取模块：

| 方法 | 功能 |
|------|------|
| `extract_from()` | 从当前页面提取商品信息 |
| `extract_single_product()` | 处理单个商品的完整流程 |

### 4.5 EvidenceManager

证据管理模块，负责截图和报告的保存：

| 方法 | 功能 |
|------|------|
| `get_shop_dir()` | 获取/创建店铺证据目录 |
| `save_*()` | 保存各类截图 |
| `save_report()` | 保存 JSON 报告 |

---

## 五、盗版判定逻辑

![判定逻辑](pic/5.%20判定逻辑%20(Detection%20Logic).jpeg)

系统采用**双重验证机制**来判断商品是否为正版：

### 5.1 输入信息

检测前需要获取以下商品信息：
- **店铺名**：销售方名称
- **商品价格**：当前售价
- **商品标题**：商品名称和描述

### 5.2 判定流程

#### 第一重：白名单匹配

系统维护一份官方授权店铺白名单，例如：
- "方圆圆众合教育"
- "得到官方旗舰店"
- 其他已验证的正版店铺

如果店铺名**完全匹配**白名单中的任一项，直接判定为**官方店铺**，跳过举报。

#### 第二重：关键词匹配

如果不在白名单中，检查店铺名是否包含以下关键词：
- "官方"
- "旗舰"
- "授权"

包含这些关键词的店铺**可能**是官方店铺，系统会更谨慎处理。

### 5.3 判定结果

| 判定结果 | 处理方式 |
|---------|---------|
| 官方店铺 | 跳过举报，`back()` 返回列表 |
| 非官方店铺 | 执行举报流程 |

### 5.4 举报理由生成

对于非官方店铺，系统调用 `generate_report_text()` 自动生成举报理由，包含三个要点：

1. **价格异常**：该商品售价明显低于正版价格，存在盗版嫌疑
2. **分发违规**：未经版权方授权擅自销售数字内容
3. **资质存疑**：店铺未提供官方授权证明

---

## 六、证据保存结构

![证据结构](pic/6.%20证据保存结构%20(Evidence%20Structure).jpeg)

系统会自动保存完整的检测证据，便于后续追溯和复核。

### 6.1 目录结构

每次检测任务会创建一个独立的证据目录，命名规则为：`时间戳_关键词`

```
test/evidence/
└── 20251228_143000_众合法考/      # 检测任务目录
    ├── report.json                 # 检测报告
    ├── 店铺A名称/                  # 店铺证据目录
    │   ├── 1_商品介绍.png          # 商品标题+价格截图
    │   └── 2_店铺信息.png          # 店铺名称截图
    └── 店铺B名称/
        ├── 1_商品介绍.png
        └── 2_店铺信息.png
```

### 6.2 报告格式 (report.json)

```json
{
  "keyword": "众合法考",
  "timestamp": "20251228_143000",
  "total_shops": 3,
  "shops": [
    {
      "shop_name": "xxx教育资料店",
      "price": 29.9,
      "title": "2025法考全套资料",
      "reported": true
    },
    {
      "shop_name": "方圆圆众合教育",
      "price": 199.0,
      "title": "众合法考官方课程",
      "reported": false
    }
  ]
}
```

### 6.3 截图说明

| 截图类型 | 文件名 | 内容 |
|---------|--------|------|
| 商品介绍 | `1_商品介绍.png` | 商品标题、价格信息 |
| 店铺信息 | `2_店铺信息.png` | 店铺名称、店铺信息 |

---

## 七、前后端通信架构

![前后端通信](pic/7.%20前后端通信%20(Frontend-Backend%20Communication).jpeg)

系统采用 WebSocket 实现前后端实时通信。

### 7.1 前端 (React App.tsx)

前端维护三个核心状态：

| 状态 | 说明 |
|------|------|
| `wsConnected` | WebSocket 连接状态 |
| `Start/Stop` | 检测任务控制 |
| `logs[]` | 实时日志数组 |

**事件处理**：
- `onopen/onclose`：连接状态变化
- `send()`：发送命令到后端
- `onmessage`：接收后端推送的日志

### 7.2 WebSocket 通信

WebSocket 服务运行在 `ws://localhost:8766`，支持以下命令：

| 命令 | 方向 | 功能 |
|------|------|------|
| `start_detection` | 前端 → 后端 | 启动检测任务 |
| `stop_detection` | 前端 → 后端 | 停止检测任务 |
| `ping` | 前端 → 后端 | 心跳检测 |
| `pong` | 后端 → 前端 | 心跳响应 |
| `log` | 后端 → 前端 | 实时日志推送 |

### 7.3 后端 (api_server.py)

后端的 `websocket_handler()` 函数处理所有 WebSocket 消息：

1. 解析收到的命令
2. 根据命令类型执行相应操作：
   - `start_detection`：调用 `subprocess.Popen()` 启动 `test_detection.py`
   - `stop_detection`：终止检测进程
   - `ping`：返回 `pong`
3. 将检测日志实时推送给前端

---

## 八、快速开始

### 8.1 环境要求

**硬件要求**：
- 电脑：macOS / Linux / Windows
- Android 手机：Android 7.0+
- USB 数据线

**软件要求**：
- Python 3.10+
- Node.js 16+
- ADB 工具
- ADB Keyboard（Android 中文输入）

### 8.2 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/GUI-Stride.git
cd GUI-Stride

# 2. 安装后端依赖
cd anti_piracy_system
pip install -r requirements.txt

# 3. 安装前端依赖
cd ../front_end
npm install
```

### 8.3 手机配置

1. 开启开发者模式（连续点击版本号 7 次）
2. 开启 USB 调试
3. 安装并启用 ADB Keyboard
4. USB 连接手机到电脑
5. 手机上点击"允许 USB 调试"

### 8.4 验证连接

```bash
adb devices
# 应显示:
# List of devices attached
# 9c00759f    device
```

### 8.5 启动服务

```bash
# 终端 1: 启动后端
cd anti_piracy_system
python api_server.py

# 终端 2: 启动前端
cd front_end
npm run dev
```

### 8.6 访问界面

打开浏览器访问 `http://localhost:5173`，点击 **Start Detection** 开始检测。

---

## 九、项目结构

```
GUI-Stride/
├── anti_piracy_system/              # 后端核心模块
│   ├── api_server.py                # WebSocket API 服务
│   ├── test_detection.py            # 检测主程序
│   ├── adb_controller.py            # ADB 设备控制
│   ├── xiaohongshu_controller.py    # 小红书平台控制
│   ├── product_extractor.py         # 商品信息提取
│   ├── evidence_manager.py          # 证据管理
│   └── test/evidence/               # 证据存储目录
│
├── front_end/                       # 前端 React 应用
│   ├── App.tsx                      # 主组件
│   ├── index.html                   # 入口页面
│   ├── package.json                 # 依赖配置
│   └── vite.config.ts               # Vite 配置
│
└── pic/                             # 架构流程图
    ├── 1. 整体架构 (System Architecture).jpeg
    ├── 2. 核心检测流程 (Main Detection Flow).jpg
    ├── 3. 举报流程详解 (Report Flow).jpg
    ├── 4. 模块依赖关系 (Module Dependencies).jpg
    ├── 5. 判定逻辑 (Detection Logic).jpeg
    ├── 6. 证据保存结构 (Evidence Structure).jpeg
    └── 7. 前后端通信 (Frontend-Backend Communication).jpeg
```

---

## 十、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React + TypeScript + Vite | 现代化前端框架 |
| 通信 | WebSocket | 实时双向通信 |
| 后端 | Python + asyncio | 异步高性能服务 |
| 设备控制 | ADB | Android 调试桥 |
| 数据存储 | JSON | 轻量级数据格式 |

---

## 十一、注意事项

### 合法合规

1. **仅用于保护自有版权内容**：请确保您拥有相关内容的版权或授权
2. **遵守平台规则**：举报功能依赖平台提供的举报入口
3. **不得滥用**：禁止用于恶意举报或骚扰他人

### 使用建议

1. **首次使用**：建议先在测试模式下运行，确认流程正常
2. **定期更新白名单**：添加新的官方授权店铺
3. **检查证据**：定期查看证据目录，确认截图质量

### 技术限制

1. 小红书 App 更新可能导致 UI 元素变化，需要调整坐标
2. 网络状况可能影响页面加载速度，建议设置合理的等待时间
3. ADB 连接不稳定时，可尝试重新插拔 USB 线

---

## License

MIT License

---

*最后更新: 2025-12-28*
