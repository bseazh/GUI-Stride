"""反盗版系统配置文件

包含系统运行所需的各种配置参数和提示词
"""

from typing import Dict, List


# ==================== 基础配置 ====================

# 文件路径配置
PATHS = {
    "product_database": "data/genuine_products.json",
    "report_log": "logs/report_history.json",
    "screenshots_dir": "screenshots",
    "temp_dir": "temp"
}

# 检测器配置
DETECTOR_CONFIG = {
    "price_threshold": 0.7,  # 价格阈值,低于原价70%触发警告
    "similarity_threshold": 0.6,  # 内容相似度阈值
    "confidence_threshold": 0.7  # 判定为盗版的置信度阈值
}

# Agent 配置
AGENT_CONFIG = {
    "max_steps": 50,  # 每个任务最大步数
    "scroll_count": 5,  # 滚动浏览的最大次数
    "item_check_limit": 10,  # 每次运行检查的最大商品数
    "wait_after_action": 2.0,  # 操作后等待时间(秒)
    "screenshot_interval": 1.0  # 截图间隔(秒)
}

# 支持的平台配置
SUPPORTED_PLATFORMS = {
    "xiaohongshu": {
        "name": "小红书",
        "app_package": "com.xingin.xhs",
        "search_keywords": ["得到", "得到课程", "得到电子书"]
    },
    "xianyu": {
        "name": "闲鱼",
        "app_package": "com.taobao.idlefish",
        "search_keywords": ["得到", "得到课程", "得到电子书"]
    },
    "taobao": {
        "name": "淘宝",
        "app_package": "com.taobao.taobao",
        "search_keywords": ["得到课程", "得到电子书"]
    }
}


# ==================== 提示词配置 ====================

# 系统提示词 - 用于指导AI模型理解任务
SYSTEM_PROMPT = """你是一个专门用于识别和举报盗版电子内容的自动化助手。你的任务是:

1. 在指定的电商平台(如小红书、闲鱼)上搜索潜在的盗版内容
2. 分析商品信息,包括标题、店铺名称、价格、描述等
3. 根据正版商品信息数据库判断是否为盗版
4. 对确认的盗版内容进行举报

你需要特别关注以下几点:
- 店铺名称是否为官方授权店铺
- 价格是否远低于正版价格(低于70%)
- 商品描述和图片是否与正版内容匹配

在执行操作时请谨慎、准确,避免误判。
"""

# 任务提示词模板
TASK_PROMPTS = {
    # 启动应用并搜索
    "launch_and_search": """
请执行以下操作:
1. 启动{platform}应用
2. 等待应用加载完成
3. 点击搜索框
4. 输入搜索关键词: "{keyword}"
5. 点击搜索按钮
6. 等待搜索结果加载
""",

    # 小红书专用 - 切换到商品标签
    "switch_to_products_tab": """
当前在小红书搜索结果页面,请执行:
1. 查找页面顶部的标签栏
2. 点击"商品"标签(可能显示为"商品"、"goods"或购物车图标)
3. 等待商品列表加载完成
""",

    # 浏览搜索结果
    "browse_results": """
当前在搜索结果页面,请:
1. 浏览当前可见的商品/笔记
2. 识别商品标题、价格、店铺名称
3. 记录可疑商品的位置
""",

    # 从列表页批量提取商品信息
    "extract_from_list": """
当前在商品列表页面,请识别并提取当前屏幕上所有可见商品的信息。

对于每个商品,请提取:
1. 商品标题(完整标题)
2. 价格(数字,如果有)
3. 店铺名称或卖家昵称
4. 商品在列表中的位置(第几个)

请以JSON数组格式返回,每个商品一个对象:
[
  {{
    "index": 0,
    "title": "商品标题",
    "price": 99.9,
    "shop_name": "店铺名称"
  }},
  ...
]

如果某个字段无法识别,请用 null 表示。
""",

    # 进入商品详情
    "enter_detail": """
请点击第{index}个商品/笔记,进入详情页查看完整信息。
""",

    # 提取商品信息
    "extract_info": """
当前在商品详情页,请识别并提取以下信息:
1. 商品标题
2. 店铺名称(卖家名称)
3. 商品价格
4. 商品描述(尽可能详细)
5. 页面上的所有文字内容(OCR)

请以JSON格式返回这些信息。
""",

    # 执行举报
    "report_piracy": """
这是一个确认的盗版商品,请执行举报操作:
1. 查找页面上的举报按钮(通常在右上角或分享按钮附近)
2. 点击举报按钮
3. 选择举报原因: "盗版侵权"或"知识产权侵权"
4. 填写举报说明: {report_reason}
5. 提交举报
6. 等待提交完成
7. 截图保存举报成功页面
""",

    # 返回列表
    "back_to_list": """
请返回搜索结果列表,继续检查下一个商品。
"""
}


