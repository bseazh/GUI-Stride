#!/usr/bin/env python3
"""
真机测试脚本 - 通过ADB连接真实手机

测试内容:
1. ADB设备连接检测
2. 屏幕截图功能
3. AI模型信息提取（店铺名称等）
4. 完整的巡查流程（测试模式）

使用方法:
    cd /Users/Apple/Documents/GUI/anti_piracy_system
    source venv/bin/activate

    # 测试设备连接
    python test/test_real_device.py --check-device

    # 测试截图功能
    python test/test_real_device.py --test-screenshot

    # 测试信息提取（需要手动打开小红书商品页）
    python test/test_real_device.py --test-extraction

    # 运行完整测试流程
    python test/test_real_device.py --full-test

前提条件:
    1. 手机通过USB连接并开启USB调试
    2. 或通过WiFi连接（adb connect <IP>:5555）
    3. 安装了ADB键盘（用于文本输入）
"""

import sys
import os
import argparse
import time
import subprocess
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../Open-AutoGLM'))

# 加载环境变量
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def check_adb_connection():
    """检查ADB设备连接状态"""
    print("\n" + "=" * 60)
    print("步骤 1: 检查ADB设备连接")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["adb", "devices", "-l"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(f"\nADB 输出:\n{result.stdout}")

        # 解析设备列表
        lines = result.stdout.strip().split("\n")[1:]  # 跳过标题行
        devices = []

        for line in lines:
            if line.strip() and "device" in line:
                parts = line.split()
                device_id = parts[0]
                status = parts[1] if len(parts) > 1 else "unknown"

                # 提取设备型号
                model = "unknown"
                for part in parts:
                    if part.startswith("model:"):
                        model = part.split(":")[1]
                        break

                devices.append({
                    "id": device_id,
                    "status": status,
                    "model": model
                })

        if devices:
            print(f"\n✅ 检测到 {len(devices)} 个设备:")
            for i, dev in enumerate(devices, 1):
                print(f"   [{i}] {dev['id']} ({dev['model']}) - {dev['status']}")
            return devices
        else:
            print("\n❌ 未检测到任何设备")
            print("\n请检查:")
            print("   1. 手机是否通过USB连接")
            print("   2. USB调试是否已开启")
            print("   3. 是否已授权此电脑调试")
            print("\n如果使用WiFi连接:")
            print("   adb connect <手机IP>:5555")
            return []

    except FileNotFoundError:
        print("\n❌ 未找到 adb 命令")
        print("   请确保 Android SDK Platform Tools 已安装并添加到 PATH")
        return []
    except Exception as e:
        print(f"\n❌ 检查设备时出错: {e}")
        return []


def test_screenshot(device_id=None):
    """测试截图功能"""
    print("\n" + "=" * 60)
    print("步骤 2: 测试截图功能")
    print("=" * 60)

    try:
        from phone_agent.adb import get_screenshot

        print("\n正在截取屏幕...")
        screenshot = get_screenshot(device_id=device_id)

        if screenshot and screenshot.base64_data:
            print(f"✅ 截图成功!")
            print(f"   尺寸: {screenshot.width} x {screenshot.height}")
            print(f"   数据大小: {len(screenshot.base64_data)} 字符")
            print(f"   敏感屏幕: {screenshot.is_sensitive}")

            # 保存截图到本地
            import base64
            screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(screenshot_dir, f"test_screenshot_{timestamp}.png")

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(screenshot.base64_data))

            print(f"   已保存到: {filepath}")
            return True
        else:
            print("❌ 截图失败或返回空数据")
            return False

    except Exception as e:
        print(f"❌ 截图测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extraction(device_id=None):
    """测试信息提取功能（需要手动打开小红书商品页）"""
    print("\n" + "=" * 60)
    print("步骤 3: 测试AI信息提取")
    print("=" * 60)

    print("\n⚠️  请先手动操作:")
    print("   1. 在手机上打开小红书App")
    print("   2. 搜索 '众合法考'")
    print("   3. 点击进入任意一个商品详情页")
    print("   4. 确保商品详情页已完全加载")

    input("\n按 Enter 键继续测试...")

    try:
        from phone_agent import PhoneAgent
        from phone_agent.agent import AgentConfig
        from phone_agent.model import ModelConfig
        from config_anti_piracy import get_task_prompt

        # 配置模型（使用环境变量）
        model_config = ModelConfig()
        print(f"\n模型配置:")
        print(f"   URL: {model_config.base_url}")
        print(f"   Model: {model_config.model_name}")

        # 配置Agent
        agent_config = AgentConfig(
            max_steps=10,
            device_id=device_id,
            verbose=True,
            lang="cn"
        )

        # 创建Agent
        print("\n正在初始化 PhoneAgent...")
        agent = PhoneAgent(
            model_config=model_config,
            agent_config=agent_config
        )

        # 获取提取提示词
        task = get_task_prompt("extract_info")
        print(f"\n提示词预览: {task[:100]}...")

        # 执行提取
        print("\n正在调用AI模型提取商品信息...")
        response = agent.run(task)

        print(f"\n模型响应:")
        print("-" * 40)
        print(response)
        print("-" * 40)

        # 尝试解析JSON
        import json
        import re

        # 尝试提取JSON
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, str(response), re.DOTALL)

        if matches:
            for match in matches:
                try:
                    data = json.loads(match)
                    print(f"\n✅ 成功解析JSON:")
                    print(f"   标题: {data.get('title', 'N/A')}")
                    print(f"   店铺: {data.get('shop_name', 'N/A')}")
                    print(f"   价格: {data.get('price', 'N/A')}")

                    # 检查店铺名称是否成功提取
                    shop_name = data.get('shop_name')
                    if shop_name and shop_name not in ["未知", "null", None, ""]:
                        print(f"\n✅ 店铺名称提取成功: {shop_name}")
                    else:
                        print(f"\n⚠️  店铺名称提取失败或为空")

                    return True
                except json.JSONDecodeError:
                    continue

        print("\n⚠️  未能从响应中解析出有效JSON")
        return False

    except Exception as e:
        print(f"\n❌ 信息提取测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_full_test(device_id=None):
    """运行完整测试流程"""
    print("\n" + "=" * 60)
    print("完整测试流程 - 众合法考盗版检测")
    print("=" * 60)

    print("\n当前案例配置:")
    print("   搜索关键词: 众合法考")
    print("   官方店铺: 方圆众合教育")
    print("   正版价格: ¥898")

    try:
        from anti_piracy_agent import AntiPiracyAgent
        from phone_agent.model import ModelConfig

        # 配置模型
        model_config = ModelConfig()

        # 创建反盗版Agent（测试模式）
        print("\n正在初始化反盗版Agent...")
        agent = AntiPiracyAgent(
            model_config=model_config,
            platform="xiaohongshu",
            test_mode=True  # 测试模式，不实际举报
        )

        # 开始巡查
        print("\n开始巡查测试...")
        result = agent.start_patrol(
            keyword="众合法考",
            max_items=2  # 测试只检查2个商品
        )

        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)
        print(f"   检查商品数: {result['checked_count']}")
        print(f"   发现盗版数: {result['piracy_count']}")
        print(f"   已举报数: {result['reported_count']}")

        return True

    except Exception as e:
        print(f"\n❌ 完整测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="反盗版系统真机测试")
    parser.add_argument("--check-device", action="store_true", help="检查设备连接")
    parser.add_argument("--test-screenshot", action="store_true", help="测试截图功能")
    parser.add_argument("--test-extraction", action="store_true", help="测试信息提取")
    parser.add_argument("--full-test", action="store_true", help="运行完整测试")
    parser.add_argument("--device", type=str, help="指定设备ID")

    args = parser.parse_args()

    # 如果没有指定任何测试，显示帮助
    if not any([args.check_device, args.test_screenshot, args.test_extraction, args.full_test]):
        parser.print_help()
        print("\n示例:")
        print("   python test/test_real_device.py --check-device")
        print("   python test/test_real_device.py --test-screenshot")
        print("   python test/test_real_device.py --test-extraction")
        print("   python test/test_real_device.py --full-test")
        return

    print("\n" + "=" * 60)
    print("反盗版系统 - 真机测试")
    print("=" * 60)

    device_id = args.device

    # 步骤1: 检查设备连接
    if args.check_device or args.test_screenshot or args.test_extraction or args.full_test:
        devices = check_adb_connection()

        if not devices:
            print("\n测试终止: 没有可用设备")
            return

        # 如果没有指定设备，使用第一个
        if not device_id:
            device_id = devices[0]["id"]
            print(f"\n使用设备: {device_id}")

    # 步骤2: 测试截图
    if args.test_screenshot:
        test_screenshot(device_id)

    # 步骤3: 测试信息提取
    if args.test_extraction:
        test_extraction(device_id)

    # 步骤4: 完整测试
    if args.full_test:
        run_full_test(device_id)

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
