# 模型服务配置指南

## 问题诊断

如果您遇到 `502 Bad Gateway` 错误,说明模型服务未正确配置或未运行。

### 快速诊断

运行诊断工具检查问题:

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate
python diagnose_model_service.py
```

诊断工具会自动检测:
- 依赖模块是否安装
- 服务器是否可达
- API端点是否正常工作
- 并提供针对性的解决方案

---

## 解决方案

根据您的需求和资源,可以选择以下任一方案:

### 方案 1: 使用智谱 AI API (推荐 - 最快捷)

**优点**: 无需本地部署,开箱即用,适合快速测试

**步骤**:

1. **注册账号获取 API Key**
   - 访问: https://open.bigmodel.cn/
   - 注册并创建 API Key

2. **配置环境变量**
   ```bash
   export PHONE_AGENT_BASE_URL='https://open.bigmodel.cn/api/paas/v4'
   export PHONE_AGENT_API_KEY='your-api-key-here'
   export PHONE_AGENT_MODEL='glm-4-plus'
   ```

3. **验证配置**
   ```bash
   python diagnose_model_service.py
   ```

4. **运行系统**
   ```bash
   python main_anti_piracy.py --show-stats
   python main_anti_piracy.py --platform xiaohongshu --test-mode
   ```

**费用**: 按调用次数计费,新用户通常有免费额度

---

### 方案 2: 使用 ModelScope API

**优点**: 国内访问稳定,支持多种模型

**步骤**:

1. **获取 API Key**
   - 访问: https://www.modelscope.cn/
   - 注册并获取 API Token

2. **配置环境变量**
   ```bash
   export PHONE_AGENT_BASE_URL='https://api-inference.modelscope.cn/v1'
   export PHONE_AGENT_API_KEY='your-api-token-here'
   export PHONE_AGENT_MODEL='qwen-turbo'
   ```

3. **验证和运行**
   ```bash
   python diagnose_model_service.py
   python main_anti_piracy.py --platform xiaohongshu --test-mode
   ```

---

### 方案 3: 本地部署 AutoGLM-Phone-9B (完整功能)

**优点**:
- 完全私有化部署
- 专为手机自动化优化
- 无需外网访问
- 长期使用成本低

**硬件要求**:
- GPU: 至少 24GB 显存 (推荐 NVIDIA A100/A6000/4090)
- 内存: 32GB+
- 存储: 50GB+

**步骤**:

#### 3.1 安装 vLLM

```bash
# 创建新的虚拟环境用于模型服务
python3 -m venv venv_model
source venv_model/bin/activate

# 安装 vLLM
pip install vllm

# 或使用 conda
conda create -n vllm python=3.10
conda activate vllm
pip install vllm
```

#### 3.2 下载模型

**方式 A: 从 ModelScope 下载**

```bash
pip install modelscope

python -c "
from modelscope import snapshot_download
model_dir = snapshot_download('ZhipuAI/AutoGLM-Phone-9B', cache_dir='./models')
print(f'模型已下载到: {model_dir}')
"
```

**方式 B: 从 HuggingFace 下载**

```bash
pip install huggingface-hub

python -c "
from huggingface_hub import snapshot_download
model_dir = snapshot_download('THUDM/AutoGLM-Phone-9B', cache_dir='./models')
print(f'模型已下载到: {model_dir}')
"
```

#### 3.3 启动模型服务

```bash
# 激活模型服务环境
source venv_model/bin/activate

# 启动 vLLM 服务
vllm serve THUDM/AutoGLM-Phone-9B \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096

# 或者如果已经下载到本地:
vllm serve ./models/THUDM/AutoGLM-Phone-9B \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code \
  --gpu-memory-utilization 0.9
```

**参数说明**:
- `--host 0.0.0.0`: 允许外部访问
- `--port 8000`: 服务端口
- `--trust-remote-code`: 信任模型代码
- `--gpu-memory-utilization 0.9`: GPU 显存使用率
- `--max-model-len 4096`: 最大序列长度

#### 3.4 验证服务

在**另一个终端**中:

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate

# 运行诊断工具
python diagnose_model_service.py
```

如果看到 "✅ API正常工作!",说明服务已成功启动。

#### 3.5 运行反盗版系统

```bash
# 确保使用反盗版系统的虚拟环境
source venv/bin/activate

# 配置使用本地服务
export PHONE_AGENT_BASE_URL='http://localhost:8000/v1'
export PHONE_AGENT_MODEL='autoglm-phone-9b'
export PHONE_AGENT_API_KEY='EMPTY'

# 运行系统
python main_anti_piracy.py --platform xiaohongshu --test-mode
```

---

### 方案 4: 使用 SGLang (vLLM 替代方案)

SGLang 是另一个高性能推理框架,支持 AutoGLM-Phone-9B。

