"""
反盗版系统包装器 - 将现有命令行功能包装为Python函数
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

# 添加Open-AutoGLM到Python路径
project_root = Path(__file__).parent.parent.parent.parent
open_autoglm_path = project_root / "Open-AutoGLM"
if open_autoglm_path.exists():
    sys.path.insert(0, str(open_autoglm_path))

# 添加反盗版系统到Python路径
anti_piracy_path = project_root / "anti_piracy_system"
if anti_piracy_path.exists():
    sys.path.insert(0, str(anti_piracy_path))

# 尝试导入反盗版系统模块
try:
    from phone_agent.model import ModelConfig
    from anti_piracy_agent import AntiPiracyAgent
    from piracy_detector import PiracyDetector, ProductInfo, DetectionResult as PiracyDetectionResult
    from product_database import ProductDatabase, GenuineProduct
    from report_manager import ReportManager
    from config_anti_piracy import SUPPORTED_PLATFORMS, get_ui_text
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"警告: 导入反盗版系统模块失败 - {e}")
    IMPORT_SUCCESS = False

@dataclass
class PatrolTaskParams:
    """巡查任务参数"""
    platform: str  # xiaohongshu/xianyu/taobao
    keyword: str
    max_items: int = 10
    test_mode: bool = True
    device_id: Optional[str] = None
    device_type: str = "adb"

@dataclass
class PatrolTaskResult:
    """巡查任务结果"""
    checked_count: int = 0
    piracy_count: int = 0
    reported_count: int = 0
    details: List[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []

class AntiPiracyWrapper:
    """反盗版系统包装器"""

    def __init__(self):
        self.model_config = None
        self.agent = None
        self.detector = None
        self.database = None
        self.report_manager = None

    def initialize(self):
        """初始化反盗版系统组件"""
        if not IMPORT_SUCCESS:
            raise RuntimeError("反盗版系统模块导入失败，无法初始化")

        # 从环境变量加载配置
        base_url = os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1")
        model_name = os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b")
        api_key = os.getenv("PHONE_AGENT_API_KEY", "EMPTY")

        # 创建模型配置
        self.model_config = ModelConfig(
            base_url=base_url,
            model_name=model_name,
            api_key=api_key
        )

        # 初始化数据库
        self.database = ProductDatabase()

        # 初始化检测器
        self.detector = PiracyDetector(self.database)

        # 初始化报告管理器
        self.report_manager = ReportManager()

        print("反盗版系统包装器初始化完成")

    async def start_patrol(self, params: PatrolTaskParams) -> PatrolTaskResult:
        """
        启动巡查任务

        参数:
            params: 巡查任务参数

        返回:
            PatrolTaskResult: 巡查任务结果
        """
        result = PatrolTaskResult(start_time=datetime.now())

        try:
            if not self.agent or self.agent.platform != params.platform:
                # 创建Agent实例
                self.agent = AntiPiracyAgent(
                    model_config=self.model_config,
                    platform=params.platform,
                    test_mode=params.test_mode
                )

            # 执行巡查
            patrol_result = self.agent.start_patrol(
                keyword=params.keyword,
                max_items=params.max_items
            )

            # 转换结果
            result.checked_count = patrol_result.get("checked_count", 0)
            result.piracy_count = patrol_result.get("piracy_count", 0)
            result.reported_count = patrol_result.get("reported_count", 0)

            # 提取详情
            details = patrol_result.get("details", [])
            for detail in details:
                result.details.append({
                    "title": detail.get("title", ""),
                    "shop_name": detail.get("shop_name", ""),
                    "price": detail.get("price", 0),
                    "is_piracy": detail.get("is_piracy", False),
                    "confidence": detail.get("confidence", 0),
                    "reasons": detail.get("reasons", []),
                    "report_status": detail.get("report_status")
                })

            result.end_time = datetime.now()

        except Exception as e:
            result.error_message = str(e)
            print(f"巡查任务执行失败: {e}")

        return result

    async def detect_single_product(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测单个商品是否为盗版

        参数:
            product_info: 商品信息字典

        返回:
            检测结果字典
        """
        if not self.detector:
            self.initialize()

        # 创建ProductInfo对象
        info = ProductInfo(
            title=product_info.get("title", ""),
            shop_name=product_info.get("shop_name", ""),
            price=product_info.get("price", 0),
            description=product_info.get("description", ""),
            platform=product_info.get("platform", "unknown")
        )

        # 执行检测
        detection_result = self.detector.detect(info)

        # 转换结果
        return {
            "is_piracy": detection_result.is_piracy,
            "confidence": detection_result.confidence,
            "reasons": detection_result.reasons,
            "matched_genuine_product": detection_result.matched_genuine_product,
            "price_comparison": detection_result.price_comparison
        }

    async def add_genuine_product(self, product_data: Dict[str, Any]) -> bool:
        """
        添加正版商品到数据库

        参数:
            product_data: 正版商品数据

        返回:
            是否添加成功
        """
        if not self.database:
            self.initialize()

        try:
            product = GenuineProduct(
                product_id=product_data.get("product_id", ""),
                product_name=product_data.get("product_name", ""),
                shop_name=product_data.get("shop_name", ""),
                official_shops=product_data.get("official_shops", []),
                original_price=product_data.get("original_price", 0),
                platform=product_data.get("platform", ""),
                category=product_data.get("category", ""),
                keywords=product_data.get("keywords", [])
            )

            self.database.add_product(product)
            return True

        except Exception as e:
            print(f"添加正版商品失败: {e}")
            return False

    async def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息

        返回:
            统计信息字典
        """
        if not self.database:
            self.initialize()

        stats = self.database.get_stats()
        return {
            "total_products": stats.total_products,
            "platforms": stats.platforms,
            "categories": stats.categories
        }

    async def get_report_statistics(self) -> Dict[str, Any]:
        """
        获取举报统计信息

        返回:
            举报统计字典
        """
        if not self.report_manager:
            self.initialize()

        stats = self.report_manager.get_statistics()
        return {
            "total_reports": stats.total_reports,
            "successful_reports": stats.successful_reports,
            "failed_reports": stats.failed_reports,
            "pending_reports": stats.pending_reports,
            "by_platform": stats.by_platform
        }

    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """
        获取支持的平台列表

        返回:
            平台信息列表
        """
        platforms = []
        for key, info in SUPPORTED_PLATFORMS.items():
            platforms.append({
                "key": key,
                "name": info.get("name", key),
                "description": info.get("description", ""),
                "supported": info.get("supported", True)
            })
        return platforms

# 全局包装器实例
_wrapper_instance: Optional[AntiPiracyWrapper] = None

def get_wrapper() -> AntiPiracyWrapper:
    """获取包装器实例（单例）"""
    global _wrapper_instance
    if _wrapper_instance is None:
        _wrapper_instance = AntiPiracyWrapper()
        try:
            _wrapper_instance.initialize()
        except Exception as e:
            print(f"包装器初始化失败: {e}")
            # 继续使用包装器，但部分功能可能受限
    return _wrapper_instance

# 异步包装函数
async def run_patrol_task_async(params: PatrolTaskParams) -> PatrolTaskResult:
    """异步运行巡查任务"""
    wrapper = get_wrapper()
    return await wrapper.start_patrol(params)

async def detect_product_async(product_info: Dict[str, Any]) -> Dict[str, Any]:
    """异步检测单个商品"""
    wrapper = get_wrapper()
    return await wrapper.detect_single_product(product_info)

async def add_product_async(product_data: Dict[str, Any]) -> bool:
    """异步添加正版商品"""
    wrapper = get_wrapper()
    return await wrapper.add_genuine_product(product_data)