# 反盗版自动巡查系统

基于 Open-AutoGLM 框架构建的智能反盗版系统，用于识别和举报小红书、闲鱼等平台上的盗版电子内容。

## 功能特性

- **智能检测**: 基于多模态 AI 模型自动识别疑似盗版商品
- **三层判断机制**:
  - 店铺名称匹配（官方授权验证）
  - 价格比对（低于原价 70% 触发警告）
  - 内容识别（基于 OCR 和图像分析）
- **自动举报**: 自动触发平台内举报功能
- **数据管理**: 正版商品数据库和举报记录系统
- **证据保存**: 自动保存举报证据截图

## 项目结构

```
anti_piracy_system/
├── main_anti_piracy.py       # 主启动脚本（AI Agent 模式）
├── anti_piracy_agent.py      # 反盗版 Agent 主类
├── product_database.py       # 正版商品数据库管理
├── piracy_detector.py        # 盗版识别引擎
├── report_manager.py         # 举报流程管理
├── config_anti_piracy.py     # 系统配置
├── .env                      # API 配置文件
├── data/
│   └── genuine_products.json # 正版商品数据库
├── logs/
│   └── report_history.json   # 举报记录
├── screenshots/              # 证据截图
└── test/
    ├── test_detection.py     # ADB 自动化检测脚本（推荐）
    ├── evidence/             # 证据保存目录
    └── debug/                # 调试信息目录
```

## 环境要求

### 硬件
- Android 手机（Android 7.0+）或鸿蒙设备
- USB 数据线
- 电脑（macOS/Linux/Windows）

### 软件
- Python 3.10+
- ADB 工具
- Open-AutoGLM 框架

## 快速开始

### 1. 安装依赖

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system

# 创建并激活虚拟环境（已完成）
source venv/bin/activate

# 安装依赖（已完成）
pip install -r requirements.txt
```

### 2. 配置 API

系统已配置 ModelScope API，配置文件位于 `.env`：

```bash
PHONE_AGENT_BASE_URL=https://api-inference.modelscope.cn/v1
PHONE_AGENT_MODEL=ZhipuAI/AutoGLM-Phone-9B
PHONE_AGENT_API_KEY=your-api-key
```

### 3. 配置手机

1. **开启开发者模式**: 设置 → 关于手机 → 连续点击版本号 7 次
2. **开启 USB 调试**: 设置 → 开发者选项 → USB 调试
3. **安装 ADB Keyboard**（Android）: [下载地址](https://github.com/senzhk/ADBKeyBoard)
4. **验证连接**:
   ```bash
   adb devices
   ```

### 4. 运行系统

系统提供两种运行模式：

#### 模式一：ADB 自动化检测（推荐）

使用 `test/test_detection.py` 脚本，通过 ADB 直接控制手机进行自动化检测和举报。

```bash
# 激活环境
source venv/bin/activate

# 仅检测（不举报），检测3个商品
python test/test_detection.py -n 3

# 检测并自动举报
python test/test_detection.py -n 5 --report

# 指定搜索关键词
python test/test_detection.py -n 3 -k "得到" --report

# 调试模式（保存 UI XML 用于分析）
python test/test_detection.py -n 1 --report --debug
```

#### 模式二：AI Agent 模式

使用 `main_anti_piracy.py`，基于 Open-AutoGLM 的 AI Agent 进行智能检测。

```bash
# 激活环境
source venv/bin/activate

# 查看数据库统计
python main_anti_piracy.py --show-stats

# 测试模式（不实际举报）
python main_anti_piracy.py --platform xiaohongshu --keyword "得到" --test-mode

