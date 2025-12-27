"""正版商品数据库管理模块

用于存储和管理正版商品信息,作为盗版识别的基准数据。
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class GenuineProduct:
    """正版商品数据模型"""

    product_id: str  # 商品唯一标识
    product_name: str  # 商品名称
    shop_name: str  # 官方店铺名称
    official_shops: List[str]  # 所有官方授权店铺名称列表
    original_price: float  # 正版原价
    platform: str  # 所属平台 (如"得到")
    category: str  # 商品类别 (如"电子书", "课程")
    description: Optional[str] = None  # 商品描述
    keywords: Optional[List[str]] = None  # 关键词列表
    created_at: str = None  # 添加时间
    updated_at: str = None  # 更新时间

    def __post_init__(self):
        """初始化时间戳"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.keywords is None:
            self.keywords = []

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'GenuineProduct':
        """从字典创建对象"""
        return cls(**data)


class ProductDatabase:
    """正版商品数据库管理类"""

    def __init__(self, db_path: str = "data/genuine_products.json"):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.products: Dict[str, GenuineProduct] = {}
        self._ensure_db_exists()
        self.load()

    def _ensure_db_exists(self):
        """确保数据库文件和目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def load(self) -> None:
        """从文件加载数据库"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.products = {
                    pid: GenuineProduct.from_dict(pdata)
                    for pid, pdata in data.items()
                }
            print(f"✅ 已加载 {len(self.products)} 个正版商品信息")
        except Exception as e:
            print(f"⚠️ 加载数据库失败: {e}")
            self.products = {}

    def save(self) -> None:
        """保存数据库到文件"""
        try:
            data = {pid: p.to_dict() for pid, p in self.products.items()}
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {len(self.products)} 个商品信息到数据库")
        except Exception as e:
            print(f"❌ 保存数据库失败: {e}")

    def add_product(self, product: GenuineProduct) -> bool:
        """
        添加正版商品

        Args:
            product: 正版商品对象

        Returns:
            是否添加成功
        """
        if product.product_id in self.products:
            print(f"⚠️ 商品 {product.product_id} 已存在,将更新信息")
            product.updated_at = datetime.now().isoformat()

        self.products[product.product_id] = product
        self.save()
        print(f"✅ 已添加/更新商品: {product.product_name}")
        return True

    def get_product(self, product_id: str) -> Optional[GenuineProduct]:
        """
        根据ID获取商品

        Args:
            product_id: 商品ID

        Returns:
            商品对象或None
        """
        return self.products.get(product_id)

    def search_by_name(self, product_name: str) -> List[GenuineProduct]:
        """
        根据商品名称搜索

        Args:
            product_name: 商品名称(支持部分匹配)

        Returns:
            匹配的商品列表
        """
        results = []
        for product in self.products.values():
            if product_name.lower() in product.product_name.lower():
                results.append(product)
        return results

    def search_by_keywords(self, keywords: List[str]) -> List[GenuineProduct]:
        """
        根据关键词搜索

        Args:
            keywords: 关键词列表

        Returns:
            匹配的商品列表
        """
        results = []
        for product in self.products.values():
            if not product.keywords:
                continue
            # 检查是否有任何关键词匹配
            if any(kw.lower() in ' '.join(product.keywords).lower() for kw in keywords):
                results.append(product)
        return results

    def is_official_shop(self, shop_name: str, product_id: str = None) -> bool:
        """
        检查是否为官方店铺

        Args:
            shop_name: 店铺名称
            product_id: 可选的商品ID,如果提供则只检查该商品

        Returns:
            是否为官方店铺
        """
        if product_id:
            product = self.get_product(product_id)
            if product:
                return shop_name in product.official_shops or shop_name == product.shop_name
            return False

        # 检查所有商品的官方店铺
        for product in self.products.values():
            if shop_name in product.official_shops or shop_name == product.shop_name:
                return True
        return False

    def get_all_products(self) -> List[GenuineProduct]:
        """获取所有商品"""
        return list(self.products.values())

    def delete_product(self, product_id: str) -> bool:
        """
        删除商品

        Args:
            product_id: 商品ID

        Returns:
            是否删除成功
        """
        if product_id in self.products:
            del self.products[product_id]
            self.save()
            print(f"✅ 已删除商品: {product_id}")
            return True
        print(f"⚠️ 商品不存在: {product_id}")
        return False

    def get_stats(self) -> Dict:
        """获取数据库统计信息"""
        platforms = {}
        categories = {}

        for product in self.products.values():
            platforms[product.platform] = platforms.get(product.platform, 0) + 1
            categories[product.category] = categories.get(product.category, 0) + 1

        return {
            "total_products": len(self.products),
            "platforms": platforms,
            "categories": categories
        }


# 示例使用
if __name__ == "__main__":
    # 创建数据库实例
    db = ProductDatabase("../data/genuine_products.json")

    # 添加示例商品
    sample_product = GenuineProduct(
        product_id="dedao_001",
        product_name="《薛兆丰的经济学课》电子书",
        shop_name="得到官方旗舰店",
        official_shops=["得到官方旗舰店", "得到App官方店"],
        original_price=199.0,
        platform="得到",
        category="电子书",
        description="经济学入门课程",
        keywords=["薛兆丰", "经济学", "得到", "电子书"]
    )

    db.add_product(sample_product)

    # 查询示例
    print("\n=== 数据库统计 ===")
    stats = db.get_stats()
    print(f"总商品数: {stats['total_products']}")
    print(f"平台分布: {stats['platforms']}")
    print(f"类别分布: {stats['categories']}")

    print("\n=== 搜索测试 ===")
    results = db.search_by_name("经济学")
    print(f"搜索'经济学'找到 {len(results)} 个结果")

    print("\n=== 店铺验证测试 ===")
    print(f"'得到官方旗舰店'是官方店铺: {db.is_official_shop('得到官方旗舰店')}")
    print(f"'某盗版店铺'是官方店铺: {db.is_official_shop('某盗版店铺')}")
