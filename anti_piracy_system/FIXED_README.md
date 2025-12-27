# 反盗版系统 - 修复完成

✅ **所有问题已修复，系统可以正常运行！**

## 修复内容

1. ✅ 修复了 Open-AutoGLM 路径引用（从 `Open-AutoGLM-main` 改为 `Open-AutoGLM`）
2. ✅ 确认所有依赖已安装在 venv 中
3. ✅ 配置 ModelScope API（已在 .env 文件中）
4. ✅ 修复 shebang 行，使用标准 Python3
5. ✅ 设置脚本可执行权限

## 使用方法

### 方式 1：使用交互式启动脚本（推荐）

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
./start_with_modelscope.sh
```

启动后会看到菜单：
```
1. 查看数据库统计
2. 添加正版商品
3. 运行诊断测试
4. 开始巡查(测试模式 - 推荐)
5. 开始巡查(正式模式)
6. 运行检测逻辑演示(无需手机)
0. 退出
```

### 方式 2：直接运行命令

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate

# 查看数据库统计
python main_anti_piracy.py --show-stats

# 添加正版商品
python main_anti_piracy.py --add-product

# 运行检测逻辑演示（无需连接手机）
python demo_detection.py

# 测试模式巡查（不实际举报）
python main_anti_piracy.py \
    --base-url https://api-inference.modelscope.cn/v1 \
    --model "ZhipuAI/AutoGLM-Phone-9B" \
    --apikey "ms-464d1e28-e9ee-432a-b20e-afeee7a9d0fa" \
    --platform xiaohongshu \
    --keyword "得到" \
    --max-items 10 \
    --test-mode

# 正式模式巡查（实际执行举报）
python main_anti_piracy.py \
    --base-url https://api-inference.modelscope.cn/v1 \
    --model "ZhipuAI/AutoGLM-Phone-9B" \
    --apikey "ms-464d1e28-e9ee-432a-b20e-afeee7a9d0fa" \
    --platform xiaohongshu \
    --keyword "得到" \
    --max-items 10
```

## 支持的平台

- `xiaohongshu` - 小红书
- `xianyu` - 闲鱼
- `taobao` - 淘宝

## 重要提醒

### 使用前准备

1. **确保 Android 手机已连接**
   ```bash
   adb devices
   # 应该显示您的设备
   ```

2. **确保 ADB Keyboard 已安装并启用**（用于中文输入）
   - 下载：https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk
   - 在手机设置中启用该输入法

3. **首次使用建议先运行测试模式**
   ```bash
   ./start_with_modelscope.sh
   # 然后选择选项 4（测试模式）
   ```

### 运行演示（无需手机）

如果您想先了解检测逻辑，可以运行演示程序：

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate
python demo_detection.py
```

这会演示如何：
- 定义正版商品
- 检测盗版商品
- 生成举报理由

### 项目结构

```
anti_piracy_system/
├── main_anti_piracy.py          # 主程序
├── anti_piracy_agent.py         # Agent 实现
├── product_database.py          # 正版商品数据库
├── piracy_detector.py          # 盗版检测器
├── report_manager.py           # 举报记录管理
├── config_anti_piracy.py       # 配置文件
├── demo_detection.py           # 检测逻辑演示
├── diagnose_model_service.py   # 模型服务诊断工具
├── start_with_modelscope.sh    # 启动脚本
├── .env                        # 环境变量配置
├── data/                       # 数据目录
│   └── genuine_products.json   # 正版商品数据
├── logs/                       # 日志目录
│   └── report_history.json     # 举报历史
└── screenshots/                # 截图证据
```

## 配置说明

### 模型服务配置（.env 文件）

当前使用 ModelScope 免费推理服务：

```bash
PHONE_AGENT_BASE_URL=https://api-inference.modelscope.cn/v1
PHONE_AGENT_MODEL=ZhipuAI/AutoGLM-Phone-9B
PHONE_AGENT_API_KEY=ms-464d1e28-e9ee-432a-b20e-afeee7a9d0fa
```

### 切换到其他服务

如果需要切换到智谱 BigModel：

```bash
PHONE_AGENT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
PHONE_AGENT_MODEL=autoglm-phone
PHONE_AGENT_API_KEY=your-bigmodel-api-key
```

## 工作流程

1. **添加正版商品到数据库**
   ```bash
   python main_anti_piracy.py --add-product
   ```

2. **测试模式运行**（推荐首次使用）
   ```bash
   python main_anti_piracy.py --platform xiaohongshu --keyword "得到" --test-mode
   ```

3. **正式模式运行**（实际举报）
   ```bash
   python main_anti_piracy.py --platform xiaohongshu --keyword "得到"
   ```

4. **查看统计信息**
   ```bash
   python main_anti_piracy.py --show-stats
   ```

5. **导出举报记录**
   ```bash
   python main_anti_piracy.py --export-report report.txt
   ```

## 故障排查

### 如果遇到 "ModuleNotFoundError"

确保在虚拟环境中运行：
```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate
```

### 如果遇到 "502 Bad Gateway"

运行诊断工具：
```bash
python diagnose_model_service.py
```

### 如果 ADB 连接失败

```bash
# 重启 ADB 服务
adb kill-server
adb start-server
adb devices
```

### 如果无法输入中文

确保 ADB Keyboard 已安装并在手机设置中启用。

## 下一步

1. **首次运行建议**：先运行 `python demo_detection.py` 了解检测逻辑
2. **添加正版商品**：运行 `python main_anti_piracy.py --add-product`
3. **测试模式巡查**：运行 `./start_with_modelscope.sh` 选择选项 4
4. **查看结果**：运行 `python main_anti_piracy.py --show-stats`

## 技术支持

如有问题，请查看：
- `README.md` - 完整文档
- `TROUBLESHOOTING_502.md` - 模型服务问题排查
- `QUICK_START.md` - 快速开始指南
