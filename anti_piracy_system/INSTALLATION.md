# 安装和环境配置指南

## 问题说明

由于 macOS 的 Python 环境管理策略,系统 Python 被保护,无法直接安装第三方包。因此我们为本项目创建了一个独立的虚拟环境。

## 已完成的配置

✅ **虚拟环境已创建并配置完成**

我已经为您完成了以下配置:

1. 在项目目录创建了虚拟环境: `venv/`
2. 安装了所有必需的依赖:
   - openai
   - Pillow
   - requests
   - phone-agent (Open-AutoGLM)
3. 更新了启动脚本,自动使用虚拟环境

## 使用方法

### 方式 1: 使用快速启动脚本(推荐)

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
./quick_start.sh
```

快速启动脚本会自动激活虚拟环境。

### 方式 2: 手动激活虚拟环境

```bash
# 进入项目目录
cd /Users/Apple/Documents/GUI/anti_piracy_system

# 激活虚拟环境
source venv/bin/activate

# 现在可以运行任何命令
python main_anti_piracy.py --show-stats
python main_anti_piracy.py --add-product
python main_anti_piracy.py --platform xiaohongshu --test-mode

# 完成后,退出虚拟环境
deactivate
```

### 方式 3: 直接运行(推荐新手)

由于我已经更新了 shebang,您可以直接运行:

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
./main_anti_piracy.py --show-stats
```

## 验证安装

运行以下命令检查环境是否配置正确:

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate
python -c "import phone_agent; print('✅ Open-AutoGLM 安装成功')"
python -c "import openai; print('✅ OpenAI SDK 安装成功')"
python main_anti_piracy.py --show-stats
```

如果看到商品数据库统计信息,说明一切正常!

## 常见命令

### 查看数据库统计
```bash
source venv/bin/activate
python main_anti_piracy.py --show-stats
```

### 添加正版商品
```bash
source venv/bin/activate
python main_anti_piracy.py --add-product
```

### 测试模式巡查
```bash
source venv/bin/activate
python main_anti_piracy.py --platform xiaohongshu --keyword "得到" --test-mode
```

## 项目结构

```
anti_piracy_system/
├── venv/                    # 虚拟环境(已配置)
│   ├── bin/
│   │   ├── activate         # 激活脚本
│   │   └── python3          # Python 解释器
│   └── lib/                 # 已安装的包
├── main_anti_piracy.py      # 主程序
├── quick_start.sh           # 快速启动脚本
└── ...其他文件
```

## 依赖包列表

虚拟环境中已安装以下包:

- **openai** (2.14.0) - OpenAI API 客户端
- **Pillow** (12.0.0) - 图像处理
- **requests** (2.32.5) - HTTP 请求
- **phone-agent** (0.1.0) - Open-AutoGLM 框架
- 以及它们的依赖项

## 重新安装虚拟环境

如果需要重新创建虚拟环境:

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system

# 删除旧环境
rm -rf venv

# 创建新环境
python3 -m venv venv

# 激活环境
source venv/bin/activate

# 安装依赖
pip install openai Pillow requests
cd ../Open-AutoGLM-main
pip install -e .
cd ../anti_piracy_system
```

## 为什么需要虚拟环境?

1. **系统保护**: macOS 的 Python 环境受 PEP 668 保护,禁止直接安装包
2. **依赖隔离**: 避免与其他项目的依赖冲突
3. **版本管理**: 可以为不同项目使用不同版本的包
4. **便于迁移**: 虚拟环境可以轻松复制到其他机器

## 故障排查

### 问题: "ModuleNotFoundError: No module named 'openai'"

**解决方法**: 确保激活了虚拟环境

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate
```

### 问题: "command not found: python"

**解决方法**: 使用 `python3` 而不是 `python`

```bash
python3 main_anti_piracy.py --show-stats
```

### 问题: 虚拟环境损坏

**解决方法**: 重新创建虚拟环境(参考上面的"重新安装虚拟环境"章节)

## 总结

✅ 虚拟环境已配置完成,开箱即用
✅ 使用 `./quick_start.sh` 或手动激活环境
✅ 所有依赖已安装
✅ 可以开始使用反盗版系统了!

如有任何问题,请参考 README.md 或本文档。
