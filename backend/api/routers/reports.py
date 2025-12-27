"""
举报记录管理路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json

from ..utils.anti_piracy_wrapper import get_wrapper

router = APIRouter()

# 数据模型
class ReportRecord(BaseModel):
    """举报记录"""
    report_id: str
    platform: str
    target_title: str
    target_shop: str
    target_price: float
    status: str  # pending/success/failed
    created_at: datetime
    updated_at: datetime
    notes: Optional[str] = None
    screenshot_path: Optional[str] = None

class ReportStatistics(BaseModel):
    """举报统计"""
    total_reports: int = 0
    successful_reports: int = 0
    failed_reports: int = 0
    pending_reports: int = 0
    by_platform: dict = {}
    by_status: dict = {}
    last_7_days: List[dict] = []

class ExportRequest(BaseModel):
    """导出请求"""
    format: str = Field("json", description="导出格式: json/csv/txt")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None

@router.get("/", response_model=List[ReportRecord])
async def get_reports(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
):
    """获取举报记录列表"""
    # TODO: 实现从数据库查询举报记录
    # 这里先返回模拟数据
    reports = []
    for i in range(min(5, limit)):
        reports.append(ReportRecord(
            report_id=f"report_{i}",
            platform="xiaohongshu",
            target_title=f"测试商品 {i}",
            target_shop=f"测试店铺 {i}",
            target_price=99.9 + i * 10,
            status="success" if i % 3 == 0 else "failed" if i % 3 == 1 else "pending",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            notes="测试举报记录",
            screenshot_path=f"/screenshots/report_{i}.png"
        ))
    return reports

@router.get("/statistics", response_model=ReportStatistics)
async def get_report_statistics():
    """获取举报统计"""
    try:
        wrapper = get_wrapper()
        stats = await wrapper.get_report_statistics()

        return ReportStatistics(
            total_reports=stats.get("total_reports", 0),
            successful_reports=stats.get("successful_reports", 0),
            failed_reports=stats.get("failed_reports", 0),
            pending_reports=stats.get("pending_reports", 0),
            by_platform=stats.get("by_platform", {}),
            by_status={
                "success": stats.get("successful_reports", 0),
                "failed": stats.get("failed_reports", 0),
                "pending": stats.get("pending_reports", 0)
            },
            last_7_days=[]
        )
    except Exception as e:
        # 返回模拟数据
        return ReportStatistics(
            total_reports=15,
            successful_reports=10,
            failed_reports=3,
            pending_reports=2,
            by_platform={"xiaohongshu": 10, "xianyu": 5},
            by_status={"success": 10, "failed": 3, "pending": 2},
            last_7_days=[]
        )

@router.post("/export")
async def export_reports(request: ExportRequest):
    """导出举报记录"""
    try:
        # TODO: 实现实际导出逻辑
        # 这里先返回模拟数据

        # 模拟导出数据
        export_data = {
            "format": request.format,
            "records": [
                {
                    "report_id": "report_1",
                    "platform": "xiaohongshu",
                    "target_title": "测试商品",
                    "status": "success",
                    "created_at": "2025-12-27T10:00:00Z"
                }
            ],
            "exported_at": datetime.now().isoformat()
        }

        if request.format == "json":
            content = json.dumps(export_data, indent=2, ensure_ascii=False)
            content_type = "application/json"
            filename = f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        elif request.format == "csv":
            content = "report_id,platform,target_title,status,created_at\nreport_1,xiaohongshu,测试商品,success,2025-12-27T10:00:00Z"
            content_type = "text/csv"
            filename = f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        else:
            content = str(export_data)
            content_type = "text/plain"
            filename = f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        return {
            "success": True,
            "filename": filename,
            "content_type": content_type,
            "content": content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@router.get("/{report_id}")
async def get_report_details(report_id: str):
    """获取举报记录详情"""
    # TODO: 实现从数据库查询举报详情
    return {
        "report_id": report_id,
        "platform": "xiaohongshu",
        "target_title": "测试商品",
        "details": "这是举报详情"
    }