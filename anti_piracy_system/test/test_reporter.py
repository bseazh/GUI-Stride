#!/usr/bin/env python3
"""
举报模块测试脚本

快速验证：
1. 店铺名称提取
2. 盗版检测逻辑
3. 举报流程（使用 Mock Agent）

使用方法:
    cd /Users/Apple/Documents/GUI/anti_piracy_system
    source venv/bin/activate
    python test/test_reporter.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../Open-AutoGLM'))


class MockAgent:
    """模拟 Agent，用于测试举报流程"""

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.actions = []  # 记录所有执行的动作

    def run(self, prompt: str):
        """模拟执行提示词"""
        # 提取关键操作
        action = self._extract_action(prompt)
        self.actions.append(action)

        if self.verbose:
            print(f"   [MockAgent] {action}")

        return f"模拟执行: {action}"

    def _extract_action(self, prompt: str) -> str:
        """从提示词中提取关键操作"""
        if "..." in prompt or "三个点" in prompt or "更多" in prompt:
            return "点击右上角'...'菜单"
        elif "举报" in prompt and "点击" in prompt:
            return "点击举报按钮"
        elif "侵权" in prompt or "举报类型" in prompt:
            return "选择举报类型: 侵权举报"
        elif "输入" in prompt and "举报" in prompt:
            return "填写举报内容"
        elif "上传" in prompt or "图片" in prompt:
            return "上传证据图片"
        elif "提交" in prompt:
            return "提交举报"
        elif "返回" in prompt:
            return "返回列表页"
        else:
            return f"执行操作: {prompt[:30]}..."


class MockReportManager:
    """模拟举报管理器"""

    def __init__(self):
        self.reports = []

    def create_report(self, **kwargs):
        report_id = f"test_report_{len(self.reports)}"
        self.reports.append({"id": report_id, **kwargs})
        return type('Report', (), {'report_id': report_id, 'report_reason': '测试举报'})()

    def update_status(self, report_id, status, note):
        print(f"   [ReportManager] 更新状态: {report_id} -> {status}")

    def add_screenshot(self, report_id, path):
        print(f"   [ReportManager] 添加截图: {path}")


def test_reporter_module():
    """测试举报模块"""
    print("\n" + "=" * 60)
    print("测试 1: 举报模块导入和初始化")
    print("=" * 60)

    from reporter import create_reporter, ReportContext, XiaohongshuReporter

    mock_agent = MockAgent(verbose=False)
    mock_manager = MockReportManager()

    # 创建举报器
    reporter = create_reporter(
        platform="xiaohongshu",
        agent=mock_agent,
        report_manager=mock_manager,
        screenshot_dir="test/screenshots"
    )

    print(f"✅ 创建小红书举报器成功: {type(reporter).__name__}")

    # 测试举报理由生成
    print("\n" + "-" * 40)
    print("测试举报理由生成:")
    print("-" * 40)

    context = ReportContext(
        product_title="薛兆丰经济学课程 超低价",
        shop_name="某个人卖家",
        price=9.9,
        platform="小红书",
        detection_reasons=[
            "❌ 店铺名称'某个人卖家'不在官方授权列表中",
            "❌ 价格异常: ¥9.9 仅为原价¥199.0的5%",
            "✅ 内容匹配度高: 73%"
        ],
        confidence=0.8,
        matched_product_name="薛兆丰的经济学课",
        original_price=199.0,
        report_id="test_001"
    )

    reason = reporter.generate_report_reason(context)
    print(reason)

    return reporter, context


def test_report_flow():
    """测试完整举报流程"""
    print("\n" + "=" * 60)
    print("测试 2: 完整举报流程（Mock 模式）")
    print("=" * 60)

    from reporter import create_reporter, ReportContext

    mock_agent = MockAgent(verbose=True)
    mock_manager = MockReportManager()

    reporter = create_reporter(
        platform="xiaohongshu",
        agent=mock_agent,
        report_manager=mock_manager,
        screenshot_dir="test/screenshots"
    )

    context = ReportContext(
        product_title="薛兆丰经济学课程",
        shop_name="盗版店铺",
        price=9.9,
        platform="小红书",
        detection_reasons=["店铺不匹配", "价格过低"],
        confidence=0.85,
        report_id="test_flow_001"
    )

    print("\n开始执行举报流程...\n")
    success = reporter.execute_report(context)

    print(f"\n举报结果: {'成功' if success else '失败'}")
    print(f"执行的动作数: {len(mock_agent.actions)}")
    print(f"动作列表:")
    for i, action in enumerate(mock_agent.actions, 1):
        print(f"   {i}. {action}")

    return success


def test_detection_logic():
    """测试盗版检测逻辑"""
    print("\n" + "=" * 60)
    print("测试 3: 盗版检测逻辑")
    print("=" * 60)

    from product_database import ProductDatabase, GenuineProduct
    from piracy_detector import PiracyDetector, ProductInfo

    # 初始化数据库
    db = ProductDatabase("data/genuine_products.json")
    detector = PiracyDetector(db, price_threshold=0.7)

    print(f"\n数据库状态: {db.get_stats()}")

    # 测试案例
    test_cases = [
        {
            "name": "正版商品（官方店铺）",
            "info": ProductInfo(
                title="薛兆丰的经济学课",
                shop_name="得到官方旗舰店",
                price=199.0,
                platform="小红书"
            ),
            "expected": False  # 不是盗版
        },
        {
            "name": "疑似盗版（价格过低）",
            "info": ProductInfo(
                title="薛兆丰经济学课程 超值",
                shop_name="某个人卖家",
                price=9.9,
                platform="小红书"
            ),
            "expected": True  # 是盗版
        },
        {
            "name": "疑似盗版（非官方店铺）",
            "info": ProductInfo(
                title="得到 薛兆丰经济学",
                shop_name="便宜资料店",
                price=29.9,
                platform="闲鱼"
            ),
            "expected": True  # 是盗版
        },
        {
            "name": "无法匹配的商品",
            "info": ProductInfo(
                title="Python 编程教程",
                shop_name="某教育机构",
                price=99.0,
                platform="淘宝"
            ),
            "expected": False  # 无法判断
        }
    ]

    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        result = detector.detect(case['info'])

        status = "盗版" if result.is_piracy else "正常/无法判断"
        match = "✅" if result.is_piracy == case['expected'] else "❌"

        print(f"   商品: {case['info'].title}")
        print(f"   店铺: {case['info'].shop_name}")
        print(f"   价格: ¥{case['info'].price}")
        print(f"   检测结果: {status} (置信度: {result.confidence:.0%})")
        print(f"   预期: {'盗版' if case['expected'] else '正常'} {match}")

        if result.reasons:
            print(f"   判定依据:")
            for reason in result.reasons[:3]:  # 只显示前3条
                print(f"      • {reason}")


def test_prompt_optimization():
    """测试优化后的提示词"""
    print("\n" + "=" * 60)
    print("测试 4: 提示词优化检查")
    print("=" * 60)

    from config_anti_piracy import get_task_prompt

    prompts_to_check = [
        ("extract_info", "店铺名称"),
        ("extract_from_list", "店铺名称"),
    ]

    for prompt_key, keyword in prompts_to_check:
        prompt = get_task_prompt(prompt_key)
        has_keyword = keyword in prompt

        print(f"\n{prompt_key}:")
        print(f"   长度: {len(prompt)} 字符")
        print(f"   包含'{keyword}': {'✅' if has_keyword else '❌'}")

        # 显示提示词预览
        preview = prompt[:200].replace('\n', ' ')
        print(f"   预览: {preview}...")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("反盗版系统测试套件")
    print("=" * 60)

    try:
        # 测试 1: 举报模块
        test_reporter_module()

        # 测试 2: 举报流程
        test_report_flow()

        # 测试 3: 检测逻辑
        test_detection_logic()

        # 测试 4: 提示词优化
        test_prompt_optimization()

        print("\n" + "=" * 60)
        print("所有测试完成!")
        print("=" * 60)

        print("\n下一步:")
        print("1. 连接真实手机运行: python main_anti_piracy.py --test-mode")
        print("2. 观察店铺名称是否正确提取")
        print("3. 验证举报流程是否顺畅")

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
