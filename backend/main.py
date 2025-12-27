#!/usr/bin/env python3
"""
Backend API server for GUI-Stride anti-piracy system.
Provides REST API for frontend to interact with anti-piracy agents.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# 导入任务管理器
from task_manager import task_manager

# Add project root to path to import anti_piracy_system modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import anti-piracy system modules
try:
    from anti_piracy_system.product_database import ProductDatabase
    from anti_piracy_system.report_manager import ReportManager
    from anti_piracy_system.anti_piracy_agent import AntiPiracyAgent
    from anti_piracy_system.config_anti_piracy import SUPPORTED_PLATFORMS
    ANTI_PIRACY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Anti-piracy modules not available: {e}")
    print("Running in mock mode for development.")
    ANTI_PIRACY_AVAILABLE = False

# Pydantic models for API requests/responses
class PatrolRequest(BaseModel):
    platform: str = Field(..., description="Platform: xianyu, xhs, etc.")
    keyword: str = Field(..., description="Search keyword")
    max_items: int = Field(10, description="Maximum items to check")
    test_mode: bool = Field(True, description="Test mode (no actual reporting)")

class PatrolResponse(BaseModel):
    task_id: str
    status: str
    message: str

class Merchant(BaseModel):
    id: str
    name: str
    platform: str
    status: str  # 'official' or 'pirated'
    imageUrl: str
    uid: str
    reasoning: Optional[str] = None
    evidenceImages: Optional[List[str]] = None
    reportNumber: Optional[str] = None
    reportDate: Optional[str] = None

class LogEntry(BaseModel):
    id: str
    timestamp: str
    type: str  # 'info', 'performance', 'action'
    message: str
    metadata: Optional[Dict[str, Any]] = None

class ReportRecord(BaseModel):
    id: str
    reportNumber: str
    merchantName: str
    productName: str
    price: float
    lossPrevented: float
    reason: str
    date: str
    screenshots: List[str]

# Initialize FastAPI app
app = FastAPI(
    title="GUI-Stride API",
    description="Backend API for anti-piracy web interface",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for tasks (in production, use a proper task queue)
# patrol_tasks: Dict[str, Dict[str, Any]] = {}  # 使用 task_manager 替代

# Mock data for development
MOCK_MERCHANTS = [
    {
        "id": "1",
        "name": "24届法考资料专营",
        "platform": "闲鱼",
        "status": "pirated",
        "imageUrl": "https://picsum.photos/seed/m1/200/200",
        "uid": "9827214",
        "reasoning": "该商家售价显著低于正版定价（¥299 vs ¥50），且商品描述中包含“百度网盘秒发”、“电子版”等非法分发关键词。店铺资质为个人，无出版社授权证明。",
        "evidenceImages": ["https://picsum.photos/seed/ev1/400/800", "https://picsum.photos/seed/ev2/400/800"],
        "reportNumber": "RP-20240522-001",
        "reportDate": "2024-05-22 14:05"
    },
    {
        "id": "2",
        "name": "官方图书旗舰店",
        "platform": "闲鱼",
        "status": "official",
        "imageUrl": "https://picsum.photos/seed/m2/200/200",
        "uid": "9827215"
    }
]

MOCK_LOGS = [
    {
        "id": "l1",
        "timestamp": "14:20:01",
        "type": "info",
        "message": "系统初始化完成，等待指令..."
    }
]

MOCK_REPORTS = [
    {
        "id": "r1",
        "reportNumber": "RP-20240522-001",
        "merchantName": "阿强书屋",
        "productName": "2024法考全套电子资料",
        "price": 50.0,
        "lossPrevented": 1200.0,
        "reason": "非法网盘分发，包含加密水印关键词，确认为盗版。",
        "date": "2024-05-22",
        "screenshots": ["https://picsum.photos/seed/scr1/200/200"]
    }
]

@app.get("/")
async def root():
    return {"message": "GUI-Stride API Server", "status": "online"}

@app.get("/api/merchants", response_model=List[Merchant])
async def get_merchants(limit: int = 20, platform: Optional[str] = None):
    """Get list of merchants (pirated/official)"""
    # TODO: Replace with real data from report manager
    merchants = MOCK_MERCHANTS
    if platform:
        merchants = [m for m in merchants if m["platform"] == platform]
    return merchants[:limit]

@app.get("/api/logs", response_model=List[LogEntry])
async def get_logs(limit: int = 50):
    """Get system logs"""
    # TODO: Replace with real logs
    return MOCK_LOGS[:limit]

@app.get("/api/reports", response_model=List[ReportRecord])
async def get_reports(limit: int = 50):
    """Get report history"""
    # TODO: Replace with real reports from report manager
    return MOCK_REPORTS[:limit]

@app.post("/api/patrol", response_model=PatrolResponse)
async def start_patrol(request: PatrolRequest):
    """启动新的巡查任务"""
    try:
        # 使用任务管理器创建任务
        task_id = task_manager.create_task(
            platform=request.platform,
            keyword=request.keyword,
            max_items=request.max_items,
            test_mode=request.test_mode
        )

        return PatrolResponse(
            task_id=task_id,
            status="started",
            message=f"巡查任务已启动，任务ID: {task_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动任务失败: {str(e)}")

@app.get("/api/patrol/{task_id}")
async def get_patrol_status(task_id: str):
    """获取巡查任务状态"""
    status = task_manager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="任务不存在")
    return status

@app.get("/api/patrol/{task_id}/logs")
async def get_patrol_logs(task_id: str, since: int = 0):
    """获取巡查任务日志"""
    logs = task_manager.get_task_logs(task_id, since)
    if logs is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return logs

@app.get("/api/patrol/{task_id}/logs/new")
async def get_new_patrol_logs(task_id: str):
    """获取巡查任务新日志（实时轮询）"""
    logs = task_manager.get_new_task_logs(task_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return logs

@app.get("/api/platforms")
async def get_platforms():
    """Get supported platforms"""
    if ANTI_PIRACY_AVAILABLE:
        return list(SUPPORTED_PLATFORMS.keys())
    return ["xianyu", "xhs", "taobao"]  # Default mock platforms

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    # TODO: Implement real statistics
    return {
        "total_merchants": len(MOCK_MERCHANTS),
        "pirated_count": len([m for m in MOCK_MERCHANTS if m["status"] == "pirated"]),
        "official_count": len([m for m in MOCK_MERCHANTS if m["status"] == "official"]),
        "total_reports": len(MOCK_REPORTS),
        "total_loss_prevented": sum(r["lossPrevented"] for r in MOCK_REPORTS)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)