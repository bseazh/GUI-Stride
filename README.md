# 🛡️ 反盗版自动巡查系统 (Anti-Piracy Patrol System)

> **基于 Open-AutoGLM 的智能版权保护系统** —— 使用多模态 AI 在小红书、闲鱼等平台自动识别和举报盗版内容

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iOS%20%7C%20HarmonyOS-orange.svg)
![AutoGLM](https://img.shields.io/badge/powered%20by-AutoGLM--Phone--9B-blue.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)

---

## 📖 项目简介

**反盗版自动巡查系统**是一个基于 [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) 框架构建的智能 Agent，能够像人类一样操作手机，在小红书、闲鱼、淘宝等电商平台上**自动搜索、识别、举报**盗版电子内容。

### 为什么需要这个系统？

数字内容盗版问题日益严重，传统的人工巡查效率低下且成本高昂。本系统通过以下技术实现全自动化：

- 🤖 **AutoGLM Phone Agent** - 自动控制手机完成复杂操作流程
- 👁️ **多模态 AI 视觉** - 理解屏幕内容，提取商品信息（标题/店铺/价格）
- 🧠 **三层判定机制** - 店铺验证 + 价格分析 + 内容匹配
- 📢 **自动化举报** - 生成举报理由，触发平台举报功能

### 🌟 最新更新 (2025-12-27)

- ✅ **小红书商品提取优化**：自动切换到"商品"标签，支持 AI 视觉识别商品信息
- ✅ **ModelScope API 集成**：开箱即用的模型服务，无需本地部署
- ✅ **智能 JSON 解析**：自动解析多种格式的模型响应
- ✅ **完善文档系统**：提供详细的使用指南和故障排查

---

## ✨ 核心特性

### 🎯 智能检测三层机制

```
第一层: 店铺验证
├─ 检查是否为官方授权店铺
└─ 白名单匹配 → 直接判定为正版

第二层: 价格分析
├─ 比对正版商品价格
├─ 低于 70% 触发警告
└─ 结合其他因素综合判断

第三层: 内容匹配
├─ OCR 提取页面文字
├─ 关键词匹配分析
└─ 相似度计算 (>60% 为疑似)
```

### 🚀 自动化全流程

1. **自动操作手机** - 基于 ADB/HDC，模拟人类操作
2. **平台自适应** - 小红书/闲鱼/淘宝不同流程自动识别
3. **AI 视觉识别** - 使用 AutoGLM-Phone-9B 多模态模型提取商品信息
4. **智能举报** - 生成结构化举报理由，自动提交
5. **证据保存** - 自动截图保存举报证据
6. **统计报告** - 生成详细的巡查和举报统计

### 📱 小红书平台特性（新增）

- ✅ 自动识别并点击"商品"标签
- ✅ AI 视觉模型提取商品标题、店铺名称、价格
- ✅ 智能解析多种 JSON 响应格式
- ✅ 容错处理和备用方案

---

## 🏗️ 系统架构

### 项目结构

```
GUI/
├── Open-AutoGLM/               # AutoGLM 框架（已安装）
│   ├── phone_agent/           # Phone Agent 核心
│   ├── main.py                # AutoGLM 启动脚本
│   └── requirements.txt       # AutoGLM 依赖
│
└── anti_piracy_system/        # 反盗版系统（本项目）
    ├── main_anti_piracy.py        # 🚀 主启动脚本
    ├── anti_piracy_agent.py       # 🤖 Agent 核心逻辑
    │                               #    - AI 视觉提取
    │                               #    - 小红书标签切换
    │                               #    - JSON 智能解析
    ├── piracy_detector.py         # 🔍 三层检测引擎
    ├── product_database.py        # 📚 正版商品数据库
    ├── report_manager.py          # 📢 举报流程管理
    ├── config_anti_piracy.py      # ⚙️  配置和提示词
    │
    ├── data/                      # 数据目录
    │   └── genuine_products.json  # 正版商品数据
    ├── logs/                      # 日志目录
    │   └── report_history.json    # 举报历史记录
    ├── screenshots/               # 证据截图目录
    │
    ├── start_with_modelscope.sh   # 🎯 一键启动脚本
    ├── demo_detection.py          # 📊 检测逻辑演示
    ├── diagnose_model_service.py  # 🔧 诊断工具
    │
    └── 📘 文档
        ├── README.md                          # 详细说明
        ├── QUICK_START.md                     # 快速开始 ⭐
        ├── XIAOHONGSHU_EXTRACTION_GUIDE.md    # 小红书提取指南 ⭐ NEW
        ├── FIXED_README.md                    # 修复说明 ⭐ NEW
        ├── INSTALLATION.md                    # 安装指南
        ├── MODEL_SERVICE_SETUP.md             # 模型配置
        └── TROUBLESHOOTING_502.md             # 故障排查
```

### 技术栈

- **基础框架**: [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)
- **AI 模型**: AutoGLM-Phone-9B (多模态视觉语言模型)
- **模型服务**: ModelScope API (已配置)
- **设备控制**: ADB (Android) / HDC (HarmonyOS) / WebDriverAgent (iOS)
- **语言**: Python 3.10+

---

## 🚀 快速开始 (3 分钟)

### 前提条件

✅ **已完成**（无需操作）:
- Open-AutoGLM 已安装在 `/Users/Apple/Documents/GUI/Open-AutoGLM`
- ModelScope API 已配置在 `.env` 文件中
- Python 依赖已安装在 `venv` 虚拟环境中

⚠️ **需要准备**:
- Android/HarmonyOS 手机 (Android 7.0+ / HarmonyOS NEXT)
- 开启开发者模式和 USB 调试
- 安装 ADB Keyboard (仅 Android，用于中文输入)
- USB 数据线连接手机到电脑

### 极简 3 步启动

```bash
# 1. 进入项目目录
cd /Users/Apple/Documents/GUI/anti_piracy_system

# 2. 检查手机连接
adb devices  # 应显示您的设备

# 3. 启动系统
./start_with_modelscope.sh
```

启动后选择：
- **选项 6** - 运行检测逻辑演示（无需手机，快速了解功能）
- **选项 4** - 测试模式巡查（需要手机，不实际举报）
- **选项 5** - 正式模式巡查（实际执行举报操作）

### 快速测试（无需手机）

想立即看到效果？运行演示程序：

```bash
cd anti_piracy_system
source venv/bin/activate
python demo_detection.py
```

这会展示 5 个测试案例，演示三层检测机制如何工作。

---

## 📋 工作流程

### 小红书平台完整流程（示例）

```
┌─────────────────────────────────────────┐
│  1. 启动小红书应用                        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  2. 搜索关键词 (例如: "得到")             │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  3. ⭐ 点击"商品"标签 (小红书特有)        │
│     → AI 识别标签位置并点击               │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  4. 循环处理每个商品                      │
│     ┌────────────────────────────┐      │
│     │ 4.1 点击进入详情页          │      │
│     └────────┬───────────────────┘      │
│              ↓                           │
│     ┌────────────────────────────┐      │
│     │ 4.2 ⭐ AI 视觉识别          │      │
│     │   - 提取商品标题            │      │
│     │   - 提取店铺名称            │      │
│     │   - 提取价格信息            │      │
│     │   - 提取商品描述/OCR        │      │
│     └────────┬───────────────────┘      │
│              ↓                           │
│     ┌────────────────────────────┐      │
│     │ 4.3 三层检测判定            │      │
│     │   ├─ 店铺验证               │      │
│     │   ├─ 价格分析               │      │
│     │   └─ 内容匹配               │      │
│     └────────┬───────────────────┘      │
│              ↓                           │
│     ┌────────────────────────────┐      │
│     │ 4.4 如果判定为盗版          │      │
│     │   ├─ 生成举报理由           │      │
│     │   ├─ 自动点击举报按钮       │      │
│     │   ├─ 填写举报说明           │      │
│     │   └─ 保存证据截图           │      │
│     └────────┬───────────────────┘      │
│              ↓                           │
│     ┌────────────────────────────┐      │
│     │ 4.5 返回列表，继续下一个     │      │
│     └────────────────────────────┘      │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  5. 生成巡查报告                          │
│     - 检查商品数                          │
│     - 发现盗版数                          │
│     - 成功举报数                          │
│     - 详细检测结果                        │
└─────────────────────────────────────────┘
```

### 三层检测逻辑

```python
# 第一层：店铺验证（最高优先级）
if 店铺名称 in 官方授权列表:
    return "正版" ✅

# 第二层 + 第三层：综合判定
if 店铺名称 not in 官方授权列表 \
   AND 价格 < 正版价格 * 0.7 \
   AND 内容相似度 > 0.6:
    return "盗版" ❌ (置信度: 综合计算)

else:
    return "无法判定" ⚠️
```

---

## 💻 使用方法

### 方法 1: 交互式菜单（推荐）

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
./start_with_modelscope.sh
```

菜单选项：
```
1. 查看数据库统计          - 查看正版商品和举报记录
2. 添加正版商品            - 交互式添加正版商品到数据库
3. 运行诊断测试            - 检查模型服务连接状态
4. 开始巡查(测试模式)      - 不实际举报，推荐首次使用 ⭐
5. 开始巡查(正式模式)      - 实际执行举报操作
6. 运行检测逻辑演示        - 无需手机，演示检测逻辑 ⭐
```

### 方法 2: 命令行直接运行

```bash
cd anti_piracy_system
source venv/bin/activate

# 测试模式（推荐首次使用）
python main_anti_piracy.py \
    --platform xiaohongshu \
    --keyword "得到" \
    --max-items 5 \
    --test-mode

# 正式模式（实际举报）
python main_anti_piracy.py \
    --platform xiaohongshu \
    --keyword "得到课程" \
    --max-items 10

# 指定模型服务（可选，默认使用 .env 配置）
python main_anti_piracy.py \
    --base-url https://api-inference.modelscope.cn/v1 \
    --model "ZhipuAI/AutoGLM-Phone-9B" \
    --apikey "your-api-key" \
    --platform xiaohongshu \
    --keyword "得到"
```

### 方法 3: 查看统计和管理

```bash
# 查看数据库统计
python main_anti_piracy.py --show-stats

# 添加正版商品
python main_anti_piracy.py --add-product

# 导出举报记录
python main_anti_piracy.py --export-report report.txt
```

---

## 📚 文档导航

### 快速入门
- 📘 **[QUICK_START.md](anti_piracy_system/QUICK_START.md)** - 快速开始指南 ⭐ 推荐首先阅读
- 📘 **[XIAOHONGSHU_EXTRACTION_GUIDE.md](anti_piracy_system/XIAOHONGSHU_EXTRACTION_GUIDE.md)** - 小红书商品提取详解 ⭐ NEW
- 📘 **[FIXED_README.md](anti_piracy_system/FIXED_README.md)** - 系统修复说明 ⭐ NEW

### 安装配置
- 📘 **[INSTALLATION.md](anti_piracy_system/INSTALLATION.md)** - 虚拟环境配置
- 📘 **[MODEL_SERVICE_SETUP.md](anti_piracy_system/MODEL_SERVICE_SETUP.md)** - 模型服务配置详解
- 📘 **[API_CONFIGURED.md](anti_piracy_system/API_CONFIGURED.md)** - ModelScope API 配置说明

### 故障排查
- 🔧 **[TROUBLESHOOTING_502.md](anti_piracy_system/TROUBLESHOOTING_502.md)** - 502 错误解决方案
- 🔧 **诊断工具**: `python diagnose_model_service.py`

### 项目文档
- 📘 **[PROJECT_SUMMARY.md](anti_piracy_system/PROJECT_SUMMARY.md)** - 项目总体说明
- 📘 **[anti_piracy_system/README.md](anti_piracy_system/README.md)** - 详细技术文档

---

## 🎯 支持的平台

| 平台 | 平台键名 | App 包名 | 特殊处理 |
|------|---------|---------|---------|
| 小红书 | `xiaohongshu` | `com.xingin.xhs` | ✅ 自动切换商品标签 |
| 闲鱼 | `xianyu` | `com.taobao.idlefish` | - |
| 淘宝 | `taobao` | `com.taobao.taobao` | - |

---

## 🔧 环境要求

### 硬件要求
- 💻 **电脑**: macOS / Linux / Windows
- 📱 **手机**:
  - Android 7.0+ 或
  - HarmonyOS NEXT+ 或
  - iOS 13+ (需额外配置 WebDriverAgent)
- 🔌 **数据线**: 支持数据传输的 USB 线

### 软件要求
- 🐍 **Python**: 3.10 或更高版本
- 🔧 **ADB Tools**:
  - Android: `adb` (已通过 Homebrew 安装)
  - HarmonyOS: `hdc`
  - iOS: WebDriverAgent
- ⌨️ **ADB Keyboard**: 仅 Android 需要（用于中文输入）

### 手机配置清单
```
✅ 1. 开启开发者模式（连续点击版本号 7 次）
✅ 2. 开启 USB 调试
✅ 3. 开启 USB 调试（安全设置）- 部分机型需要
✅ 4. 安装并启用 ADB Keyboard - 仅 Android
✅ 5. 用 USB 线连接到电脑
✅ 6. 手机上点击"允许 USB 调试"
```

验证连接：
```bash
adb devices
# 应显示:
# List of devices attached
# 9c00759f    device  ✅
```

---

## 🌟 技术亮点

### 1. AI 视觉商品信息提取

使用 AutoGLM-Phone-9B 多模态模型直接识别屏幕内容：

```python
# 让 AI 识别商品详情页
task = """
当前在商品详情页,请识别并提取:
1. 商品标题
2. 店铺名称
3. 商品价格
4. 商品描述

以 JSON 格式返回
"""

response = agent.run(task)
# 返回: {"title": "商品名", "shop_name": "店铺", "price": "99.9", ...}
```

### 2. 智能 JSON 解析

支持多种响应格式：
- ✅ 纯 JSON: `{"title": "..."}`
- ✅ 代码块: ` ```json {...} ``` `
- ✅ 混合文本: `商品信息如下: {"title": ...}`

### 3. 小红书平台自适应

自动识别平台并执行特定流程：

```python
if platform == "xiaohongshu":
    # 自动点击"商品"标签
    agent.run("点击商品标签")
    # AI 提取商品信息
    info = extract_with_ai_vision()
```

### 4. 三层检测机制

```
店铺验证（100% 准确）
    ↓ (如果非官方)
价格分析（异常检测）
    ↓ (如果价格低)
内容匹配（相似度计算）
    ↓
综合置信度判定
```

---

## 📊 使用示例和预期输出

### 测试模式运行

```bash
$ python main_anti_piracy.py --platform xiaohongshu --keyword "得到" --max-items 3 --test-mode

============================================================
🛡️  反盗版自动巡查系统
============================================================
平台: 小红书
关键词: 得到
最大检查数: 3
运行模式: 🧪 测试模式
模型: ZhipuAI/AutoGLM-Phone-9B
API 地址: https://api-inference.modelscope.cn/v1
============================================================

🚀 启动 小红书 并搜索'得到'...
✅ 应用启动和搜索完成

📱 小红书平台：切换到商品标签...
✅ 已切换到商品标签

--- 检查第 1/3 个商品 ---
📋 提取第 1 个商品信息...
   使用AI视觉模型识别页面内容...
   模型响应: {"title": "薛兆丰经济学讲义", "shop_name": "某店铺", "price": "29.9"}
✅ 成功提取商品信息:
   标题: 薛兆丰经济学讲义
   店铺: 某店铺
   价格: ¥29.9

🔍 检测商品: 薛兆丰经济学讲义
❌ 检测到疑似盗版! (置信度: 85%)
   判定依据:
   - 店铺"某店铺"不在官方授权列表中
   - 价格¥29.9，仅为官方价格¥199.0的15%
   - 商品内容与正版高度相似

⚠️  测试模式:跳过实际举报操作

============================================================
✅ 巡查完成!
============================================================
检查商品数: 3
发现疑似盗版: 2
已举报数: 2 (测试模式)
============================================================
```

---

## ⚠️ 注意事项

### 合法合规使用
- ✅ 仅用于保护自有版权内容
- ✅ 确保举报对象确实侵权
- ❌ 不得用于恶意举报或骚扰他人
- ❌ 不得泄露个人隐私信息

### 安全建议
- 🔒 首次使用建议启用测试模式
- 🔒 定期备份正版商品数据库
- 🔒 妥善保管 API Key 和配置文件
- 🔒 不确定时进行人工复核

### 技术限制
- ⚠️ AI 识别准确率受页面质量影响
- ⚠️ 部分平台 UI 更新可能需要适配
- ⚠️ 举报功能依赖平台提供的举报入口

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献方向
- 🎯 新平台适配（拼多多、京东等）
- 🎯 提升 AI 识别准确率
- 🎯 优化检测逻辑
- 🎯 改进文档和示例

### 提交流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证 (License)

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

⚠️ **免责声明**: 本项目仅供学习和研究使用。使用本系统时请遵守相关法律法规和平台规则。作者不对使用本系统造成的任何后果负责。

---

## 🙏 致谢

- 🌟 **[Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)** - 提供强大的 Phone Agent 框架
- 🌟 **[AutoGLM-Phone-9B](https://huggingface.co/zai-org/AutoGLM-Phone-9B)** - 多模态视觉语言模型
- 🌟 **[ModelScope](https://modelscope.cn)** - 提供便捷的模型推理服务

---

## 📞 技术支持

- 📧 **问题反馈**: 提交 GitHub Issue
- 📚 **文档**: 查看 [anti_piracy_system/](anti_piracy_system/) 目录下的详细文档
- 🔧 **诊断工具**: `python anti_piracy_system/diagnose_model_service.py`

---

**🛡️ 守护原创，智驱维权 - 让 AI 为版权保护赋能！**

*最后更新: 2025-12-27*
