#!/usr/bin/env /Users/Apple/Documents/GUI/anti_piracy_system/venv/bin/python3
"""
反盗版检测演示脚本

不需要连接手机或模型服务,纯粹演示检测逻辑
"""

from product_database import ProductDatabase, GenuineProduct
from piracy_detector import PiracyDetector, ProductInfo
from report_manager import ReportManager


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_detection():
    """演示盗版检测功能"""

    print_header("反盗版检测系统演示")

    # 1. 初始化数据库
    print("📦 加载正版商品数据库...")
    db = ProductDatabase("data/genuine_products.json")

    stats = db.get_stats()
    print(f"   已加载 {stats['total_products']} 个正版商品")
    print(f"   平台分布: {stats['platforms']}")
    print(f"   类别分布: {stats['categories']}")

    # 2. 初始化检测器
    print("\n🔍 初始化盗版检测器...")
    detector = PiracyDetector(db, price_threshold=0.7, similarity_threshold=0.6)
    print("   价格阈值: 70% (低于此比例触发警告)")
    print("   相似度阈值: 60%")

    # 3. 初始化举报管理器
    print("\n📢 初始化举报管理器...")
    report_manager = ReportManager("logs/report_history.json")

    # 4. 测试案例
    print_header("测试案例")

    test_cases = [
        {
            "name": "案例1: 正版商品(官方店铺)",
            "product": ProductInfo(
                title="薛兆丰的经济学课 正版",
                shop_name="得到官方旗舰店",
                price=199.0,
                platform="小红书",
                description="官方正版课程"
            )
        },
        {
            "name": "案例2: 疑似盗版(价格过低)",
            "product": ProductInfo(
                title="薛兆丰经济学课程 超低价",
                shop_name="某个人卖家",
                price=9.9,
                platform="闲鱼",
                description="经济学课程资料"
            )
        },
        {
            "name": "案例3: 疑似盗版(非官方店铺+低价)",
            "product": ProductInfo(
                title="得到 薛兆丰经济学 课程资料",
                shop_name="便宜资料店",
                price=19.9,
                platform="淘宝",
                description="薛兆丰经济学全套"
            )
        },
        {
            "name": "案例4: 不相关商品",
            "product": ProductInfo(
                title="Python 编程入门教程",
                shop_name="某教育机构",
                price=99.0,
                platform="小红书"
            )
        },
        {
            "name": "案例5: 正版商品(价格略高)",
            "product": ProductInfo(
                title="吴军的阅读与写作讲义",
                shop_name="得到App官方店",
                price=78.0,
                platform="小红书"
            )
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{'─' * 60}")
        print(f"🧪 {case['name']}")
        print(f"{'─' * 60}")

        product = case['product']
        print(f"📝 商品信息:")
        print(f"   标题: {product.title}")
        print(f"   店铺: {product.shop_name}")
        print(f"   价格: ¥{product.price}")
        print(f"   平台: {product.platform}")

        # 执行检测
        print(f"\n🔍 执行检测...")
        result = detector.detect(product)

        # 显示结果
        print(f"\n📊 检测结果:")
        if result.is_piracy:
            print(f"   ❌ 疑似盗版 (置信度: {result.confidence:.0%})")
        else:
            print(f"   ✅ 正常 (置信度: {result.confidence:.0%})")

        print(f"\n   判定依据:")
        for reason in result.reasons:
            print(f"   • {reason}")

        # 如果是盗版,创建举报记录
        if result.is_piracy:
            print(f"\n📢 创建举报记录...")
            report = report_manager.create_report(
                platform=product.platform,
                target_title=product.title,
                target_shop=product.shop_name,
                target_price=product.price,
                detection_result=result.to_dict()
            )
            print(f"   举报ID: {report.report_id}")
            print(f"   举报状态: {report.report_status}")

    # 5. 统计总结
    print_header("统计总结")

    print("📊 检测统计:")
    piracy_count = sum(1 for case in test_cases if detector.detect(case['product']).is_piracy)
    print(f"   总测试案例: {len(test_cases)}")
    print(f"   检测到盗版: {piracy_count}")
    print(f"   正常商品: {len(test_cases) - piracy_count}")

    print("\n📢 举报统计:")
    report_stats = report_manager.get_statistics()
    print(f"   总举报记录: {report_stats['total_reports']}")
    print(f"   平台分布: {report_stats['by_platform']}")
    print(f"   状态分布: {report_stats['by_status']}")

    print_header("演示完成")
    print("✅ 盗版检测系统运行正常!")
    print("\n💡 提示:")
    print("   • 这是纯检测逻辑演示,不需要连接手机或模型")
    print("   • 实际使用时需要配置模型服务(Open-AutoGLM)")
    print("   • 可以通过 --add-product 添加更多正版商品")
    print("   • 查看 README.md 了解完整使用方法")


if __name__ == "__main__":
    try:
        demo_detection()
    except KeyboardInterrupt:
        print("\n\n⚠️  演示中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
