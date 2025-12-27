"""
FastAPI主应用 - 反盗版系统Web API
"""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 创建FastAPI应用
app = FastAPI(
    title="反盗版自动巡查系统API",
    description="提供反盗版巡查任务的Web API和控制面板",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 配置CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
try:
    from .routers import patrol, database, reports, config
    app.include_router(patrol.router, prefix="/api/patrol", tags=["巡查任务"])
    app.include_router(database.router, prefix="/api/database", tags=["数据库管理"])
    app.include_router(reports.router, prefix="/api/reports", tags=["举报管理"])
    app.include_router(config.router, prefix="/api/config", tags=["系统配置"])
except ImportError as e:
    print(f"警告: 路由导入失败 - {e}")

# 健康检查端点
@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "anti-piracy-api"}

# 静态文件服务（用于生产环境）
if os.getenv("ENV") == "production":
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
        print(f"已挂载静态文件目录: {frontend_dist}")
    else:
        print(f"警告: 静态文件目录不存在: {frontend_dist}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)