# 商品信息提取提示词
EXTRACTION_PROMPTS = {
    "title": "请识别并提取商品标题",
    "shop_name": "请识别并提取店铺名称或卖家名称",
    "price": "请识别并提取商品价格(数字)",
    "description": "请识别并提取商品描述信息",
    "all_text": "请使用OCR提取页面上所有可见的文字内容"
}


# 举报原因模板
REPORT_REASON_TEMPLATES = {
    "price_too_low": "该商品价格为¥{price},仅为官方正版价格¥{original_price}的{ratio:.0%},远低于市场价格,疑似盗版。",
    "unofficial_shop": "该商品由非官方授权店铺'{shop_name}'销售,而官方授权店铺为{official_shops},疑似盗版。",
    "content_match": "该商品内容与正版商品'{product_name}'高度相似,但来源不明,疑似未经授权的盗版内容。",
    "comprehensive": "综合判断(置信度{confidence:.0%}),该商品疑似盗版,理由如下:\n{detailed_reasons}"
}


# ==================== UI文本配置 ====================

UI_TEXTS = {
    "cn": {
        "welcome": "欢迎使用反盗版自动巡查系统",
        "loading_db": "正在加载商品数据库...",
        "start_patrol": "开始巡查",
        "checking_item": "正在检查商品: {title}",
        "piracy_detected": "检测到疑似盗版!",
        "reporting": "正在举报...",
        "report_success": "举报成功!",
        "report_failed": "举报失败: {reason}",
        "patrol_complete": "巡查完成,共检查{total}个商品,发现{piracy_count}个疑似盗版",
        "saving_results": "正在保存结果...",
        "done": "完成"
    },
    "en": {
        "welcome": "Welcome to Anti-Piracy Patrol System",
        "loading_db": "Loading product database...",
        "start_patrol": "Start Patrol",
        "checking_item": "Checking item: {title}",
        "piracy_detected": "Piracy detected!",
        "reporting": "Reporting...",
        "report_success": "Report submitted successfully!",
        "report_failed": "Report failed: {reason}",
        "patrol_complete": "Patrol complete. Checked {total} items, found {piracy_count} piracy suspects",
        "saving_results": "Saving results...",
        "done": "Done"
    }
}


# ==================== 辅助函数 ====================

def get_platform_config(platform_key: str) -> Dict:
    """
    获取平台配置

    Args:
        platform_key: 平台键名(xiaohongshu/xianyu/taobao)

    Returns:
        平台配置字典
    """
    return SUPPORTED_PLATFORMS.get(platform_key, {})


def get_task_prompt(task_key: str, **kwargs) -> str:
    """
    获取任务提示词

    Args:
        task_key: 任务键名
        **kwargs: 格式化参数

    Returns:
        格式化后的提示词
    """
    prompt_template = TASK_PROMPTS.get(task_key, "")
    return prompt_template.format(**kwargs)


def get_report_reason(reason_type: str, **kwargs) -> str:
    """
    获取举报理由

    Args:
        reason_type: 理由类型
        **kwargs: 格式化参数

    Returns:
        格式化后的举报理由
    """
    template = REPORT_REASON_TEMPLATES.get(reason_type, "")
    return template.format(**kwargs)


def get_ui_text(key: str, lang: str = "cn", **kwargs) -> str:
    """
    获取UI文本

    Args:
        key: 文本键名
        lang: 语言(cn/en)
        **kwargs: 格式化参数

    Returns:
        格式化后的文本
    """
    text = UI_TEXTS.get(lang, {}).get(key, "")
    if kwargs:
        return text.format(**kwargs)
    return text


# ==================== 日志配置 ====================

LOG_CONFIG = {
    "level": "INFO",  # 日志级别: DEBUG/INFO/WARNING/ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file": "logs/anti_piracy.log",
    "console": True  # 是否输出到控制台
}


# ==================== 测试配置 ====================

# 测试模式配置(用于调试,不实际执行举报)
TEST_MODE = {
    "enabled": False,  # 是否启用测试模式
    "mock_detection": False,  # 是否模拟检测结果
    "mock_report": True,  # 是否模拟举报操作(不实际提交)
    "save_screenshots": True  # 是否保存截图
}


if __name__ == "__main__":
    # 配置测试
    print("=== 配置文件测试 ===\n")

    print("1. 平台配置:")
    xhs_config = get_platform_config("xiaohongshu")
    print(f"   {xhs_config['name']}: {xhs_config['app_package']}")

    print("\n2. 任务提示词:")
    prompt = get_task_prompt(
        "launch_and_search",
        platform="小红书",
        keyword="得到课程"
    )
    print(f"   {prompt[:50]}...")

    print("\n3. 举报理由:")
    reason = get_report_reason(
        "price_too_low",
        price=9.9,
        original_price=199.0,
        ratio=9.9/199.0
    )
    print(f"   {reason}")

    print("\n4. UI文本:")
    text = get_ui_text("checking_item", lang="cn", title="测试商品")
    print(f"   {text}")

    print("\n✅ 配置文件加载成功")
