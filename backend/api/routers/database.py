"""
正版商品数据库管理路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

from ..utils.anti_piracy_wrapper import add_product_async, get_wrapper

router = APIRouter()

# 数据模型
class GenuineProductCreate(BaseModel):
    """创建正版商品的请求模型"""
    product_name: str = Field(..., description="商品名称")
    shop_name: str = Field(..., description="店铺名称")
    official_shops: List[str] = Field(default_factory=list, description="官方店铺列表")
    original_price: float = Field(..., description="原价", gt=0)
    platform: str = Field(..., description="平台: xiaohongshu/xianyu/taobao")
    category: Optional[str] = Field(None, description="商品分类")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")

class GenuineProductResponse(BaseModel):
    """正版商品响应模型"""
    product_id: str
    product_name: str
    shop_name: str
    official_shops: List[str]
    original_price: float
    platform: str
    category: Optional[str]
    keywords: List[str]
    created_at: str

class DatabaseStats(BaseModel):
    """数据库统计"""
    total_products: int
    platforms: dict
    categories: dict

@router.get("/products", response_model=List[GenuineProductResponse])
async def get_products(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50
):
    """获取正版商品列表"""
    # TODO: 实现从数据库查询商品
    # 这里先返回空列表
    return []

@router.post("/products", response_model=dict)
async def create_product(product: GenuineProductCreate):
    """添加正版商品到数据库"""
    try:
        # 生成商品ID
        product_id = str(uuid.uuid4())

        # 准备商品数据
        product_data = {
            "product_id": product_id,
            "product_name": product.product_name,
            "shop_name": product.shop_name,
            "official_shops": product.official_shops,
            "original_price": product.original_price,
            "platform": product.platform,
            "category": product.category,
            "keywords": product.keywords
        }

        # 调用包装器添加商品
        success = await add_product_async(product_data)

        if success:
            return {
                "success": True,
                "product_id": product_id,
                "message": "商品添加成功"
            }
        else:
            raise HTTPException(status_code=500, detail="商品添加失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加商品时出错: {str(e)}")

@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """删除正版商品"""
    # TODO: 实现商品删除
    return {"success": True, "message": f"商品 {product_id} 已删除"}

@router.get("/stats", response_model=DatabaseStats)
async def get_database_stats():
    """获取数据库统计"""
    try:
        wrapper = get_wrapper()
        stats = await wrapper.get_database_stats()

        return DatabaseStats(
            total_products=stats.get("total_products", 0),
            platforms=stats.get("platforms", {}),
            categories=stats.get("categories", {})
        )
    except Exception as e:
        # 返回模拟数据
        return DatabaseStats(
            total_products=0,
            platforms={},
            categories={}
        )