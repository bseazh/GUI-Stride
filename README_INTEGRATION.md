# GUI-Stride 项目整合指南

## 项目结构

```
GUI-Stride/
├── backend/                 # FastAPI 后端服务
│   ├── api/                # API 应用代码
│   ├── requirements.txt    # Python 依赖
│   └── .env.example       # 环境变量示例
├── frontend/               # React 前端（原 market-intelligence-searcher）
│   ├── src/               # 前端源代码
│   ├── services/          # API 服务层
│   ├── package.json       # 前端依赖
│   └── vite.config.ts     # Vite 配置（已配置代理）
├── anti_piracy_system/     # 原有反盗版系统（保持不变）
└── Open-AutoGLM/          # AutoGLM 框架（已包含）
```

## 快速启动

### 1. 后端服务启动

#### 环境准备
```bash
cd backend

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，设置您的 ModelScope API 密钥
# PHONE_AGENT_API_KEY=your_api_key_here

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 启动后端服务
```bash
cd backend
python -m api.main
```
服务将在 http://localhost:8000 启动。

API 文档：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 2. 前端服务启动

#### 环境准备
```bash
cd frontend

# 安装依赖
npm install

# 环境变量已配置在 .env.local
# 如需修改 API 地址，编辑 .env.local 中的 VITE_API_BASE_URL
```

#### 启动前端开发服务器
```bash
cd frontend
npm run dev
```
前端将在 http://localhost:3000 启动，API 请求会自动代理到后端。

### 3. 同时启动前后端（推荐）

使用两个终端窗口：
```bash
# 终端 1: 启动后端
cd backend && python -m api.main

# 终端 2: 启动前端
cd frontend && npm run dev
```

## 功能验证

### 1. 检查服务健康
```bash
# 后端健康检查
curl http://localhost:8000/api/health

# 预期响应: {"status":"healthy","service":"anti-piracy-api"}
```

### 2. 检查平台列表
```bash
curl http://localhost:8000/api/config/platforms

# 预期响应: 支持的平台列表
```

### 3. 打开前端控制面板
浏览器访问：http://localhost:3000

应该看到反盗版自动巡查系统控制面板，包含：
- 平台选择（小红书、闲鱼、淘宝）
- 巡查参数配置
- 设备状态显示
- 任务历史记录

## 使用流程

### 1. 连接设备
- 确保 Android/HarmonyOS 手机已开启 USB 调试
- 通过 USB 连接到电脑
- 前端控制面板应显示"设备已连接"

### 2. 配置巡查任务
1. 选择目标平台（如小红书）
2. 输入搜索关键词（如"众合法考"）
3. 设置最大检查商品数（默认 10）
4. 选择运行模式（测试模式/正式模式）

### 3. 启动巡查
点击"开始自动巡查"按钮，系统将：
- 启动手机上的目标应用
- 搜索指定关键词
- 自动识别商品信息
- 执行三层盗版检测
- 生成巡查报告

### 4. 监控任务进度
- 任务状态实时更新
- 进度条显示执行进度
- 结果面板展示检测统计

## API 接口

### 核心端点
- `POST /api/patrol/start` - 启动巡查任务
- `GET /api/patrol/{task_id}` - 获取任务状态
- `GET /api/patrol/` - 获取任务历史
- `GET /api/config/platforms` - 获取支持平台
- `GET /api/config/device/status` - 获取设备状态

### 数据模型
参见前端 `services/antiPiracyService.ts` 中的类型定义。

## 故障排查

### 常见问题

#### 1. 后端启动失败
- 检查 Python 版本（需要 3.10+）
- 检查依赖安装：`pip list | grep fastapi`
- 检查环境变量：确保 `.env` 文件存在且格式正确

#### 2. 前端无法连接后端
- 检查后端是否运行：`curl http://localhost:8000/api/health`
- 检查代理配置：`frontend/vite.config.ts`
- 检查 CORS 设置：`backend/api/main.py`

#### 3. 设备连接失败
- 检查 USB 连接：`adb devices`
- 检查手机开发者选项和 USB 调试
- 重启 ADB 服务：`adb kill-server && adb start-server`

#### 4. 模型服务错误
- 检查 ModelScope API 密钥
- 检查网络连接
- 查看后端日志获取详细错误信息

### 日志查看

#### 后端日志
后端控制台会显示详细的执行日志，包括：
- 任务启动和状态更新
- 设备连接状态
- 模型调用结果
- 错误信息

#### 前端日志
浏览器开发者工具（F12）查看：
- 网络请求和响应
- 控制台日志
- 错误信息

## 生产部署

### 后端部署
1. 设置生产环境变量：
   ```bash
   ENV=production
   DEBUG=false
   ALLOWED_ORIGINS=https://your-domain.com
   ```

2. 使用生产服务器：
   ```bash
   # 使用 uvicorn 生产配置
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. 或使用 Docker：
   ```dockerfile
   # 创建 Dockerfile（示例）
   FROM python:3.10-slim
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install -r requirements.txt
   COPY backend/ .
   CMD ["python", "-m", "api.main"]
   ```

### 前端部署
1. 构建静态文件：
   ```bash
   cd frontend
   npm run build
   ```

2. 后端服务静态文件：
   - 生产模式下，FastAPI 会自动服务 `frontend/dist` 目录
   - 或使用 Nginx 等 Web 服务器

### 数据库配置
- 默认使用 SQLite 数据库（`patrol.db`）
- 生产环境建议使用 PostgreSQL 或 MySQL
- 修改 `DATABASE_URL` 环境变量

## 扩展开发

### 添加新平台
1. 在 `backend/api/routers/config.py` 中添加平台定义
2. 在 `anti_piracy_system/config_anti_piracy.py` 中配置平台参数
3. 实现平台特定的举报器（如需要）

### 添加新功能
1. 在后端添加新的 API 端点
2. 在前端添加对应的 UI 组件
3. 更新 API 服务层

### 修改界面
- 前端使用 React + TypeScript + Tailwind CSS
- 主要界面文件：`frontend/App.tsx`
- 样式使用 Tailwind 工具类

## 注意事项

1. **合法合规使用**：仅用于保护自有版权内容
2. **测试模式**：首次使用建议启用测试模式
3. **设备要求**：需要 Android 7.0+ 或 HarmonyOS NEXT+
4. **网络要求**：需要访问 ModelScope API
5. **数据安全**：妥善保管 API 密钥和配置文件

## 技术支持

- 查看详细文档：`anti_piracy_system/` 目录下的文档
- 问题反馈：检查日志文件
- 代码参考：现有反盗版系统实现

---

**整合完成时间**: 2025-12-27
**版本**: v1.0.0
**状态**: 基础功能完整，可进行测试和部署