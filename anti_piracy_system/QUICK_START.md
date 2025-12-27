# 快速开始指南

✅ **ModelScope API 已配置完成!** 您现在可以直接使用系统了。

## 最简单的使用方式

### 方式 1: 使用启动脚本 (推荐)

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
./start_with_modelscope.sh
```

脚本会自动:
- ✅ 激活虚拟环境
- ✅ 加载 ModelScope API 配置
- ✅ 显示交互式菜单

### 方式 2: 直接运行命令

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system

# 激活环境并加载配置
source venv/bin/activate
export PHONE_AGENT_BASE_URL='https://api-inference.modelscope.cn/v1'
export PHONE_AGENT_MODEL='ZhipuAI/AutoGLM-Phone-9B'
export PHONE_AGENT_API_KEY='ms-464d1e28-e9ee-432a-b20e-afeee7a9d0fa'

# 查看统计
python main_anti_piracy.py --show-stats

# 测试模式巡查
python main_anti_piracy.py --platform xiaohongshu --test-mode
```

## 推荐操作流程

### 第 1 步: 验证 API 配置

```bash
./start_with_modelscope.sh
# 选择: 3. 运行诊断测试
```

应该看到:
```
✅ 所有检查通过! 模型服务正常工作
```

### 第 2 步: 查看数据库

```bash
./start_with_modelscope.sh
# 选择: 1. 查看数据库统计
```

查看当前有哪些正版商品数据。

### 第 3 步: (可选) 添加更多正版商品

```bash
./start_with_modelscope.sh
# 选择: 2. 添加正版商品
```

按提示输入商品信息。

### 第 4 步: 运行检测演示

```bash
./start_with_modelscope.sh
# 选择: 6. 运行检测逻辑演示(无需手机)
```

这会展示检测算法如何工作,无需连接手机。

### 第 5 步: 连接手机并测试

**前提条件**:
- Android 手机已开启 USB 调试
- 已安装 ADB 工具
- 手机通过 USB 连接到电脑
- 已安装目标 App (小红书/闲鱼)

**验证连接**:
```bash
adb devices
# 应该看到你的设备
```

**运行测试模式**:
```bash
./start_with_modelscope.sh
# 选择: 4. 开始巡查(测试模式 - 推荐)
# 输入平台: xiaohongshu
# 输入关键词: 得到
# 输入商品数: 3
```

测试模式不会实际举报,只会模拟流程。

### 第 6 步: 正式运行

确认一切正常后:

```bash
./start_with_modelscope.sh
# 选择: 5. 开始巡查(正式模式)
```

⚠️ **注意**: 正式模式会实际执行举报操作!

---

## 常用命令速查

### 查看统计信息
```bash
source venv/bin/activate
export PHONE_AGENT_BASE_URL='https://api-inference.modelscope.cn/v1'
export PHONE_AGENT_MODEL='ZhipuAI/AutoGLM-Phone-9B'
export PHONE_AGENT_API_KEY='ms-464d1e28-e9ee-432a-b20e-afeee7a9d0fa'
python main_anti_piracy.py --show-stats
```

### 添加正版商品
```bash
python main_anti_piracy.py --add-product
```

### 测试模式巡查
```bash
python main_anti_piracy.py \
    --platform xiaohongshu \
    --keyword "得到" \
    --max-items 5 \
    --test-mode
```

### 运行检测演示 (无需手机)
```bash
python demo_detection.py
```

### 诊断 API 连接
```bash
python diagnose_model_service.py
```

---

## 配置文件说明

### .env 文件

已创建 `.env` 文件,包含 ModelScope API 配置:

```bash
PHONE_AGENT_BASE_URL=https://api-inference.modelscope.cn/v1
PHONE_AGENT_MODEL=ZhipuAI/AutoGLM-Phone-9B
PHONE_AGENT_API_KEY=ms-464d1e28-e9ee-432a-b20e-afeee7a9d0fa
```

如需修改配置,直接编辑此文件即可。

---

## 目录结构

```
anti_piracy_system/
├── .env                          # API 配置文件 ✅
├── start_with_modelscope.sh      # 启动脚本 ✅
├── diagnose_model_service.py     # 诊断工具 ✅
├── demo_detection.py             # 检测演示 ✅
├── main_anti_piracy.py           # 主程序
├── product_database.py           # 商品数据库
├── piracy_detector.py            # 检测引擎
├── report_manager.py             # 举报管理
├── data/
│   └── genuine_products.json     # 正版商品数据
├── logs/
│   └── report_history.json       # 举报记录
└── venv/                         # 虚拟环境
```

---

## 文档索引

- 📘 **README.md** - 项目完整文档
- 📘 **INSTALLATION.md** - 环境安装指南
- 📘 **MODEL_SERVICE_SETUP.md** - 模型服务配置详解
- 📘 **TROUBLESHOOTING_502.md** - 502 错误排查
- 📘 **本文档 (QUICK_START.md)** - 快速开始

---

## 常见问题

### Q: 如何确认 API 是否正常?

运行诊断工具:
```bash
source venv/bin/activate
export PHONE_AGENT_BASE_URL='https://api-inference.modelscope.cn/v1'
export PHONE_AGENT_MODEL='ZhipuAI/AutoGLM-Phone-9B'
export PHONE_AGENT_API_KEY='ms-464d1e28-e9ee-432a-b20e-afeee7a9d0fa'
python diagnose_model_service.py
```

看到 "✅ 所有检查通过!" 说明正常。

### Q: 不想配置环境变量怎么办?

使用启动脚本:
```bash
./start_with_modelscope.sh
```

脚本会自动从 `.env` 加载配置。

### Q: 想先测试检测逻辑,不想连接手机?

运行演示:
```bash
python demo_detection.py
```

### Q: 如何添加更多正版商品?

方式 1: 交互式添加
```bash
python main_anti_piracy.py --add-product
```

方式 2: 直接编辑
```bash
vim data/genuine_products.json
```

### Q: 测试模式和正式模式有什么区别?

- **测试模式** (`--test-mode`): 模拟流程,不实际举报
- **正式模式**: 实际执行举报操作

建议先用测试模式验证流程。

---

## 下一步

1. ✅ **立即试用**: 运行 `./start_with_modelscope.sh`
2. ✅ **验证 API**: 选择 "3. 运行诊断测试"
3. ✅ **查看演示**: 选择 "6. 运行检测逻辑演示"
4. ✅ **连接手机**: 配置 ADB 和 USB 调试
5. ✅ **测试运行**: 选择 "4. 开始巡查(测试模式)"

系统已经完全配置好,可以直接使用了! 🚀

---

## 技术支持

遇到问题时:
1. 先运行 `python diagnose_model_service.py`
2. 查看对应的文档 (README.md, TROUBLESHOOTING_502.md)
3. 检查 `.env` 配置是否正确
