#!/usr/bin/env python3
"""
提示词配置测试

验证提示词是否包含必要的关键信息。

使用方法:
    cd /Users/Apple/Documents/GUI/anti_piracy_system
    source venv/bin/activate
    python test/test_prompts.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_anti_piracy import get_task_prompt, SUPPORTED_PLATFORMS


def test_prompts():
    """测试提示词配置"""
    print("\n" + "=" * 60)
    print("提示词配置测试")
    print("=" * 60)

    passed = 0
    failed = 0

    # 测试提示词关键内容
    prompt_checks = [
        {
            "key": "extract_info",
            "required_keywords": ["店铺名称", "shop_name", "JSON"],
            "description": "商品详情页信息提取"
        },
        {
            "key": "extract_from_list",
            "required_keywords": ["店铺名称", "shop_name", "JSON"],
            "description": "列表页信息提取"
        },
        {
            "key": "extract_shop_name_only",
            "required_keywords": ["店铺名称", "卖家"],
            "description": "店铺名称备用提取"
        },
        {
            "key": "launch_and_search",
            "required_keywords": ["启动", "搜索"],
            "description": "启动应用并搜索",
            "kwargs": {"platform": "小红书", "keyword": "众合法考"}
        }
    ]

    for check in prompt_checks:
        kwargs = check.get("kwargs", {})
        prompt = get_task_prompt(check["key"], **kwargs)
        print(f"\n--- {check['description']} ({check['key']}) ---")
        print(f"   长度: {len(prompt)} 字符")

        all_found = True
        for keyword in check["required_keywords"]:
            found = keyword in prompt
            mark = "✅" if found else "❌"
            print(f"   包含 '{keyword}': {mark}")
            if not found:
                all_found = False

        if all_found:
            passed += 1
        else:
            failed += 1

    # 测试平台配置
    print("\n--- 平台搜索关键词配置 ---")
    for platform_key, config in SUPPORTED_PLATFORMS.items():
        keywords = config.get("search_keywords", [])
        has_zhonghe = any("众合" in kw for kw in keywords)
        mark = "✅" if has_zhonghe else "❌"
        print(f"   {config['name']}: {keywords} {mark}")
        if has_zhonghe:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = test_prompts()
    sys.exit(0 if success else 1)
