"""
举报流程模块

将举报逻辑从 AntiPiracyAgent 中解耦出来，支持：
1. 小红书平台的完整举报流程
2. 证据截图收集
3. 举报理由生成
"""

import os
import time
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class ReportContext:
    """举报上下文 - 包含执行举报所需的所有信息"""

    product_title: str          # 商品标题
    shop_name: str              # 店铺名称
    price: float                # 商品价格
    platform: str               # 平台名称
    detection_reasons: List[str]  # 检测判定依据
    confidence: float           # 置信度
    matched_product_name: Optional[str] = None  # 匹配到的正版商品名
    original_price: Optional[float] = None      # 正版原价
    screenshot_path: Optional[str] = None       # 证据截图路径
    report_id: Optional[str] = None            # 举报记录ID


class PlatformReporter(ABC):
    """
    平台举报器基类

    定义了举报流程的标准接口，不同平台需要实现各自的举报逻辑
    """

    def __init__(self, agent, report_manager, screenshot_dir: str = "screenshots"):
        """
        初始化举报器

        Args:
            agent: PhoneAgent 实例，用于执行自动化操作
            report_manager: ReportManager 实例，用于管理举报记录
            screenshot_dir: 截图保存目录
        """
        self.agent = agent
        self.report_manager = report_manager
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)

    @abstractmethod
    def execute_report(self, context: ReportContext) -> bool:
        """
        执行举报流程

        Args:
            context: 举报上下文

        Returns:
            是否举报成功
        """
        pass

    def save_evidence_screenshot(self, context: ReportContext) -> Optional[str]:
        """
        保存证据截图

        Args:
            context: 举报上下文

        Returns:
            截图文件路径，失败返回 None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_id = context.report_id or "unknown"
            filename = f"evidence_{report_id}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)

            # TODO: 调用 agent 的截图功能
            # self.agent.screenshot(filepath)

            print(f"   截图保存: {filepath}")
            return filepath

        except Exception as e:
            print(f"   截图保存失败: {e}")
            return None

    def generate_report_reason(self, context: ReportContext) -> str:
        """
        生成举报理由文本

        Args:
            context: 举报上下文

        Returns:
            格式化的举报理由
        """
        lines = []

        # 基本信息
        lines.append(f"【疑似盗版商品举报】")
        lines.append(f"商品：{context.product_title}")
        lines.append(f"店铺：{context.shop_name}")
        lines.append(f"价格：¥{context.price}")

        # 如果匹配到正版商品
        if context.matched_product_name:
            lines.append(f"")
            lines.append(f"【正版信息】")
            lines.append(f"正版商品：{context.matched_product_name}")
            if context.original_price:
                lines.append(f"正版价格：¥{context.original_price}")

        # 判定依据
        lines.append(f"")
        lines.append(f"【判定依据】置信度：{context.confidence:.0%}")
        for reason in context.detection_reasons:
            # 移除 emoji 以适应举报输入框
            clean_reason = reason.replace("✅", "[通过]").replace("❌", "[异常]").replace("⚠️", "[警告]")
            lines.append(f"• {clean_reason}")

        return "\n".join(lines)


class XiaohongshuReporter(PlatformReporter):
    """
    小红书平台举报器

    实现小红书 App 的完整举报流程：
    1. 点击右上角"..."菜单
    2. 下滑找到"举报"按钮
    3. 选择举报原因
    4. 填写举报说明并上传证据
    5. 提交举报
    """

    # 各步骤的提示词
    PROMPTS = {
        # Step 1: 打开更多菜单
        "open_menu": """
当前在小红书商品详情页，请执行以下操作：
1. 观察页面右上角
2. 找到"..."（三个点/更多）按钮
3. 点击该按钮打开菜单

注意：按钮通常在页面最顶部的右上角位置。
""",

        # Step 2: 查找举报按钮
        "find_report_button": """
当前显示了菜单弹窗/底部菜单，请执行以下操作：
1. 观察弹出的菜单内容
2. 如果看不到"举报"选项，向下滑动菜单
3. 找到"举报"按钮（可能显示为"举报"、"投诉"、"举报该商品"等）
4. 点击"举报"按钮

注意：举报按钮通常在菜单的下方，可能需要滑动才能看到。
""",

        # Step 3: 选择举报类型
        "select_report_type": """
当前在举报类型选择页面，请执行以下操作：
1. 浏览可选的举报类型列表
2. 查找以下任一选项并点击：
   - "侵权举报"
   - "知识产权侵权"
   - "盗版侵权"
   - "版权问题"
   - 如果没有上述选项，选择"其他"或"其他问题"
3. 点击选中的选项进入下一步
""",

        # Step 4: 填写举报内容
        "fill_report_content": """
当前在举报详情填写页面，请执行以下操作：
1. 找到文字输入框/举报说明框
2. 点击输入框
3. 输入以下举报内容：
{report_reason}
4. 确保内容输入完整
""",

        # Step 5: 上传证据图片
        "upload_evidence": """
当前需要上传证据图片，请执行以下操作：
1. 找到"添加图片"、"上传图片"或"+"按钮
2. 点击该按钮
3. 如果弹出权限请求，点击"允许"
4. 在相册中找到最近的截图（证据图片）
5. 选择该图片
6. 确认上传

注意：如果没有上传图片的选项，可以跳过此步骤。
""",

        # Step 6: 提交举报
        "submit_report": """
请完成举报提交：
1. 检查举报信息是否完整
2. 找到"提交"、"确认"或"提交举报"按钮
3. 点击该按钮提交举报
4. 等待提交成功的提示

