#!/usr/bin/env python3
"""
盗版检测逻辑测试

单独测试检测逻辑，不需要连接手机。

使用方法:
    cd /Users/Apple/Documents/GUI/anti_piracy_system
    source venv/bin/activate
    python test/test_detection.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product_database import ProductDatabase
from piracy_detector import PiracyDetector, ProductInfo


def test_detection():
    """测试盗版检测逻辑"""
    print("\n" + "=" * 60)
    print("盗版检测逻辑测试 - 众合法考")
    print("=" * 60)

    # 初始化
    db = ProductDatabase("data/genuine_products.json")
    detector = PiracyDetector(db, price_threshold=0.7)

    print(f"\n数据库状态: {db.get_stats()}")

    # 测试案例
    test_cases = [
        {
            "name": "正版商品（官方店铺 + 正常价格）",
            "info": ProductInfo(
                title="2026众合法考客观题学习包",
                shop_name="方圆众合教育",
                price=898.0,
                platform="小红书"
            ),
            "expected": False
        },
        {
            "name": "疑似盗版（价格过低 11%）",
            "info": ProductInfo(
                title="众合法考客观题学习包",
                shop_name="某个人卖家",
                price=99.0,
                platform="小红书"
            ),
            "expected": True
        },
        {
            "name": "疑似盗版（非官方店铺 + 低价）",
            "info": ProductInfo(
                title="众合法考 技术流 书课包",
                shop_name="便宜资料店",
                price=199.0,
                platform="闲鱼"
            ),
            "expected": True
        },
        {
            "name": "边界情况（70%价格阈值）",
            "info": ProductInfo(
                title="众合法考学习包",
                shop_name="某店铺",
                price=628.6,  # 898 * 0.7 = 628.6
                platform="小红书"
            ),
            "expected": False  # 刚好在阈值上，不触发价格警告
        },
        {
            "name": "无法匹配的商品",
            "info": ProductInfo(
                title="Python 编程教程",
                shop_name="某教育机构",
                price=99.0,
                platform="淘宝"
            ),
            "expected": False
        }
    ]

    passed = 0
    failed = 0

    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        result = detector.detect(case['info'])

        status = "盗版" if result.is_piracy else "正常/无法判断"
        is_correct = result.is_piracy == case['expected']
        mark = "✅" if is_correct else "❌"

        print(f"   商品: {case['info'].title}")
        print(f"   店铺: {case['info'].shop_name}")
        print(f"   价格: ¥{case['info'].price}")
        print(f"   检测结果: {status} (置信度: {result.confidence:.0%})")
        print(f"   预期: {'盗版' if case['expected'] else '正常'} {mark}")

        if result.reasons:
            print(f"   判定依据:")
            for reason in result.reasons[:3]:
                print(f"      • {reason}")

        if is_correct:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = test_detection()
    sys.exit(0 if success else 1)
