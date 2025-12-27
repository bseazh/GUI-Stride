#!/usr/bin/env python3
"""
反盗版自动巡查系统 - 主启动脚本

使用方法:
    python main_anti_piracy.py --platform xiaohongshu --keyword "得到" --max-items 10

功能:
- 在指定平台(小红书/闲鱼)搜索关键词
- 自动识别疑似盗版商品
- 执行举报操作
- 生成巡查报告
"""

import argparse
import sys
import os
from pathlib import Path

# 加载 .env 文件
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# 添加 Open-AutoGLM 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../Open-AutoGLM'))

from phone_agent.model import ModelConfig
from product_database import ProductDatabase, GenuineProduct
from anti_piracy_agent import AntiPiracyAgent
from config_anti_piracy import SUPPORTED_PLATFORMS, get_ui_text


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="反盗版自动巡查系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本使用 - 在小红书搜索"得到"
  python main_anti_piracy.py --platform xiaohongshu --keyword "得到"

  # 指定模型服务
  python main_anti_piracy.py --base-url http://localhost:8000/v1 --model autoglm-phone-9b

  # 测试模式(不实际举报)
  python main_anti_piracy.py --platform xianyu --test-mode

  # 添加正版商品到数据库
  python main_anti_piracy.py --add-product

  # 查看数据库统计
  python main_anti_piracy.py --show-stats

