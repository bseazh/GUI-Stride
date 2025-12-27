"""盗版识别逻辑引擎

实现三层判断机制:
1. 店铺名称匹配
2. 价格比对(低于原价70%触发)
3. 内容识别(基于OCR和多模态模型)
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from product_database import ProductDatabase, GenuineProduct


@dataclass
class ProductInfo:
    """待检测商品信息"""

    title: str  # 商品标题
    shop_name: str  # 店铺名称
    price: float  # 商品价格
    description: Optional[str] = None  # 商品描述
    ocr_text: Optional[str] = None  # OCR提取的文本
    image_analysis: Optional[str] = None  # 图像分析结果
    url: Optional[str] = None  # 商品链接
    platform: str = "未知平台"  # 平台名称(小红书/闲鱼等)


@dataclass
class DetectionResult:
    """检测结果"""

    is_piracy: bool  # 是否为盗版
    confidence: float  # 置信度(0-1)
    reasons: List[str]  # 判定依据列表
    matched_product: Optional[GenuineProduct] = None  # 匹配到的正版商品
    shop_check: bool = False  # 店铺检查是否通过
    price_check: bool = False  # 价格检查是否通过
    content_check: bool = False  # 内容检查是否通过
    price_ratio: Optional[float] = None  # 价格比例
    detected_at: str = None  # 检测时间

    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "is_piracy": self.is_piracy,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "matched_product_id": self.matched_product.product_id if self.matched_product else None,
            "matched_product_name": self.matched_product.product_name if self.matched_product else None,
            "shop_check": self.shop_check,
            "price_check": self.price_check,
            "content_check": self.content_check,
            "price_ratio": self.price_ratio,
            "detected_at": self.detected_at
        }


class PiracyDetector:
    """盗版检测器"""

    def __init__(
        self,
        product_db: ProductDatabase,
        price_threshold: float = 0.7,  # 价格阈值(低于此比例触发警告)
        similarity_threshold: float = 0.6  # 内容相似度阈值
    ):
        """
        初始化检测器

        Args:
            product_db: 正版商品数据库
            price_threshold: 价格阈值,低于原价的该比例将触发盗版警告
            similarity_threshold: 内容相似度阈值
        """
        self.product_db = product_db
        self.price_threshold = price_threshold
        self.similarity_threshold = similarity_threshold

    def detect(self, product_info: ProductInfo) -> DetectionResult:
        """
        检测商品是否为盗版

        Args:
            product_info: 待检测商品信息

        Returns:
            检测结果
        """
        # Step 1: 尝试匹配正版商品
        matched_product = self._match_genuine_product(product_info)

        if not matched_product:
            # 无法匹配到正版商品,无法判断
            return DetectionResult(
                is_piracy=False,
                confidence=0.0,
                reasons=["未能匹配到对应的正版商品信息,无法判断"],
                matched_product=None
            )

        # Step 2: 店铺名称检查
        shop_check_passed, shop_reason = self._check_shop_name(
            product_info.shop_name,
            matched_product
        )

        # Step 3: 价格检查
        price_check_passed, price_reason, price_ratio = self._check_price(
            product_info.price,
            matched_product.original_price
        )

        # Step 4: 内容检查
        content_check_passed, content_reason = self._check_content(
            product_info,
            matched_product
        )

        # 综合判断
        reasons = []
        confidence = 0.0

        # 如果店铺名称匹配,大概率是正版
        if shop_check_passed:
            reasons.append(shop_reason)
            return DetectionResult(
                is_piracy=False,
                confidence=0.9,
                reasons=reasons,
                matched_product=matched_product,
                shop_check=True,
                price_check=price_check_passed,
                content_check=content_check_passed,
                price_ratio=price_ratio
            )

        # 店铺名称不匹配,检查价格和内容
        if not shop_check_passed:
            reasons.append(shop_reason)
            confidence += 0.4  # 店铺不匹配增加40%可疑度

        if not price_check_passed:
            reasons.append(price_reason)
            confidence += 0.4  # 价格异常增加40%可疑度

        if content_check_passed:
            reasons.append(content_reason)
            confidence += 0.2  # 内容匹配增加20%可疑度

        # 判定为盗版的条件:
        # 1. 店铺不匹配 + 价格低于阈值 + 内容匹配
        # 2. 综合置信度超过0.7
        is_piracy = (not shop_check_passed and not price_check_passed and content_check_passed) or confidence >= 0.7

        return DetectionResult(
            is_piracy=is_piracy,
            confidence=confidence,
            reasons=reasons,
            matched_product=matched_product,
            shop_check=shop_check_passed,
            price_check=price_check_passed,
            content_check=content_check_passed,
            price_ratio=price_ratio
        )

    def _match_genuine_product(self, product_info: ProductInfo) -> Optional[GenuineProduct]:
        """
        匹配正版商品

        Args:
            product_info: 待检测商品信息

        Returns:
            匹配到的正版商品,如果没有匹配则返回None
        """
        # 方法1: 通过商品名称精确匹配
        results = self.product_db.search_by_name(product_info.title)
        if results:
            # 返回第一个匹配结果
            return results[0]

        # 方法2: 通过关键词匹配
        keywords = self._extract_keywords(product_info.title)
        if keywords:
            results = self.product_db.search_by_keywords(keywords)
            if results:
                return results[0]

        # 方法3: 通过OCR文本匹配
        if product_info.ocr_text:
            for product in self.product_db.get_all_products():
                if product.keywords:
                    # 检查是否有关键词出现在OCR文本中
                    if any(kw in product_info.ocr_text for kw in product.keywords):
                        return product

        return None

    def _check_shop_name(
        self,
        shop_name: str,
        genuine_product: GenuineProduct
    ) -> Tuple[bool, str]:
        """
        检查店铺名称

        Args:
            shop_name: 待检测店铺名称
            genuine_product: 正版商品信息

        Returns:
            (是否通过检查, 检查原因说明)
        """
        # 检查是否为官方店铺
        is_official = self.product_db.is_official_shop(shop_name, genuine_product.product_id)

        if is_official:
            return True, f"✅ 店铺名称匹配官方店铺: '{shop_name}'"
        else:
            return False, f"❌ 店铺名称'{shop_name}'不在官方授权列表中(官方店铺: {', '.join(genuine_product.official_shops)})"

    def _check_price(
        self,
        current_price: float,
        original_price: float
    ) -> Tuple[bool, str, float]:
        """
        检查价格

        Args:
            current_price: 当前价格
            original_price: 正版原价

        Returns:
            (是否通过检查, 检查原因说明, 价格比例)
        """
        if original_price <= 0:
            return True, "⚠️ 原价信息无效,跳过价格检查", 0.0

        price_ratio = current_price / original_price

        if price_ratio >= self.price_threshold:
            return True, f"✅ 价格正常: ¥{current_price} (原价¥{original_price}的{price_ratio:.0%})", price_ratio
        else:
            return False, f"❌ 价格异常: ¥{current_price} 仅为原价¥{original_price}的{price_ratio:.0%},低于{self.price_threshold:.0%}阈值", price_ratio

    def _check_content(
        self,
        product_info: ProductInfo,
        genuine_product: GenuineProduct
    ) -> Tuple[bool, str]:
        """
        检查内容相似度

        Args:
            product_info: 待检测商品信息
            genuine_product: 正版商品信息

        Returns:
            (是否匹配, 检查原因说明)
        """
        # 检查标题相似度
        title_similarity = self._calculate_text_similarity(
            product_info.title,
            genuine_product.product_name
        )

        # 检查描述相似度
        description_similarity = 0.0
        if product_info.description and genuine_product.description:
            description_similarity = self._calculate_text_similarity(
                product_info.description,
                genuine_product.description
            )

        # 检查关键词匹配度
        keyword_match_count = 0
        if genuine_product.keywords:
            combined_text = f"{product_info.title} {product_info.description or ''} {product_info.ocr_text or ''}"
            for keyword in genuine_product.keywords:
                if keyword in combined_text:
                    keyword_match_count += 1

        keyword_match_ratio = keyword_match_count / len(genuine_product.keywords) if genuine_product.keywords else 0

        # 综合相似度
        overall_similarity = (title_similarity * 0.5 + description_similarity * 0.2 + keyword_match_ratio * 0.3)

        if overall_similarity >= self.similarity_threshold:
            return True, f"✅ 内容匹配度高: {overall_similarity:.0%} (标题:{title_similarity:.0%}, 关键词:{keyword_match_ratio:.0%})"
        else:
            return False, f"⚠️ 内容匹配度较低: {overall_similarity:.0%}"

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度(简单的字符匹配)

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度(0-1)
        """
        if not text1 or not text2:
            return 0.0

        # 转换为小写并移除标点符号
        text1_clean = re.sub(r'[^\w\s]', '', text1.lower())
        text2_clean = re.sub(r'[^\w\s]', '', text2.lower())

        # 计算共同字符数
        common_chars = sum(1 for c in text1_clean if c in text2_clean)
        max_len = max(len(text1_clean), len(text2_clean))

        if max_len == 0:
            return 0.0

        return common_chars / max_len

    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词

        Args:
            text: 输入文本

        Returns:
            关键词列表
        """
        # 移除标点符号
        text_clean = re.sub(r'[^\w\s]', ' ', text)

        # 分词(简单的空格分割)
        words = text_clean.split()

        # 过滤短词和常见词
        stop_words = {'的', '了', '和', '是', '在', '有', '与', '及', '等', '为'}
        keywords = [w for w in words if len(w) > 1 and w not in stop_words]

        return keywords


# 示例使用
if __name__ == "__main__":
    # 创建数据库和检测器
    db = ProductDatabase("../data/genuine_products.json")

    # 添加测试商品
    from product_database import GenuineProduct

    test_product = GenuineProduct(
        product_id="dedao_001",
        product_name="薛兆丰的经济学课",
        shop_name="得到官方旗舰店",
        official_shops=["得到官方旗舰店", "得到App官方店"],
        original_price=199.0,
        platform="得到",
        category="电子书",
        keywords=["薛兆丰", "经济学", "得到"]
    )
    db.add_product(test_product)

    # 创建检测器
    detector = PiracyDetector(db, price_threshold=0.7)

    # 测试案例1: 正版商品(官方店铺)
    print("\n=== 测试案例1: 正版商品 ===")
    case1 = ProductInfo(
        title="薛兆丰的经济学课 官方正版",
        shop_name="得到官方旗舰店",
        price=199.0,
        platform="小红书"
    )
    result1 = detector.detect(case1)
    print(f"检测结果: {'盗版' if result1.is_piracy else '正版'}")
    print(f"置信度: {result1.confidence:.0%}")
    print(f"判定依据:\n  " + "\n  ".join(result1.reasons))

    # 测试案例2: 疑似盗版(价格过低)
    print("\n=== 测试案例2: 疑似盗版 ===")
    case2 = ProductInfo(
        title="薛兆丰经济学课程 超低价",
        shop_name="某个人卖家",
        price=9.9,
        platform="闲鱼"
    )
    result2 = detector.detect(case2)
    print(f"检测结果: {'盗版' if result2.is_piracy else '正版'}")
    print(f"置信度: {result2.confidence:.0%}")
    print(f"判定依据:\n  " + "\n  ".join(result2.reasons))

    # 测试案例3: 无法匹配
    print("\n=== 测试案例3: 无法匹配 ===")
    case3 = ProductInfo(
        title="完全不相关的商品",
        shop_name="某店铺",
        price=50.0,
        platform="淘宝"
    )
    result3 = detector.detect(case3)
    print(f"检测结果: {'盗版' if result3.is_piracy else '正版/无法判断'}")
    print(f"置信度: {result3.confidence:.0%}")
    print(f"判定依据:\n  " + "\n  ".join(result3.reasons))
