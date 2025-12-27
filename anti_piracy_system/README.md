# 反盗版自动巡查与举报系统

基于 Open-AutoGLM 框架构建的智能反盗版系统,专门用于识别和举报小红书、闲鱼等平台上的盗版电子内容。

## 功能特性

- 🔍 **智能检测**: 基于多模态 AI 模型自动识别疑似盗版商品
- 🎯 **三层判断机制**:
  - 店铺名称匹配(官方授权验证)
  - 价格比对(低于原价70%触发警告)
  - 内容识别(基于OCR和图像分析)
- 📢 **自动举报**: 自动触发平台内举报功能
- 📊 **数据管理**: 完整的正版商品数据库和举报记录系统
- 📸 **证据保存**: 自动保存举报证据截图
- 📈 **统计报告**: 生成详细的巡查报告和统计信息

## 系统架构

```
anti_piracy_system/
├── product_database.py      # 正版商品数据库管理
├── piracy_detector.py        # 盗版识别逻辑引擎
├── report_manager.py         # 举报流程管理
├── config_anti_piracy.py     # 系统配置
├── anti_piracy_agent.py      # 主 Agent 类
├── main_anti_piracy.py       # 启动脚本
├── data/                     # 数据文件
│   └── genuine_products.json # 正版商品数据库
├── logs/                     # 日志文件
│   └── report_history.json   # 举报记录
├── screenshots/              # 证据截图
└── README.md                 # 本文档
```

## 环境要求

### 硬件要求
- Android 手机(Android 7.0+)或鸿蒙设备
- 支持数据传输的 USB 数据线
- 电脑(macOS/Linux/Windows)

### 软件要求
- Python 3.10+
- ADB 工具(Android)/HDC 工具(鸿蒙)
- Open-AutoGLM 框架
- AutoGLM-Phone-9B 模型服务

## 快速开始

✅ **ModelScope API 已配置完成!** 直接使用:

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
./start_with_modelscope.sh
```

详细使用说明请查看: 📘 [QUICK_START.md](QUICK_START.md)

---

⚠️ **遇到问题?** 请查看:
- 📘 [QUICK_START.md](QUICK_START.md) - 快速开始指南 ⭐推荐
- 📘 [INSTALLATION.md](INSTALLATION.md) - 虚拟环境配置指南
- 📘 [MODEL_SERVICE_SETUP.md](MODEL_SERVICE_SETUP.md) - 模型服务配置详解
- 🔧 运行诊断工具: `python diagnose_model_service.py`

### 最快测试方法 (无需模型服务)

如果您想立即看到检测逻辑的效果:

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate
python demo_detection.py
```

这将运行 5 个测试案例,展示三层检测机制如何工作,无需任何外部服务。

## 完整安装步骤

### 1. 安装 Open-AutoGLM

```bash
# 克隆 Open-AutoGLM 项目(如果还未安装)
cd /Users/Apple/Documents/GUI
git clone https://github.com/zai-org/Open-AutoGLM.git Open-AutoGLM-main
cd Open-AutoGLM-main

# 安装依赖
pip install -r requirements.txt
pip install -e .
```

### 2. 配置手机

1. **开启开发者模式**
   - 设置 → 关于手机 → 连续点击版本号 7 次

2. **开启 USB 调试**
   - 设置 → 开发者选项 → USB 调试

3. **安装 ADB Keyboard**(仅 Android)
   - 下载: https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk
   - 在设置中启用 ADB Keyboard

4. **连接手机**
   ```bash
   # 验证连接
   adb devices
   ```

### 3. 配置模型服务

⚠️ **遇到 502 错误?** 查看 [MODEL_SERVICE_SETUP.md](MODEL_SERVICE_SETUP.md) 获取完整配置指南

#### 快速诊断

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate
python diagnose_model_service.py
```

诊断工具会自动检测问题并提供解决方案。

#### 选项 A: 使用第三方服务(推荐 - 最快)

```bash
# 使用智谱 AI API (需要注册获取 API Key)
export PHONE_AGENT_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
export PHONE_AGENT_MODEL="glm-4-plus"
export PHONE_AGENT_API_KEY="your-api-key-here"

# 验证配置
python diagnose_model_service.py
```

注册地址: https://open.bigmodel.cn/

#### 选项 B: 本地部署 AutoGLM-Phone-9B

```bash
# 安装 vLLM
pip install vllm

# 启动模型服务
vllm serve THUDM/AutoGLM-Phone-9B \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code
```

详细配置步骤请查看 [MODEL_SERVICE_SETUP.md](MODEL_SERVICE_SETUP.md)

## 使用方法

### 快速开始

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system

# 基本使用 - 在小红书搜索"得到"
python main_anti_piracy.py --platform xiaohongshu --keyword "得到"

# 测试模式(不实际举报)
python main_anti_piracy.py --platform xiaohongshu --test-mode
```

### 添加正版商品

