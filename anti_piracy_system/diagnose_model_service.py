#!/usr/bin/env /Users/Apple/Documents/GUI/anti_piracy_system/venv/bin/python3
"""
模型服务诊断工具

用于检查和诊断模型服务连接问题
"""

import sys
import requests
from urllib.parse import urlparse
import json


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def check_url_reachable(base_url):
    """检查URL是否可达"""
    print(f"🔍 检查URL可达性: {base_url}")

    try:
        parsed = urlparse(base_url)
        # 尝试连接基础URL
        response = requests.get(f"{parsed.scheme}://{parsed.netloc}", timeout=5)
        print(f"   ✅ 服务器可达 (状态码: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 连接失败: 无法连接到服务器")
        print(f"      可能原因:")
        print(f"      1. 服务未启动")
        print(f"      2. 地址错误")
        print(f"      3. 防火墙阻止")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ 连接超时")
        return False
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")
        return False


def test_model_endpoint(base_url, api_key="EMPTY", model_name="autoglm-phone-9b"):
    """测试模型API端点"""
    print(f"\n🔍 测试模型API端点")
    print(f"   URL: {base_url}")
    print(f"   模型: {model_name}")

    # 构建测试请求
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "测试连接"}
        ],
        "max_tokens": 10,
        "temperature": 0.7
    }

    try:
        print(f"\n   发送测试请求...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"   状态码: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✅ API正常工作!")
            try:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    print(f"   响应内容: {content[:50]}...")
            except:
                print(f"   响应: {response.text[:100]}...")
            return True
        elif response.status_code == 502:
            print(f"   ❌ 502 Bad Gateway 错误")
            print(f"      这通常表示:")
            print(f"      1. 后端模型服务未启动")
            print(f"      2. API网关配置错误")
            print(f"      3. 模型加载失败")
            return False
        elif response.status_code == 401:
            print(f"   ❌ 401 未授权")
            print(f"      API Key可能不正确")
            return False
        elif response.status_code == 404:
            print(f"   ❌ 404 未找到")
            print(f"      端点URL可能不正确")
            print(f"      期望: {url}")
            return False
        else:
            print(f"   ❌ 未预期的状态码: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"   ❌ 连接失败: 无法连接到API服务器")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ 请求超时 (30秒)")
        print(f"      模型服务可能负载过高或未响应")
        return False
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


def check_openai_module():
    """检查openai模块"""
    print(f"🔍 检查依赖模块")

    try:
        import openai
        print(f"   ✅ openai 模块已安装 (版本: {openai.__version__})")
        return True
    except ImportError:
        print(f"   ❌ openai 模块未安装")
        print(f"      请运行: pip install openai")
        return False


def provide_solutions(base_url):
    """提供解决方案"""
    print_header("解决方案")

    print("根据诊断结果,以下是可能的解决方案:\n")

    print("方案 1: 使用本地模型服务")
    print("─" * 60)
    print("1. 安装vLLM或SGLang:")
    print("   pip install vllm")
    print("")
    print("2. 下载AutoGLM-Phone-9B模型:")
    print("   从 ModelScope 或 HuggingFace 下载")
    print("")
    print("3. 启动模型服务:")
    print("   vllm serve THUDM/AutoGLM-Phone-9B \\")
    print("     --host 0.0.0.0 \\")
    print("     --port 8000 \\")
    print("     --trust-remote-code")
    print("")
    print("4. 验证服务:")
    print("   运行本诊断脚本再次测试")
    print("")

    print("\n方案 2: 使用智谱AI API (推荐快速测试)")
    print("─" * 60)
    print("1. 注册账号获取API Key:")
    print("   访问: https://open.bigmodel.cn/")
    print("")
    print("2. 修改配置:")
    print("   export PHONE_AGENT_BASE_URL='https://open.bigmodel.cn/api/paas/v4'")
    print("   export PHONE_AGENT_API_KEY='你的API密钥'")
    print("   export PHONE_AGENT_MODEL='glm-4-plus'")
    print("")
    print("3. 运行系统:")
    print("   python main_anti_piracy.py --show-stats")
    print("")

    print("\n方案 3: 使用ModelScope API")
    print("─" * 60)
    print("1. 获取API Key:")
    print("   访问: https://www.modelscope.cn/")
    print("")
    print("2. 配置环境变量:")
    print("   export PHONE_AGENT_BASE_URL='https://api-inference.modelscope.cn/v1'")
    print("   export PHONE_AGENT_API_KEY='你的API密钥'")
    print("")

    print("\n方案 4: 仅测试检测逻辑(不需要模型)")
    print("─" * 60)
    print("如果只想测试盗版检测逻辑,可以运行:")
    print("   python demo_detection.py")
    print("")
    print("这将展示三层检测机制的工作原理,无需模型服务")
    print("")


def main():
    """主函数"""
    import os

    print_header("模型服务诊断工具")

    # 获取配置
    base_url = os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1")
    api_key = os.getenv("PHONE_AGENT_API_KEY", "EMPTY")
    model_name = os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b")

    print(f"当前配置:")
    print(f"   BASE_URL: {base_url}")
    print(f"   API_KEY: {'*' * 8 if api_key != 'EMPTY' else 'EMPTY'}")
    print(f"   MODEL: {model_name}")

    # 1. 检查依赖
    print_header("步骤 1: 检查依赖模块")
    openai_ok = check_openai_module()

    if not openai_ok:
        print("\n❌ 请先安装必要的依赖:")
        print("   source venv/bin/activate")
        print("   pip install openai")
        return 1

    # 2. 检查URL可达性
    print_header("步骤 2: 检查服务器连接")
    url_ok = check_url_reachable(base_url)

    # 3. 测试API端点
    print_header("步骤 3: 测试模型API")
    api_ok = test_model_endpoint(base_url, api_key, model_name)

    # 4. 总结
    print_header("诊断总结")

    if openai_ok and url_ok and api_ok:
        print("✅ 所有检查通过! 模型服务正常工作")
        print("\n可以开始使用反盗版系统:")
        print("   python main_anti_piracy.py --show-stats")
        return 0
    else:
        print("❌ 发现问题:")
        if not openai_ok:
            print("   • OpenAI模块未安装")
        if not url_ok:
            print("   • 无法连接到服务器")
        if not api_ok:
            print("   • API端点测试失败")

        # 提供解决方案
        provide_solutions(base_url)

        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  诊断中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 诊断出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