# 正式模式
python main_anti_piracy.py --platform xiaohongshu --keyword "得到"
```

## ADB 自动化检测流程详解

`test/test_detection.py` 是推荐使用的检测脚本，完整流程如下：

### 整体流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      ADB 自动化检测流程                           │
├─────────────────────────────────────────────────────────────────┤
│  1. 连接设备    →  2. 启动小红书  →  3. 搜索关键词                  │
│       ↓                                                         │
│  4. 切换商品Tab →  5. 遍历商品列表  →  6. 进入商品详情               │
│       ↓                                                         │
│  7. 截图取证    →  8. 提取信息     →  9. 判断是否官方店铺            │
│       ↓                                                         │
│  10. 执行举报（可选） → 11. 返回列表  →  12. 继续下一个商品          │
│       ↓                                                         │
│  13. 保存报告   →  完成                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 详细步骤

#### 步骤 1-4：初始化

1. **检查 ADB 连接** - 自动检测已连接的设备
2. **启动小红书 App** - 强制停止后重新启动，确保干净状态
3. **搜索关键词** - 点击搜索框，输入关键词（如"众合法考"）
4. **切换商品标签** - 从默认的笔记页切换到商品列表页

#### 步骤 5-9：商品检测循环

对每个商品执行：

5. **点击商品** - 根据双列布局计算点击位置
6. **截图商品介绍** - 截取包含标题和价格的页面
7. **向下滑动** - 滑动到店铺信息区域
8. **截图店铺信息** - 截取包含店铺名称的页面
9. **提取信息** - 解析 UI XML 获取：
   - 商品标题
   - 商品价格
   - 店铺名称

#### 步骤 10：举报流程（启用 `--report` 时）

```
举报流程:
┌────────────────────────────────────────────────────────────┐
│  1. 判断店铺     如果是官方店铺 → 跳过举报                    │
│       ↓                                                    │
│  2. 点击分享     点击右上角分享按钮                          │
│       ↓                                                    │
│  3. 找举报入口   在分享面板向左滑动找到"举报"按钮             │
│       ↓                                                    │
│  4. 选择类型     选择"假货/低质/山寨商品举报"                 │
│       ↓                                                    │
│  5. 选择原因     选择"盗版图书音像制品类"                     │
│       ↓                                                    │
│  6. 填写说明     自动生成并填写举报文本（200字以内）           │
│       ↓                                                    │
│  7. 上传图片     从相册选择刚截取的证据图片                   │
│       ↓                                                    │
│  8. 提交举报     点击提交按钮完成举报                        │
└────────────────────────────────────────────────────────────┘
```

#### 步骤 11-13：收尾

11. **返回列表** - 按返回键回到商品列表
12. **翻页处理** - 每处理4个商品后自动向上滑动加载更多
13. **保存报告** - 生成 JSON 格式的检测报告

### 证据保存结构

```
test/evidence/
└── 20251227_143000_众合法考/          # 时间戳_关键词
    ├── report.json                     # 检测报告
    ├── 店铺A名称/
    │   ├── 1_商品介绍.png              # 商品标题+价格截图
    │   └── 2_店铺信息.png              # 店铺名称截图
    ├── 店铺B名称/
    │   ├── 1_商品介绍.png
    │   └── 2_店铺信息.png
    └── ...
```

### 官方店铺白名单

以下店铺会自动跳过举报：

```python
OFFICIAL_SHOPS = [
    "方圆众合教育",
    "众合教育旗舰店",
    "众合法考官方",
    "众合教育官方店",
]
```

包含"官方"且与关键词相关的店铺也会被识别为官方店铺。

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-n, --num` | 检测商品数量 | 3 |
| `-k, --keyword` | 搜索关键词 | 众合法考 |
| `--device` | 指定设备 ID | 自动检测 |
| `--report` | 启用自动举报 | 关闭 |
| `--debug` | 调试模式 | 关闭 |
| `--mock` | Mock 测试（无需设备） | 关闭 |
| `--debug-report-page` | 调试举报页面 | 关闭 |

## 使用方法

### 添加正版商品

```bash
python main_anti_piracy.py --add-product
```

### 查看统计信息

