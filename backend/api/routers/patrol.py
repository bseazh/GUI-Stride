"""
巡查任务路由
"""
import uuid
from typing import Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

# 任务状态枚举
from enum import Enum
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# 数据模型
class PatrolParams(BaseModel):
    """启动巡查任务的参数"""
    platform: str = Field(..., description="目标平台: xiaohongshu/xianyu/taobao")
    keyword: str = Field(..., description="搜索关键词")
    max_items: int = Field(10, description="最大检查商品数", ge=1, le=100)
    test_mode: bool = Field(True, description="测试模式（不实际举报）")
    device_id: Optional[str] = Field(None, description="设备ID（可选）")
    device_type: Optional[str] = Field("adb", description="设备类型: adb/hdc/wda")

class DetectionResult(BaseModel):
    """单商品检测结果"""
    title: str
    shop_name: str
    price: float
    is_piracy: bool
    confidence: float
    reasons: List[str]
    report_status: Optional[str] = None

class PatrolResult(BaseModel):
    """巡查任务结果"""
    checked_count: int = 0
    piracy_count: int = 0
    reported_count: int = 0
    details: List[DetectionResult] = []
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class PatrolTask(BaseModel):
    """巡查任务"""
    task_id: str
    status: TaskStatus
    params: PatrolParams
    result: Optional[PatrolResult] = None
    progress: float = Field(0.0, ge=0.0, le=1.0)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

# 内存中的任务存储（生产环境应使用数据库或Redis）
_tasks: Dict[str, PatrolTask] = {}

@router.post("/start", response_model=PatrolTask)
async def start_patrol(params: PatrolParams, background_tasks: BackgroundTasks):
    """启动新的巡查任务"""
    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 创建任务对象
    task = PatrolTask(
        task_id=task_id,
        status=TaskStatus.PENDING,
        params=params,
        progress=0.0,
        created_at=datetime.now()
    )

    # 存储任务
    _tasks[task_id] = task

    # 在后台运行任务
    background_tasks.add_task(run_patrol_task, task_id, params)

    return task

@router.get("/{task_id}", response_model=PatrolTask)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _tasks[task_id]

@router.get("/", response_model=List[PatrolTask])
async def get_task_history(limit: int = 20):
    """获取任务历史"""
    tasks = list(_tasks.values())
    # 按创建时间倒序排序
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    return tasks[:limit]

@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """取消任务"""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = _tasks[task_id]
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="任务已结束，无法取消")

    task.status = TaskStatus.CANCELLED
    task.completed_at = datetime.now()
    task.error_message = "任务被用户取消"

    return {"message": "任务已取消", "task_id": task_id}

# 后台任务执行函数
async def run_patrol_task(task_id: str, params: PatrolParams):
    """执行巡查任务（后台运行）"""
    try:
        task = _tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        # TODO: 调用反盗版系统包装器
        # 这里先模拟任务执行
        await simulate_patrol_task(task, params)

        task.status = TaskStatus.COMPLETED
        task.progress = 1.0
        task.completed_at = datetime.now()

    except Exception as e:
        task = _tasks.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()

async def simulate_patrol_task(task: PatrolTask, params: PatrolParams):
    """模拟巡查任务执行（用于测试）"""
    import asyncio
    import random

    # 模拟进度更新
    for i in range(10):
        await asyncio.sleep(1)
        task.progress = (i + 1) / 10
        # 更新任务状态
        _tasks[task.task_id] = task

    # 创建模拟结果
    result = PatrolResult(
        checked_count=params.max_items,
        piracy_count=random.randint(0, params.max_items // 2),
        reported_count=0 if params.test_mode else random.randint(0, params.max_items // 3),
        start_time=datetime.now(),
        end_time=datetime.now()
    )

    # 添加模拟详情
    for i in range(params.max_items):
        result.details.append(DetectionResult(
            title=f"测试商品 {i+1}",
            shop_name=f"测试店铺 {random.choice(['A', 'B', 'C'])}",
            price=random.uniform(10, 1000),
            is_piracy=random.choice([True, False]),
            confidence=random.uniform(0.5, 1.0),
            reasons=["价格异常", "非官方店铺"] if random.choice([True, False]) else [],
            report_status="已举报" if not params.test_mode and random.choice([True, False]) else None
        ))

    task.result = result