支持的平台:
  xiaohongshu - 小红书
  xianyu - 闲鱼
  taobao - 淘宝
        """
    )

    # 模型配置
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
        help="模型 API 地址"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
        help="模型名称"
    )
    parser.add_argument(
        "--apikey",
        type=str,
        default=os.getenv("PHONE_AGENT_API_KEY", "EMPTY"),
        help="API Key(如需要)"
    )

    # 平台配置
    parser.add_argument(
        "--platform",
        type=str,
        choices=list(SUPPORTED_PLATFORMS.keys()),
        default="xiaohongshu",
        help="目标平台"
    )

    # 巡查配置
    parser.add_argument(
        "--keyword",
        type=str,
        default="得到",
        help="搜索关键词"
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=10,
        help="最多检查的商品数量"
    )

    # 运行模式
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="测试模式(不实际执行举报操作)"
    )

    # 数据库管理
    parser.add_argument(
        "--add-product",
        action="store_true",
        help="交互式添加正版商品到数据库"
    )
    parser.add_argument(
        "--show-stats",
        action="store_true",
        help="显示数据库统计信息"
    )
    parser.add_argument(
        "--export-report",
        type=str,
        metavar="PATH",
        help="导出举报记录到文件"
    )

    # 设备配置
    parser.add_argument(
        "--device-id",
        type=str,
        help="ADB 设备 ID(多设备时使用)"
    )
    parser.add_argument(
        "--device-type",
        type=str,
        choices=["adb", "hdc", "ios"],
        default="adb",
        help="设备类型"
    )

    # 调试选项
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细日志"
    )

    return parser.parse_args()


def interactive_add_product():
    """交互式添加正版商品"""
    print("\n=== 添加正版商品到数据库 ===\n")

    product_id = input("商品ID (例如: dedao_001): ").strip()
    product_name = input("商品名称 (例如: 薛兆丰的经济学课): ").strip()
    shop_name = input("官方店铺名称 (例如: 得到官方旗舰店): ").strip()

    official_shops_input = input("所有官方店铺(逗号分隔): ").strip()
    official_shops = [s.strip() for s in official_shops_input.split(',')]

    original_price = float(input("正版价格 (例如: 199.0): ").strip())
    platform = input("所属平台 (例如: 得到): ").strip()
    category = input("商品类别 (例如: 电子书): ").strip()

    keywords_input = input("关键词(逗号分隔, 例如: 薛兆丰,经济学,得到): ").strip()
    keywords = [k.strip() for k in keywords_input.split(',')]

    description = input("商品描述(可选): ").strip() or None

    # 创建商品对象
    product = GenuineProduct(
        product_id=product_id,
        product_name=product_name,
        shop_name=shop_name,
        official_shops=official_shops,
        original_price=original_price,
        platform=platform,
        category=category,
        keywords=keywords,
        description=description
    )

    # 保存到数据库
    db = ProductDatabase()
    success = db.add_product(product)

    if success:
        print(f"\n✅ 成功添加商品: {product_name}")
        print(f"   商品ID: {product_id}")
        print(f"   原价: ¥{original_price}")
        print(f"   官方店铺: {', '.join(official_shops)}")
    else:
        print(f"\n❌ 添加商品失败")


def show_statistics():
    """显示数据库统计信息"""
    from report_manager import ReportManager

    print("\n" + "=" * 60)
    print("数据库统计信息")
    print("=" * 60)

    # 商品数据库统计
    product_db = ProductDatabase()
    product_stats = product_db.get_stats()

    print(f"\n📦 正版商品数据库:")
    print(f"   总商品数: {product_stats['total_products']}")
    print(f"   平台分布: {product_stats['platforms']}")
    print(f"   类别分布: {product_stats['categories']}")

    # 举报记录统计
    report_manager = ReportManager()
    report_stats = report_manager.get_statistics()

    print(f"\n📢 举报记录:")
    print(f"   总举报数: {report_stats['total_reports']}")
    print(f"   平台分布: {report_stats['by_platform']}")
    print(f"   状态分布: {report_stats['by_status']}")

    print("\n" + "=" * 60)


def main():
    """主函数"""
    args = parse_args()

    # 数据库管理功能
    if args.add_product:
        interactive_add_product()
        return

    if args.show_stats:
        show_statistics()
        return

    if args.export_report:
        from report_manager import ReportManager
        manager = ReportManager()
        success = manager.export_to_file(args.export_report, format="txt")
        if success:
            print(f"✅ 举报记录已导出到: {args.export_report}")
        return

    # 打印启动信息
    print("\n" + "=" * 60)
    print("🛡️  反盗版自动巡查系统")
    print("=" * 60)
    print(f"平台: {SUPPORTED_PLATFORMS[args.platform]['name']}")
    print(f"关键词: {args.keyword}")
    print(f"最大检查数: {args.max_items}")
    print(f"运行模式: {'🧪 测试模式' if args.test_mode else '⚡ 正式模式'}")
    print(f"模型: {args.model}")
    print(f"API 地址: {args.base_url}")
    print("=" * 60 + "\n")

    # 确认开始
    if not args.test_mode:
        confirm = input("⚠️  正式模式将实际执行举报操作,是否继续? (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return

    try:
        # 配置模型
        model_config = ModelConfig(
            base_url=args.base_url,
            model_name=args.model,
            api_key=args.apikey
        )

        # 创建 Agent
        agent = AntiPiracyAgent(
            model_config=model_config,
            platform=args.platform,
            test_mode=args.test_mode
        )

        # 开始巡查
        result = agent.start_patrol(
            keyword=args.keyword,
            max_items=args.max_items
        )

        # 显示结果
        print("\n" + "=" * 60)
        print("✅ 巡查完成!")
        print("=" * 60)
        print(f"检查商品数: {result['checked_count']}")
        print(f"发现疑似盗版: {result['piracy_count']}")
        print(f"已举报数: {result['reported_count']}")
        print("=" * 60 + "\n")

        # 询问是否查看详细报告
        if result['checked_count'] > 0:
            view_detail = input("是否查看详细报告? (y/N): ").strip().lower()
            if view_detail == 'y':
                stats = agent.get_patrol_statistics()
                print("\n详细统计信息:")
                print(stats)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        return

    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ 运行出错: {e}")

        # 提供针对性的解决建议
        if "502" in error_msg or "Bad Gateway" in error_msg:
            print("\n💡 解决建议:")
            print("   模型服务返回 502 错误,请运行诊断工具:")
            print("   python diagnose_model_service.py")
            print("")
            print("   或者尝试使用演示模式查看检测逻辑:")
            print("   python demo_detection.py")
        elif "Connection" in error_msg or "连接" in error_msg:
            print("\n💡 解决建议:")
            print("   1. 检查模型服务是否已启动")
            print(f"   2. 验证 API 地址: {args.base_url}")
            print("   3. 运行诊断工具: python diagnose_model_service.py")

        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
