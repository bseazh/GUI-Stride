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
├── main_anti_piracy.py       # 主启动脚本
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
└── screenshots/              # 证据截图
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

### 完整命令选项

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