```bash
python main_anti_piracy.py --show-stats
```

### 导出举报记录

```bash
python main_anti_piracy.py --export-report report.txt
```

### AI Agent 完整命令选项

```bash
python main_anti_piracy.py \
  --platform xiaohongshu \    # 目标平台: xiaohongshu/xianyu/taobao
  --keyword "得到" \          # 搜索关键词
  --max-items 10 \            # 最多检查商品数
  --test-mode                 # 测试模式（可选）
```

## 支持的平台

| 平台 | 键名 | App 包名 |
|------|------|----------|
| 小红书 | xiaohongshu | com.xingin.xhs |
| 闲鱼 | xianyu | com.taobao.idlefish |
| 淘宝 | taobao | com.taobao.taobao |

## 判定逻辑

### 正版判定
- 店铺名称匹配官方授权列表 → **判定为正版**

### 盗版判定（需同时满足）
- 店铺名称不在官方授权列表
- 价格低于原价的 70%
- 内容与正版商品匹配度高（>60%）
- **综合置信度 ≥ 70% → 判定为盗版**

## 配置说明

### 检测参数 (`config_anti_piracy.py`)

```python
DETECTOR_CONFIG = {
    "price_threshold": 0.7,        # 价格阈值
    "similarity_threshold": 0.6,   # 内容相似度阈值
    "confidence_threshold": 0.7    # 盗版判定置信度阈值
}

AGENT_CONFIG = {
    "max_steps": 50,               # 最大步数
    "item_check_limit": 10,        # 每次检查的最大商品数
    "wait_after_action": 2.0       # 操作后等待时间（秒）
}
```

### 数据结构

**正版商品数据** (`data/genuine_products.json`)：

```json
{
  "product_id": "dedao_001",
  "product_name": "薛兆丰的经济学课",
  "shop_name": "得到官方旗舰店",
  "official_shops": ["得到官方旗舰店", "得到App官方店"],
  "original_price": 199.0,
  "platform": "得到",
  "category": "电子书",
  "keywords": ["薛兆丰", "经济学", "得到"]
}
```

## 常见问题

### 1. 无法连接手机

```bash
adb kill-server
adb start-server
adb devices
```

### 2. ModuleNotFoundError

确保在虚拟环境中运行：

```bash
source venv/bin/activate
```

### 3. API 连接失败

检查 `.env` 配置文件中的 API 地址和密钥是否正确。

### 4. 中文无法输入到举报文本框

系统会按以下顺序尝试输入方法：

1. **ADB Keyboard**（推荐）- 需要在手机上安装并设为默认输入法
2. **Clipper** - 剪贴板应用，通过粘贴方式输入
3. **系统剪贴板** - 直接设置剪贴板并粘贴

**解决方案**：

```bash
# 方案1: 安装 ADB Keyboard（推荐）
# 下载: https://github.com/senzhk/ADBKeyBoard/releases
# 安装后设置为默认输入法:
adb shell ime set com.android.adbkeyboard/.AdbIME

# 方案2: 安装 Clipper 应用
# 从应用商店搜索 "Clipper" 或 "剪贴板管理"
```

### 5. 举报页面元素找不到

使用调试模式分析页面结构：

```bash
# 先手动打开小红书举报页面，然后运行:
python test/test_detection.py --debug-report-page
# 查看 test/debug/ 目录下的 UI XML 文件
```

## 注意事项

1. **合法使用**: 本系统仅用于合法的版权保护目的
2. **谨慎举报**: 确保举报对象确实是盗版，避免误报
3. **测试优先**: 首次使用建议启用测试模式
4. **隐私保护**: 不要泄露个人信息和账号密码

## 技术支持

- Open-AutoGLM: https://github.com/THUDM/Open-AutoGLM
- AutoGLM-Phone-9B: https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B

## 许可协议

本项目仅供学习和研究使用。使用本系统时请遵守相关法律法规和平台规则。
