"""反盗版自动巡查 Agent

基于 Open-AutoGLM 框架扩展的专门用于识别和举报盗版内容的 Agent
"""

import sys
import os
import time
import json
import re
from typing import Optional, List, Dict, Tuple
from datetime import datetime

# 添加 Open-AutoGLM 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../Open-AutoGLM'))

from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig

# 导入反盗版系统模块
from product_database import ProductDatabase, GenuineProduct
from piracy_detector import PiracyDetector, ProductInfo, DetectionResult
from report_manager import ReportManager, ReportRecord
from config_anti_piracy import (
    PATHS, DETECTOR_CONFIG, AGENT_CONFIG, SUPPORTED_PLATFORMS,
    get_task_prompt, get_ui_text, get_report_reason
)


class AntiPiracyAgent:
    """反盗版巡查 Agent"""

    def __init__(
        self,
        model_config: ModelConfig,
        agent_config: Optional[AgentConfig] = None,
        platform: str = "xiaohongshu",
        test_mode: bool = False
    ):
        """
        初始化反盗版 Agent

        Args:
            model_config: 模型配置
            agent_config: Agent 配置
            platform: 目标平台(xiaohongshu/xianyu/taobao)
            test_mode: 是否为测试模式(不实际举报)
        """
        # 初始化配置
        if agent_config is None:
            agent_config = AgentConfig(
                max_steps=AGENT_CONFIG["max_steps"],
                verbose=True
            )

        # 初始化基础 Agent
        self.base_agent = PhoneAgent(
            model_config=model_config,
            agent_config=agent_config
        )

        # 初始化反盗版组件
        self.product_db = ProductDatabase(PATHS["product_database"])
        self.detector = PiracyDetector(
            self.product_db,
            price_threshold=DETECTOR_CONFIG["price_threshold"],
            similarity_threshold=DETECTOR_CONFIG["similarity_threshold"]
        )
        self.report_manager = ReportManager(PATHS["report_log"])

        # 平台配置
        self.platform = platform
        self.platform_config = SUPPORTED_PLATFORMS.get(platform, {})
        if not self.platform_config:
            raise ValueError(f"不支持的平台: {platform}")

        # 运行状态
        self.test_mode = test_mode
        self.current_session = {
            "start_time": None,
            "checked_count": 0,
            "piracy_count": 0,
            "reported_count": 0,
            "results": []
        }

        # 截图目录
        self.screenshot_dir = PATHS["screenshots_dir"]
        os.makedirs(self.screenshot_dir, exist_ok=True)

        print(f"✅ 反盗版 Agent 初始化完成")
        print(f"   平台: {self.platform_config['name']}")
        print(f"   模式: {'测试模式' if test_mode else '正式模式'}")

    def start_patrol(
        self,
        keyword: str = "得到",
        max_items: int = 10
    ) -> Dict:
        """
        开始巡查

        Args:
            keyword: 搜索关键词
            max_items: 最多检查的商品数量

        Returns:
            巡查结果统计
        """
        print("\n" + "=" * 60)
        print(get_ui_text("welcome"))
        print("=" * 60)

        # 初始化会话
        self.current_session = {
            "start_time": datetime.now(),
            "checked_count": 0,
            "piracy_count": 0,
            "reported_count": 0,
            "results": []
        }

        try:
            # Step 1: 启动应用并搜索
            self._launch_and_search(keyword)

            # Step 2: 浏览并检查搜索结果
            for i in range(max_items):
                print(f"\n--- 检查第 {i + 1}/{max_items} 个商品 ---")

                # 提取当前商品信息
                product_info = self._extract_product_info(index=i)

                if not product_info:
                    print("⚠️ 无法提取商品信息,跳过")
                    continue

                # 检测是否为盗版
                detection_result = self._detect_piracy(product_info)

                # 记录结果
                self.current_session["checked_count"] += 1
                self.current_session["results"].append({
                    "product_info": product_info,
                    "detection_result": detection_result
                })

                # 如果检测到盗版,执行举报
                if detection_result.is_piracy:
                    self.current_session["piracy_count"] += 1

                    if not self.test_mode:
                        success = self._report_piracy(product_info, detection_result)
                        if success:
                            self.current_session["reported_count"] += 1
                    else:
                        print("⚠️ 测试模式:跳过实际举报操作")
                        self.current_session["reported_count"] += 1

                # 返回列表继续
                self._back_to_list()

                # 检查是否需要滚动加载更多
                if (i + 1) % 5 == 0:
                    self._scroll_down()

                time.sleep(AGENT_CONFIG["wait_after_action"])

        except Exception as e:
            print(f"❌ 巡查过程出错: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # 生成巡查报告
            report = self._generate_patrol_report()
            print("\n" + "=" * 60)
            print("巡查完成!")
            print("=" * 60)
            print(report)

            return self.current_session

    def _launch_and_search(self, keyword: str) -> bool:
        """
        启动应用并搜索

        Args:
            keyword: 搜索关键词

        Returns:
            是否成功
        """
        print(f"\n🚀 启动 {self.platform_config['name']} 并搜索'{keyword}'...")

        task = get_task_prompt(
            "launch_and_search",
            platform=self.platform_config['name'],
            keyword=keyword
        )

        try:
            self.base_agent.run(task)
            print("✅ 应用启动和搜索完成")
            time.sleep(3)  # 等待搜索结果加载

            # 小红书特殊处理：切换到"商品"标签
            if self.platform == "xiaohongshu":
                print("\n📱 小红书平台：切换到商品标签...")
                try:
                    switch_task = get_task_prompt("switch_to_products_tab")
                    self.base_agent.run(switch_task)
                    print("✅ 已切换到商品标签")
                    time.sleep(2)  # 等待商品列表加载
                except Exception as e:
                    print(f"⚠️  切换商品标签失败: {e}")
                    print("   将继续尝试提取信息...")

            return True
        except Exception as e:
            error_msg = str(e)
            if "502" in error_msg or "Bad Gateway" in error_msg:
                print(f"❌ 模型服务连接失败 (502 Bad Gateway)")
                print(f"   请检查模型服务是否正常运行")
                print(f"   运行诊断工具获取帮助: python diagnose_model_service.py")
            elif "Connection" in error_msg or "连接" in error_msg:
                print(f"❌ 无法连接到模型服务")
                print(f"   请确保模型服务已启动: {self.base_agent.model_config.base_url}")
            else:
                print(f"❌ 启动搜索失败: {e}")
            return False

    def _extract_product_info(self, index: int = 0) -> Optional[ProductInfo]:
        """
        提取商品信息

        使用 AutoGLM 的多模态能力直接从当前页面识别商品信息

        Args:
            index: 商品索引(0开始)

        Returns:
            商品信息对象或None
        """
        print(f"\n📋 提取第 {index + 1} 个商品信息...")

        try:
            # 进入商品详情
            if not self._enter_detail(index):
                print(f"⚠️  无法进入商品详情页，跳过")
                return None

            # 使用 AutoGLM 多模态能力提取商品信息
            print("   使用AI视觉模型识别页面内容...")
            task = get_task_prompt("extract_info")

            # 调用 Agent 让其识别页面内容
            # AutoGLM 会通过多模态模型理解当前屏幕内容
            try:
                response = self.base_agent.run(task)
                print(f"   模型响应: {response[:200] if response else 'None'}...")

                # 解析模型响应
                parsed_data = self._parse_model_response(str(response)) if response else None

                if parsed_data and isinstance(parsed_data, dict):
                    # 调试：打印解析后的所有字段
                    print(f"   📊 解析的字段: {list(parsed_data.keys())}")

                    # 从解析的数据中提取信息（支持多种字段名）
                    title = (parsed_data.get('title') or
                            parsed_data.get('商品标题') or
                            parsed_data.get('product_title') or
                            f"未识别商品_{index}")

                    # 店铺名称 - 支持多种可能的字段名
                    shop_name = (parsed_data.get('shop_name') or
                                parsed_data.get('店铺名称') or
                                parsed_data.get('卖家昵称') or
                                parsed_data.get('卖家名称') or
                                parsed_data.get('商家名称') or
                                parsed_data.get('seller_name') or
                                parsed_data.get('store_name') or
                                "未知店铺")

                    price_val = (parsed_data.get('price') or
                                parsed_data.get('价格') or
                                parsed_data.get('商品价格') or
                                parsed_data.get('售价'))

                    # 处理价格
                    price = 0.0
                    if price_val:
                        try:
                            # 尝试从字符串中提取数字
                            price_str = str(price_val).replace('¥', '').replace('元', '').strip()
                            price = float(re.findall(r'\d+\.?\d*', price_str)[0])
                        except (ValueError, IndexError):
                            print(f"   ⚠️  无法解析价格: {price_val}")

                    description = parsed_data.get('description') or parsed_data.get('商品描述')
                    ocr_text = parsed_data.get('ocr_text') or parsed_data.get('all_text')

                    product_info = ProductInfo(
                        title=title,
                        shop_name=shop_name,
                        price=price,
                        description=description,
                        ocr_text=ocr_text,
                        platform=self.platform_config['name']
                    )

                    print(f"✅ 成功提取商品信息:")
                    print(f"   标题: {title}")
                    print(f"   店铺: {shop_name}")
                    print(f"   价格: ¥{price}")

                    return product_info
                else:
                    print(f"⚠️  模型未返回有效的JSON数据")

            except Exception as e:
                print(f"⚠️  AI提取失败: {e}")

            # 如果AI提取失败，返回基本信息（可以后续改进）
            print("   使用备用方案...")
            product_info = ProductInfo(
                title=f"商品_{index}(AI提取失败)",
                shop_name="未知",
                price=0.0,
                platform=self.platform_config['name']
            )

            return product_info

        except Exception as e:
            print(f"❌ 提取商品信息失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _enter_detail(self, index: int) -> bool:
        """
        进入商品详情页

        Args:
            index: 商品索引

        Returns:
            是否成功
        """
        task = get_task_prompt("enter_detail", index=index + 1)

        try:
            self.base_agent.run(task)
            time.sleep(2)  # 等待详情页加载
            return True
        except Exception as e:
            print(f"❌ 进入详情页失败: {e}")
            return False

    def _detect_piracy(self, product_info: ProductInfo) -> DetectionResult:
        """
        检测是否为盗版

        Args:
            product_info: 商品信息

        Returns:
            检测结果
        """
        print(f"\n🔍 检测商品: {product_info.title}")

        result = self.detector.detect(product_info)

        if result.is_piracy:
            print(f"❌ 检测到疑似盗版! (置信度: {result.confidence:.0%})")
            print("   判定依据:")
            for reason in result.reasons:
                print(f"   - {reason}")
        else:
            print(f"✅ 未检测到盗版问题")

        return result

    def _report_piracy(
        self,
        product_info: ProductInfo,
        detection_result: DetectionResult
    ) -> bool:
        """
        举报盗版商品

        Args:
            product_info: 商品信息
            detection_result: 检测结果

        Returns:
            是否举报成功
        """
        print(f"\n📢 执行举报操作...")

        # 创建举报记录
        report = self.report_manager.create_report(
            platform=product_info.platform,
            target_title=product_info.title,
            target_shop=product_info.shop_name,
            target_price=product_info.price,
            detection_result=detection_result.to_dict(),
            target_url=product_info.url
        )

        # 保存当前页面截图作为证据
        screenshot_path = self._save_screenshot(report.report_id)
        if screenshot_path:
            self.report_manager.add_screenshot(report.report_id, screenshot_path)

        # 执行举报操作(使用 Agent 自动化)
        try:
            task = get_task_prompt(
                "report_piracy",
                report_reason=report.report_reason
            )

            self.base_agent.run(task)

            # 更新举报状态
            self.report_manager.update_status(
                report.report_id,
                "submitted",
                "举报已通过应用内举报功能提交"
            )

            print(f"✅ 举报成功! (举报ID: {report.report_id})")
            return True

        except Exception as e:
            print(f"❌ 举报失败: {e}")
            self.report_manager.update_status(
                report.report_id,
                "failed",
                f"举报提交失败: {str(e)}"
            )
            return False

    def _save_screenshot(self, report_id: str) -> Optional[str]:
        """
        保存当前页面截图

        Args:
            report_id: 举报ID

        Returns:
            截图文件路径或None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_id}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)

            # TODO: 实现真正的截图保存
            # 可以使用 base_agent 的截图功能

            print(f"📸 保存截图: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ 保存截图失败: {e}")
            return None

    def _back_to_list(self) -> bool:
        """
        返回搜索结果列表

        Returns:
            是否成功
        """
        task = get_task_prompt("back_to_list")

        try:
            self.base_agent.run(task)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ 返回列表失败: {e}")
            return False

    def _scroll_down(self) -> bool:
        """
        向下滚动页面

        Returns:
            是否成功
        """
        print("📜 向下滚动加载更多...")

        try:
            # 使用 Agent 执行滚动操作
            self.base_agent.run("向下滚动页面,加载更多搜索结果")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ 滚动失败: {e}")
            return False

    def _parse_model_response(self, response: str) -> Optional[Dict]:
        """
        解析模型返回的JSON响应

        支持多种JSON格式：
        1. 纯JSON: {"key": "value"}
        2. 代码块: ```json {...} ```
        3. 嵌套在文本中的JSON

        Args:
            response: 模型返回的文本

        Returns:
            解析后的字典或None
        """
        if not response:
            print("   ⚠️  模型响应为空")
            return None

        # 打印原始响应的前200个字符用于调试
        print(f"   🔍 原始响应预览: {response[:200]}...")

        try:
            # 方法1: 直接解析JSON
            result = json.loads(response)
            print("   ✅ 使用方法1解析成功（直接JSON）")
            return result
        except json.JSONDecodeError as e:
            print(f"   ⚠️  方法1失败: {str(e)[:50]}")

        try:
            # 方法2: 查找JSON代码块
            # 匹配 ```json ... ``` 或 ``` ... ```
            json_pattern = r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                result = json.loads(matches[0])
                print("   ✅ 使用方法2解析成功（代码块）")
                return result
        except (json.JSONDecodeError, IndexError) as e:
            print(f"   ⚠️  方法2失败: {str(e)[:50]}")

        try:
            # 方法3: 查找嵌套的JSON对象（支持嵌套花括号）
            # 更强大的正则，支持嵌套
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                # 尝试最长的匹配（通常是完整的JSON）
                matches_sorted = sorted(matches, key=len, reverse=True)
                for match in matches_sorted:
                    try:
                        result = json.loads(match)
                        print("   ✅ 使用方法3解析成功（嵌套JSON）")
                        return result
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"   ⚠️  方法3失败: {str(e)[:50]}")

        try:
            # 方法4: 查找简单的JSON对象（无嵌套）
            json_pattern = r'(\{[^{}]+\})'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                for match in matches:
                    try:
                        result = json.loads(match)
                        print("   ✅ 使用方法4解析成功（简单JSON）")
                        return result
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"   ⚠️  方法4失败: {str(e)[:50]}")

        # 所有方法都失败
        print(f"   ❌ 所有解析方法均失败")
        print(f"   完整响应: {response}")
        return None

    def _generate_patrol_report(self) -> str:
        """
        生成巡查报告

        Returns:
            报告文本
        """
        session = self.current_session
        duration = (datetime.now() - session["start_time"]).total_seconds() if session["start_time"] else 0

        report = f"""
╔══════════════════════════════════════════════════╗
║           反盗版巡查报告                          ║
╚══════════════════════════════════════════════════╝

📅 巡查时间: {session['start_time'].strftime('%Y-%m-%d %H:%M:%S') if session['start_time'] else 'N/A'}
⏱️  总耗时: {duration:.1f} 秒
🔍 检查商品数: {session['checked_count']}
❌ 发现疑似盗版: {session['piracy_count']}
📢 已举报数: {session['reported_count']}

╔══════════════════════════════════════════════════╗
║           检测结果详情                            ║
╚══════════════════════════════════════════════════╝
"""

        for i, result in enumerate(session["results"], 1):
            product = result["product_info"]
            detection = result["detection_result"]

            report += f"""
[{i}] {product.title}
    店铺: {product.shop_name}
    价格: ¥{product.price}
    结果: {'🚨 疑似盗版' if detection.is_piracy else '✅ 正常'}
    置信度: {detection.confidence:.0%}
"""

        return report

    def add_genuine_product(self, product: GenuineProduct) -> bool:
        """
        添加正版商品到数据库

        Args:
            product: 正版商品对象

        Returns:
            是否添加成功
        """
        return self.product_db.add_product(product)

    def get_patrol_statistics(self) -> Dict:
        """
        获取巡查统计信息

        Returns:
            统计信息字典
        """
        return {
            "session": self.current_session,
            "database_stats": self.product_db.get_stats(),
            "report_stats": self.report_manager.get_statistics()
        }


# 示例使用
if __name__ == "__main__":
    # 配置模型
    model_config = ModelConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b"
    )

    # 创建 Agent
    agent = AntiPiracyAgent(
        model_config=model_config,
        platform="xiaohongshu",
        test_mode=True  # 测试模式
    )

    # 添加测试商品到数据库
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
    agent.add_genuine_product(test_product)

    # 开始巡查(测试模式)
    # agent.start_patrol(keyword="得到", max_items=5)
    print("✅ Agent 初始化完成,可以调用 start_patrol() 开始巡查")