注意：提交成功后通常会显示"举报成功"或返回之前的页面。
""",

        # 关闭菜单/返回
        "close_and_return": """
举报已完成，请执行以下操作：
1. 如果有弹窗，点击"确定"或"知道了"关闭
2. 返回商品列表页面继续检查下一个商品
"""
    }

    def execute_report(self, context: ReportContext) -> bool:
        """
        执行小红书举报流程

        Args:
            context: 举报上下文

        Returns:
            是否举报成功
        """
        print(f"\n{'='*50}")
        print(f"开始执行小红书举报流程")
        print(f"{'='*50}")
        print(f"   商品: {context.product_title}")
        print(f"   店铺: {context.shop_name}")
        print(f"   价格: ¥{context.price}")

        try:
            # Step 0: 保存当前页面截图作为证据
            print("\n[Step 0] 保存证据截图...")
            screenshot_path = self.save_evidence_screenshot(context)
            context.screenshot_path = screenshot_path

            # Step 1: 打开更多菜单
            print("\n[Step 1] 打开更多菜单...")
            if not self._execute_step("open_menu"):
                print("   无法打开菜单，举报终止")
                return False
            time.sleep(1.5)

            # Step 2: 查找并点击举报按钮
            print("\n[Step 2] 查找举报按钮...")
            if not self._execute_step("find_report_button"):
                print("   无法找到举报按钮，举报终止")
                return False
            time.sleep(1.5)

            # Step 3: 选择举报类型
            print("\n[Step 3] 选择举报类型...")
            if not self._execute_step("select_report_type"):
                print("   无法选择举报类型，举报终止")
                return False
            time.sleep(1.5)

            # Step 4: 填写举报内容
            print("\n[Step 4] 填写举报说明...")
            report_reason = self.generate_report_reason(context)
            prompt = self.PROMPTS["fill_report_content"].format(
                report_reason=report_reason
            )
            if not self._execute_step_with_prompt(prompt):
                print("   填写举报内容失败")
                # 继续尝试提交
            time.sleep(1.5)

            # Step 5: 上传证据（可选）
            if screenshot_path:
                print("\n[Step 5] 上传证据图片...")
                # 尝试上传，失败不影响整体流程
                self._execute_step("upload_evidence")
                time.sleep(2)

            # Step 6: 提交举报
            print("\n[Step 6] 提交举报...")
            if not self._execute_step("submit_report"):
                print("   提交举报失败")
                return False
            time.sleep(2)

            # 完成
            print("\n[完成] 关闭并返回...")
            self._execute_step("close_and_return")

            print(f"\n{'='*50}")
            print(f"举报流程完成")
            print(f"{'='*50}")
            return True

        except Exception as e:
            print(f"\n举报流程出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _execute_step(self, step_name: str) -> bool:
        """
        执行单个步骤

        Args:
            step_name: 步骤名称（对应 PROMPTS 中的 key）

        Returns:
            是否执行成功
        """
        prompt = self.PROMPTS.get(step_name)
        if not prompt:
            print(f"   未知步骤: {step_name}")
            return False

        return self._execute_step_with_prompt(prompt)

    def _execute_step_with_prompt(self, prompt: str) -> bool:
        """
        使用指定提示词执行步骤

        Args:
            prompt: 提示词

        Returns:
            是否执行成功
        """
        try:
            self.agent.run(prompt)
            return True
        except Exception as e:
            print(f"   步骤执行失败: {e}")
            return False


class XianyuReporter(PlatformReporter):
    """
    闲鱼平台举报器（预留）

    TODO: 实现闲鱼平台的举报流程
    """

    def execute_report(self, context: ReportContext) -> bool:
        print("闲鱼举报功能待实现")
        return False


class TaobaoReporter(PlatformReporter):
    """
    淘宝平台举报器（预留）

    TODO: 实现淘宝平台的举报流程
    """

    def execute_report(self, context: ReportContext) -> bool:
        print("淘宝举报功能待实现")
        return False


# 举报器工厂
def create_reporter(
    platform: str,
    agent,
    report_manager,
    screenshot_dir: str = "screenshots"
) -> PlatformReporter:
    """
    创建平台对应的举报器

    Args:
        platform: 平台标识（xiaohongshu/xianyu/taobao）
        agent: PhoneAgent 实例
        report_manager: ReportManager 实例
        screenshot_dir: 截图保存目录

    Returns:
        对应平台的举报器实例

    Raises:
        ValueError: 不支持的平台
    """
    reporters = {
        "xiaohongshu": XiaohongshuReporter,
        "xianyu": XianyuReporter,
        "taobao": TaobaoReporter,
    }

    reporter_class = reporters.get(platform)
    if reporter_class:
        return reporter_class(agent, report_manager, screenshot_dir)

    raise ValueError(f"不支持的平台: {platform}，支持的平台: {list(reporters.keys())}")


# 测试代码
if __name__ == "__main__":
    # 测试举报理由生成
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
        original_price=199.0
    )

    # 创建一个简单的 mock agent 用于测试
    class MockAgent:
        def run(self, prompt):
            print(f"[MockAgent] 执行: {prompt[:50]}...")

    class MockReportManager:
        pass

    reporter = XiaohongshuReporter(MockAgent(), MockReportManager())

    print("=== 测试举报理由生成 ===")
    reason = reporter.generate_report_reason(context)
    print(reason)

    print("\n=== 测试举报流程（Mock） ===")
    # reporter.execute_report(context)  # 取消注释以测试完整流程
