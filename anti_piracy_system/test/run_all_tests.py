#!/usr/bin/env python3
"""
运行所有测试

使用方法:
    cd /Users/Apple/Documents/GUI/anti_piracy_system
    source venv/bin/activate
    python test/run_all_tests.py
"""

import sys
import os
import subprocess

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test(test_file: str, test_name: str) -> bool:
    """运行单个测试文件"""
    print(f"\n{'=' * 60}")
    print(f"运行: {test_name}")
    print("=" * 60)

    test_path = os.path.join(os.path.dirname(__file__), test_file)

    try:
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("反盗版系统 - 测试套件")
    print("=" * 60)
    print("\n当前案例: 众合法考")
    print("  - 官方店铺: 方圆众合教育")
    print("  - 商品: 2026众合法考客观题学习包")
    print("  - 价格: ¥898")

    tests = [
        ("test_prompts.py", "提示词配置测试"),
        ("test_detection.py", "盗版检测逻辑测试"),
        ("test_reporter.py", "举报模块测试"),
    ]

    results = []
    for test_file, test_name in tests:
        success = run_test(test_file, test_name)
        results.append((test_name, success))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    passed = 0
    failed = 0
    for test_name, success in results:
        mark = "✅" if success else "❌"
        print(f"   {mark} {test_name}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\n总计: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n所有测试通过! 可以进行真机测试:")
        print("   python main_anti_piracy.py --test-mode")
    else:
        print("\n有测试失败，请检查后再进行真机测试")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