```bash
# 交互式添加
python main_anti_piracy.py --add-product

# 或者直接编辑 data/genuine_products.json
```

### 查看统计信息

```bash
# 显示数据库和举报统计
python main_anti_piracy.py --show-stats

# 导出举报记录
python main_anti_piracy.py --export-report report.txt
```

### 完整命令选项

```bash
python main_anti_piracy.py \
  --platform xiaohongshu \           # 目标平台(xiaohongshu/xianyu/taobao)
  --keyword "得到" \                 # 搜索关键词
  --max-items 10 \                   # 最多检查商品数
  --base-url http://localhost:8000/v1 \  # 模型服务地址
  --model autoglm-phone-9b \         # 模型名称
  --test-mode \                      # 测试模式(可选)
  --device-id emulator-5554          # 指定设备(可选)
```

## 工作流程

1. **启动应用**: 自动启动目标平台 App(小红书/闲鱼)
2. **搜索商品**: 输入关键词搜索
3. **浏览结果**: 遍历搜索结果列表
4. **提取信息**: 进入商品详情页,提取标题、店铺、价格等信息
5. **盗版检测**:
   - 检查店铺名称是否为官方授权
   - 比对价格是否低于原价70%
   - 分析内容是否与正版商品匹配
6. **执行举报**: 对确认的盗版商品自动触发举报
7. **保存证据**: 截图保存举报证据
8. **生成报告**: 输出详细的巡查报告

## 判定逻辑

### 正版判定
- ✅ 店铺名称匹配官方授权列表 → **判定为正版**

### 盗版判定(需同时满足)
- ❌ 店铺名称不在官方授权列表
- ❌ 价格低于原价的 70%
- ✅ 内容与正版商品匹配度高(>60%)
- → **综合判定为盗版**(置信度 ≥ 70%)

## 配置说明

### 系统配置 (`config_anti_piracy.py`)

```python
# 检测器配置
DETECTOR_CONFIG = {
    "price_threshold": 0.7,        # 价格阈值
    "similarity_threshold": 0.6,   # 内容相似度阈值
    "confidence_threshold": 0.7    # 盗版判定置信度阈值
}

# Agent 配置
AGENT_CONFIG = {
    "max_steps": 50,               # 最大步数
    "scroll_count": 5,             # 滚动次数
    "item_check_limit": 10,        # 每次检查的最大商品数
    "wait_after_action": 2.0       # 操作后等待时间(秒)
}
```

### 支持的平台

| 平台       | 平台键名      | App 包名                  |
|----------|-----------|--------------------------|
| 小红书      | xiaohongshu | com.xingin.xhs          |
| 闲鱼       | xianyu    | com.taobao.idlefish     |
| 淘宝       | taobao    | com.taobao.taobao       |

## 数据结构

### 正版商品数据

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

### 举报记录

```json
{
  "report_id": "report_20250101_120000_0",
  "platform": "小红书",
  "target_title": "薛兆丰经济学课程 超低价",
  "target_shop": "某个人卖家",
  "target_price": 9.9,
  "report_status": "submitted",
  "report_reason": "综合判断该商品疑似盗版..."
}
```

## 常见问题

### 1. 无法连接手机
```bash
# 重启 ADB 服务
adb kill-server
adb start-server
adb devices
```

### 2. 模型服务连接失败 (502 Bad Gateway)

**立即运行诊断工具**:
```bash
python diagnose_model_service.py
```

诊断工具会自动:
- 检查服务器是否可达
- 测试 API 端点
- 提供针对性解决方案

详细解决方案请查看 [MODEL_SERVICE_SETUP.md](MODEL_SERVICE_SETUP.md)

### 3. 举报功能无法使用
- 确保 App 已登录
- 检查 App 版本是否支持
- 尝试手动操作验证 UI 元素

### 4. 检测准确度低
- 增加正版商品数据库内容
- 调整检测阈值参数
- 优化关键词匹配

## 注意事项

⚠️ **重要提醒**:

1. **合法使用**: 本系统仅用于合法的版权保护目的,请勿滥用
2. **谨慎举报**: 确保举报对象确实是盗版,避免误报
3. **隐私保护**: 不要泄露个人信息和账号密码
4. **测试优先**: 首次使用建议启用测试模式
5. **人工审核**: 对于不确定的情况,建议人工复核

## 技术支持

- 问题反馈: 请提交 Issue
- 文档: 参考 Open-AutoGLM 官方文档
- 模型: AutoGLM-Phone-9B

## 许可协议

本项目仅供学习和研究使用。使用本系统时请遵守相关法律法规和平台规则。

## 更新日志

### v1.0.0 (2025-01-01)
- ✅ 初始版本发布
- ✅ 支持小红书、闲鱼平台
- ✅ 实现三层判断机制
- ✅ 完整的举报流程
- ✅ 数据库和日志管理

## 致谢

- 基于 [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) 框架
- 使用 [AutoGLM-Phone-9B](https://huggingface.co/zai-org/AutoGLM-Phone-9B) 模型