```bash
# 安装 SGLang
pip install "sglang[all]"

# 启动服务
python -m sglang.launch_server \
  --model-path THUDM/AutoGLM-Phone-9B \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code
```

---

## 测试模式 vs 正式模式

### 测试模式 (推荐新手)

测试模式不会实际执行举报操作,适合:
- 验证检测逻辑
- 调试系统
- 测试配置

```bash
python main_anti_piracy.py --platform xiaohongshu --test-mode
```

### 演示模式 (无需模型服务)

如果只想测试检测算法,可以运行演示脚本:

```bash
python demo_detection.py
```

这会使用预设数据演示三层检测机制,无需连接模型服务或手机。

### 正式模式

正式模式会执行实际举报操作:

```bash
python main_anti_piracy.py --platform xiaohongshu --keyword "得到"
```

**警告**: 正式模式会通过手机应用实际提交举报,请谨慎使用。

---

## 配置持久化

为避免每次都设置环境变量,可以将配置写入 `.env` 文件:

```bash
# 创建 .env 文件
cat > .env << 'EOF'
# 智谱 AI 配置
PHONE_AGENT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
PHONE_AGENT_API_KEY=your-api-key-here
PHONE_AGENT_MODEL=glm-4-plus

# 或本地服务配置
# PHONE_AGENT_BASE_URL=http://localhost:8000/v1
# PHONE_AGENT_MODEL=autoglm-phone-9b
# PHONE_AGENT_API_KEY=EMPTY
EOF

# 加载配置
source .env
```

或者修改 `main_anti_piracy.py` 直接使用参数:

```bash
python main_anti_piracy.py \
  --base-url "https://open.bigmodel.cn/api/paas/v4" \
  --apikey "your-api-key" \
  --model "glm-4-plus" \
  --platform xiaohongshu \
  --test-mode
```

---

## 常见问题

### Q1: 502 Bad Gateway 错误

**原因**: 模型服务未启动或配置错误

**解决**:
1. 运行 `python diagnose_model_service.py` 诊断
2. 检查模型服务是否正在运行
3. 验证 BASE_URL 配置是否正确

### Q2: Connection Refused 错误

**原因**: 无法连接到指定的服务器

**解决**:
1. 确认服务器地址正确
2. 检查防火墙设置
3. 确认服务已启动并监听正确端口

### Q3: 401 Unauthorized 错误

**原因**: API Key 无效或未配置

**解决**:
1. 检查 API Key 是否正确
2. 确认 API Key 有效期
3. 验证 API Key 权限

### Q4: 模型加载失败

**原因**: 显存不足或模型文件损坏

**解决**:
1. 检查 GPU 显存是否充足
2. 降低 `--gpu-memory-utilization` 参数
3. 重新下载模型文件

### Q5: 想先测试检测逻辑,不想配置模型

**解决**: 运行演示脚本

```bash
python demo_detection.py
```

这会展示完整的检测逻辑,无需模型服务。

---

## 性能优化

### 本地部署优化建议

1. **使用量化模型** (减少显存占用)
   ```bash
   vllm serve THUDM/AutoGLM-Phone-9B \
     --quantization awq \
     --gpu-memory-utilization 0.85
   ```

2. **调整并发数**
   ```bash
   vllm serve THUDM/AutoGLM-Phone-9B \
     --max-num-seqs 8 \
     --max-num-batched-tokens 4096
   ```

3. **使用张量并行** (多GPU)
   ```bash
   vllm serve THUDM/AutoGLM-Phone-9B \
     --tensor-parallel-size 2
   ```

---

## 推荐配置

### 快速开始 (测试)
- **方案**: 智谱 AI API
- **成本**: 低 (有免费额度)
- **配置时间**: 5分钟
- **适用场景**: 功能验证、小规模测试

### 生产环境 (长期使用)
- **方案**: 本地部署 AutoGLM-Phone-9B
- **成本**: 硬件投入 (一次性)
- **配置时间**: 1-2小时
- **适用场景**: 大规模巡查、隐私要求高

### 仅测试检测算法
- **方案**: 运行 demo_detection.py
- **成本**: 无
- **配置时间**: 0
- **适用场景**: 验证检测逻辑、算法调试

---

## 获取帮助

1. **运行诊断工具**: `python diagnose_model_service.py`
2. **查看详细日志**: 添加 `--verbose` 参数
3. **查看项目文档**:
   - README.md - 项目概览
   - INSTALLATION.md - 环境配置
   - 本文档 - 模型服务配置

---

## 总结

✅ **推荐路线**:

1. **第一步**: 运行 `python demo_detection.py` 验证检测逻辑
2. **第二步**: 使用智谱 AI API 快速测试完整流程
3. **第三步**: 根据需要决定是否本地部署模型

这样可以循序渐进地验证系统功能,避免一开始就陷入复杂的本地部署配置中。
