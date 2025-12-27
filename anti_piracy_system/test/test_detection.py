#!/usr/bin/env python3
"""
实时 ADB 盗版检测测试

通过 ADB 连接真实手机，自动执行以下流程：
1. 连接设备并检查状态
2. 自动打开小红书 App
3. 搜索关键词并切换到商品标签
4. 点击商品进入详情页
5. 截取商品介绍页（价格+名称）
6. 向下滑动到店铺信息区域
7. 截取店铺信息页
8. 返回列表继续下一个商品（支持自动翻页）

使用方法:
    cd /Users/Apple/Documents/GUI/anti_piracy_system
    source venv/bin/activate
    python test/test_detection.py

前提条件:
    1. 手机已通过 USB 或 WiFi 连接 ADB
"""

import sys
import os
import re
import time
import subprocess
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量 (可选)
try:
    from pathlib import Path
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass


# 小红书 App 配置
XIAOHONGSHU_PACKAGE = "com.xingin.xhs"
SEARCH_KEYWORD = "众合法考"

# 每页可见商品数（双列布局，约2行）
PRODUCTS_PER_PAGE = 4

# 官方店铺列表 - 这些店铺不需要举报
OFFICIAL_SHOPS = [
    "方圆众合教育",
    "众合教育旗舰店",
    "众合法考官方",
    "众合教育官方店",
]


def is_official_shop(shop_name: str, keyword: str = SEARCH_KEYWORD) -> bool:
    """
    判断是否为官方店铺

    Args:
        shop_name: 店铺名称
        keyword: 搜索关键词

    Returns:
        是否为官方店铺
    """
    if not shop_name:
        return False

    # 检查是否在官方店铺列表中
    for official in OFFICIAL_SHOPS:
        if official in shop_name or shop_name in official:
            return True

    # 检查是否包含"官方"且与关键词相关
    if "官方" in shop_name:
        # 检查关键词中的关键字是否出现在店铺名中
        key_parts = ["众合", "法考", "教育"]
        for part in key_parts:
            if part in shop_name:
                return True

    return False


class EvidenceManager:
    """
    证据管理器 - 管理截图和举报证据

    文件夹结构:
    test/evidence/
    └── 20251227_143000_众合法考/          # 时间戳_关键词（顶层）
        ├── report.json                     # 检测报告
        ├── 店铺A名称/                       # 店铺名文件夹
        │   ├── 1_商品介绍.png              # 商品介绍截图
        │   └── 2_店铺信息.png              # 店铺信息截图
        ├── 店铺B名称/
        │   ├── 1_商品介绍.png
        │   └── 2_店铺信息.png
        └── ...
    """

    def __init__(self, keyword: str):
        """初始化证据管理器"""
        # 生成时间戳
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清理关键词中的特殊字符
        safe_keyword = re.sub(r'[\\/:*?"<>|]', '_', keyword)
        # 创建文件夹名: 时间戳_关键词
        folder_name = f"{self.timestamp}_{safe_keyword}"

        # 基础目录
        base_dir = os.path.join(os.path.dirname(__file__), "evidence")
        self.evidence_dir = os.path.join(base_dir, folder_name)
        os.makedirs(self.evidence_dir, exist_ok=True)

        self.keyword = keyword
        self.shops = {}  # 店铺信息 {shop_name: {screenshots: [], info: {}}}

        print(f"\n📁 证据保存目录: {self.evidence_dir}")

    def get_shop_dir(self, shop_name: str) -> str:
        """获取或创建店铺文件夹"""
        # 清理店铺名中的特殊字符
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', shop_name)
        shop_dir = os.path.join(self.evidence_dir, safe_name)
        os.makedirs(shop_dir, exist_ok=True)
        return shop_dir

    def save_product_screenshot(self, shop_name: str, filepath: str):
        """保存商品介绍截图路径"""
        if shop_name not in self.shops:
            self.shops[shop_name] = {"screenshots": {}, "info": {}}
        self.shops[shop_name]["screenshots"]["product"] = filepath

    def save_shop_screenshot(self, shop_name: str, filepath: str):
        """保存店铺信息截图路径"""
        if shop_name not in self.shops:
            self.shops[shop_name] = {"screenshots": {}, "info": {}}
        self.shops[shop_name]["screenshots"]["shop"] = filepath

    def save_shop_info(self, shop_name: str, info: Dict):
        """保存店铺商品信息"""
        if shop_name not in self.shops:
            self.shops[shop_name] = {"screenshots": {}, "info": {}}
        self.shops[shop_name]["info"] = info

    def save_report(self) -> str:
        """保存检测报告"""
        report = {
            "keyword": self.keyword,
            "timestamp": self.timestamp,
            "detection_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_shops": len(self.shops),
            "shops": []
        }

        for shop_name, data in self.shops.items():
            shop_info = {
                "shop_name": shop_name,
                "folder": re.sub(r'[\\/:*?"<>|]', '_', shop_name),
                "title": data["info"].get("title"),
                "price": data["info"].get("price"),
                "screenshots": {
                    "product": os.path.basename(data["screenshots"].get("product", "")),
                    "shop": os.path.basename(data["screenshots"].get("shop", ""))
                }
            }
            report["shops"].append(shop_info)

        report_path = os.path.join(self.evidence_dir, "report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n📄 检测报告已保存: {report_path}")
        return report_path


class ADBController:
    """ADB 设备控制器"""

    def __init__(self, device_id: Optional[str] = None, evidence_manager: Optional[EvidenceManager] = None):
        self.device_id = device_id
        self.evidence_manager = evidence_manager
        self._screen_size = None

    def _adb_cmd(self, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """执行 ADB 命令"""
        cmd = ["adb"]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    def check_connection(self) -> bool:
        """检查设备连接状态"""
        print("\n" + "=" * 50)
        print("步骤 1: 检查 ADB 设备连接")
        print("=" * 50)

        result = self._adb_cmd(["devices", "-l"])
        print(f"\nADB 输出:\n{result.stdout}")

        lines = result.stdout.strip().split("\n")[1:]
        devices = []

        for line in lines:
            if line.strip() and "device" in line and "offline" not in line:
                parts = line.split()
                device_id = parts[0]
                devices.append(device_id)

        if devices:
            if not self.device_id:
                self.device_id = devices[0]
            print(f"✅ 使用设备: {self.device_id}")
            return True
        else:
            print("❌ 未检测到可用设备")
            return False

    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        if self._screen_size:
            return self._screen_size

        result = self._adb_cmd(["shell", "wm", "size"])
        output = result.stdout.strip()
        if "x" in output:
            size_str = output.split(": ")[-1]
            width, height = map(int, size_str.split("x"))
            self._screen_size = (width, height)
            return width, height
        self._screen_size = (1080, 2400)
        return self._screen_size

    def tap(self, x: int, y: int, delay: float = 1.0) -> bool:
        """点击屏幕"""
        self._adb_cmd(["shell", "input", "tap", str(x), str(y)])
        time.sleep(delay)
        return True

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration_ms: int = 500, delay: float = 1.0) -> bool:
        """滑动屏幕"""
        self._adb_cmd([
            "shell", "input", "swipe",
            str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms)
        ])
        time.sleep(delay)
        return True

    def swipe_down(self, delay: float = 1.5) -> bool:
        """向下滑动页面（查看更多内容）"""
        width, height = self.get_screen_size()
        start_x = width // 2
        start_y = int(height * 0.7)
        end_y = int(height * 0.3)
        return self.swipe(start_x, start_y, start_x, end_y, 500, delay)

    def swipe_up_list(self, delay: float = 1.5) -> bool:
        """在商品列表向上滑动（翻页看更多商品）"""
        width, height = self.get_screen_size()
        start_x = width // 2
        start_y = int(height * 0.75)
        end_y = int(height * 0.35)
        print(f"   📜 列表翻页滑动")
        return self.swipe(start_x, start_y, start_x, end_y, 800, delay)

    def swipe_left_bottom(self, delay: float = 1.0) -> bool:
        """在屏幕底部向左滑动（用于分享面板找举报按钮）"""
        width, height = self.get_screen_size()
        start_x = int(width * 0.8)
        end_x = int(width * 0.2)
        y = int(height * 0.85)  # 底部分享面板位置
        print(f"   👈 底部面板向左滑动")
        return self.swipe(start_x, y, end_x, y, 500, delay)

    def back(self, delay: float = 1.0) -> bool:
        """按返回键"""
        self._adb_cmd(["shell", "input", "keyevent", "4"])
        time.sleep(delay)
        return True

    def screenshot(self, filepath: str) -> Optional[str]:
        """截取屏幕并保存"""
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # 在手机上截图
        self._adb_cmd(["shell", "screencap", "-p", "/sdcard/tmp_screenshot.png"])
        # 拉取到本地
        self._adb_cmd(["pull", "/sdcard/tmp_screenshot.png", filepath])
        # 清理
        self._adb_cmd(["shell", "rm", "/sdcard/tmp_screenshot.png"])

        if os.path.exists(filepath):
            print(f"   📸 {os.path.basename(filepath)}")
            return filepath
        return None

    def push_to_gallery(self, local_path: str) -> bool:
        """
        将本地图片推送到手机相册

        Args:
            local_path: 本地图片路径

        Returns:
            是否推送成功
        """
        if not os.path.exists(local_path):
            print(f"   ⚠️ 文件不存在: {local_path}")
            return False

        # 生成手机端路径（放在 DCIM/Screenshots 目录）
        filename = os.path.basename(local_path)
        remote_path = f"/sdcard/DCIM/Screenshots/{filename}"

        # 推送文件到手机
        result = self._adb_cmd(["push", local_path, remote_path])

        if result.returncode == 0:
            # 刷新媒体库，让图片显示在相册中
            self._adb_cmd([
                "shell", "am", "broadcast",
                "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                "-d", f"file://{remote_path}"
            ])
            print(f"   📤 已推送到手机: {filename}")
            return True
        else:
            print(f"   ⚠️ 推送失败: {result.stderr}")
            return False

    def dump_ui_xml(self) -> Optional[str]:
        """获取当前页面的 UI XML"""
        self._adb_cmd(["shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"])
        result = self._adb_cmd(["shell", "cat", "/sdcard/ui_dump.xml"])
        self._adb_cmd(["shell", "rm", "/sdcard/ui_dump.xml"])
        return result.stdout if result.stdout else None

    def force_stop_app(self, package: str) -> bool:
        """强制停止应用"""
        self._adb_cmd(["shell", "am", "force-stop", package])
        time.sleep(0.5)
        return True

    def input_text(self, text: str, delay: float = 0.5) -> bool:
        """输入文本（使用 ADB Keyboard）"""
        self._adb_cmd([
            "shell", "am", "broadcast",
            "-a", "ADB_INPUT_TEXT",
            "--es", "msg", text
        ])
        time.sleep(delay)
        return True

    def input_text_via_clipboard(self, text: str, delay: float = 0.5) -> bool:
        """
        通过剪贴板粘贴文本（最可靠的中文输入方案）

        流程：
        1. 将文本写入手机临时文件
        2. 使用 service call 设置剪贴板
        3. 模拟长按粘贴操作

        Args:
            text: 要输入的文本
            delay: 操作后延迟

        Returns:
            是否成功
        """
        print(f"      使用剪贴板方式输入...")

        # 方法1: 使用 service call clipboard 设置剪贴板（Android 10+）
        # 先将文本 base64 编码后传输，避免特殊字符问题
        import base64
        encoded_text = base64.b64encode(text.encode('utf-8')).decode('ascii')

        # 在手机上解码并写入剪贴板
        # 使用 am broadcast 配合 ClipboardService
        cmd_script = f'''
        echo "{encoded_text}" | base64 -d > /sdcard/clipboard_temp.txt
        '''
        self._adb_cmd(["shell", "sh", "-c", cmd_script])

        # 使用 input 命令触发粘贴（Android 7+）
        # 先尝试使用 am broadcast 设置剪贴板
        self._adb_cmd([
            "shell", "am", "broadcast",
            "-a", "clipper.set",
            "-e", "text", text
        ])
        time.sleep(0.3)

        # 模拟 Ctrl+V 粘贴
        self._adb_cmd(["shell", "input", "keyevent", "279"])  # KEYCODE_PASTE
        time.sleep(delay)

        return True

    def input_text_via_ime(self, text: str, delay: float = 0.5) -> bool:
        """
        通过输入法直接输入文本（使用 ime 命令）

        这是 Android 11+ 支持的新方法，直接通过 IME 输入文本

        Args:
            text: 要输入的文本
            delay: 操作后延迟

        Returns:
            是否成功
        """
        print(f"      使用 IME 方式输入...")

        # 使用 input text 命令（需要先进行 URL 编码处理中文）
        # Android 的 input text 命令可以处理 Unicode
        import urllib.parse
        # 对于中文，需要使用特殊处理
        # 方法：将文本写入文件，然后用 cat 读取并输入

        # 将文本写入手机临时文件
        import base64
        encoded_text = base64.b64encode(text.encode('utf-8')).decode('ascii')

        # 在手机上创建包含文本的临时文件
        self._adb_cmd([
            "shell", "sh", "-c",
            f'echo "{encoded_text}" | base64 -d > /sdcard/input_temp.txt'
        ])

        # 使用 input text 逐字符输入（仅适用于 ASCII）
        # 对于中文，使用广播方式
        result = self._adb_cmd([
            "shell", "am", "broadcast",
            "-a", "ADB_INPUT_TEXT",
            "--es", "msg", text
        ])

        if "Broadcast completed" in result.stdout:
            print(f"      ADB Keyboard 广播发送成功")
            time.sleep(delay)
            return True

        # 备用：尝试使用 Clipper 应用
        self._adb_cmd([
            "shell", "am", "broadcast",
            "-a", "clipper.set",
            "-e", "text", text
        ])
        time.sleep(0.3)

        # 执行粘贴
        self._adb_cmd(["shell", "input", "keyevent", "279"])
        time.sleep(delay)

        return True

    def input_text_smart(self, text: str, delay: float = 0.5) -> bool:
        """
        智能文本输入 - 自动选择最佳输入方法（带验证）

        优先级：
        1. ADB Keyboard 广播（如果已安装并启用）- 带验证
        2. 剪贴板粘贴方式（最可靠）

        Args:
            text: 要输入的文本
            delay: 操作后延迟

        Returns:
            是否成功
        """
        print(f"      智能输入: {len(text)} 字符")

        # 用于验证的文本片段（取前10个非空白字符）
        verify_text = text.replace("\n", "").replace(" ", "")[:10]

        # 方法1: 尝试 ADB Keyboard（最快）
        print(f"      尝试 ADB Keyboard...")
        self._adb_cmd([
            "shell", "am", "broadcast",
            "-a", "ADB_INPUT_TEXT",
            "--es", "msg", text
        ])
        time.sleep(0.8)

        # 验证是否输入成功 - 检查 UI XML 中是否包含输入的文本
        xml_after = self.dump_ui_xml()
        if xml_after and verify_text in xml_after:
            print(f"      ✓ ADB Keyboard 输入成功（已验证）")
            time.sleep(delay)
            return True

        print(f"      ADB Keyboard 未生效，切换到剪贴板方式...")

        # 方法2: 使用剪贴板粘贴（最可靠的中文输入方式）
        # 步骤2.1: 使用 Clipper 应用设置剪贴板
        print(f"      尝试 Clipper 设置剪贴板...")
        self._adb_cmd([
            "shell", "am", "broadcast",
            "-a", "clipper.set",
            "-e", "text", text
        ])
        time.sleep(0.3)

        # 执行粘贴
        self._adb_cmd(["shell", "input", "keyevent", "279"])
        time.sleep(0.8)

        # 验证
        xml_after = self.dump_ui_xml()
        if xml_after and verify_text in xml_after:
            print(f"      ✓ Clipper 粘贴成功（已验证）")
            time.sleep(delay)
            return True

        # 步骤2.2: 如果 Clipper 也不行，尝试使用 am 设置剪贴板
        print(f"      Clipper 未生效，尝试其他剪贴板方法...")

        import base64
        encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')

        # 写入临时文件并通过多种方式设置剪贴板
        self._adb_cmd([
            "shell", "sh", "-c",
            f'echo "{encoded}" | base64 -d > /sdcard/clip_temp.txt'
        ])

        # 尝试使用 content 命令设置剪贴板（Android 10+）
        self._adb_cmd([
            "shell", "sh", "-c",
            'content call --uri content://clipboard/text --method setText --arg "$(cat /sdcard/clip_temp.txt)" 2>/dev/null || true'
        ])

        # 执行粘贴
        self._adb_cmd(["shell", "input", "keyevent", "279"])
        time.sleep(0.8)

        # 再次验证
        xml_after = self.dump_ui_xml()
        if xml_after and verify_text in xml_after:
            print(f"      ✓ 剪贴板粘贴成功（已验证）")
            time.sleep(delay)
            return True

        # 方法3: 最后尝试 - 使用 input text 命令逐字输入（仅适用于 ASCII）
        # 对于中文，这个方法通常不工作，但作为最后手段
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
        if not has_chinese:
            print(f"      尝试 input text 命令...")
            # 转义特殊字符
            escaped_text = text.replace("'", "\\'").replace('"', '\\"').replace(' ', '%s')
            self._adb_cmd(["shell", "input", "text", escaped_text])
            time.sleep(delay)
            return True

        print(f"      ⚠️ 所有输入方法都未能成功！")
        print(f"      请检查：")
        print(f"         1. 是否安装了 ADB Keyboard 并设为默认输入法")
        print(f"         2. 或安装 Clipper 应用")
        print(f"      手动输入可能是必需的。")
        time.sleep(delay)
        return False

    def input_text_chunked(self, text: str, chunk_size: int = 50, delay: float = 0.3) -> bool:
        """
        分段输入文本（用于长文本）

        Args:
            text: 要输入的文本
            chunk_size: 每次输入的字符数
            delay: 每段之间的延迟

        Returns:
            是否成功
        """
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            self.input_text(chunk, delay)
        return True

    def clear_text(self, count: int = 50) -> bool:
        """清除文本"""
        self._adb_cmd(["shell", "input", "keyevent", "--longpress"] + ["67"] * min(count, 20))
        return True

    def debug_dump_ui(self, save_dir: str = None, prefix: str = "debug") -> Dict:
        """
        调试工具：保存当前页面的 UI XML 和截图

        Args:
            save_dir: 保存目录（默认为 test/debug/）
            prefix: 文件名前缀

        Returns:
            包含保存路径的字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if save_dir is None:
            save_dir = os.path.join(os.path.dirname(__file__), "debug")
        os.makedirs(save_dir, exist_ok=True)

        result = {"timestamp": timestamp, "xml_path": None, "screenshot_path": None, "elements": []}

        # 保存 UI XML
        xml = self.dump_ui_xml()
        if xml:
            xml_path = os.path.join(save_dir, f"{prefix}_{timestamp}_ui.xml")
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml)
            result["xml_path"] = xml_path
            print(f"   📄 UI XML 已保存: {xml_path}")

            # 解析并提取关键元素信息
            result["elements"] = self._parse_ui_elements(xml)

        # 保存截图
        screenshot_path = os.path.join(save_dir, f"{prefix}_{timestamp}_screen.png")
        if self.screenshot(screenshot_path):
            result["screenshot_path"] = screenshot_path

        return result

    def _parse_ui_elements(self, xml: str) -> List[Dict]:
        """
        解析 UI XML，提取所有可交互元素的信息

        Args:
            xml: UI XML 内容

        Returns:
            元素信息列表
        """
        elements = []

        # 提取所有节点
        node_pattern = r'<node\s+([^>]+)/>'
        nodes = re.findall(node_pattern, xml)

        for node_attrs in nodes:
            element = {}

            # 提取各个属性
            for attr in ["class", "text", "resource-id", "content-desc", "bounds", "clickable", "focusable"]:
                pattern = rf'{attr}="([^"]*)"'
                match = re.search(pattern, node_attrs)
                if match:
                    element[attr] = match.group(1)

            # 只保留有意义的元素
            if element.get("text") or element.get("class") and ("Edit" in element.get("class", "") or "Input" in element.get("class", "")):
                elements.append(element)

        return elements

    def find_input_elements(self) -> List[Dict]:
        """
        查找页面上所有可能的输入框元素

        Returns:
            输入框元素列表，包含位置信息
        """
        xml = self.dump_ui_xml()
        if not xml:
            return []

        input_elements = []

        # 查找 EditText、Input 等输入框
        patterns = [
            r'class="[^"]*(?:EditText|Input|TextField)[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*',
            r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*class="[^"]*(?:EditText|Input|TextField)[^"]*"',
            # 查找 focusable 且 clickable 的元素
            r'focusable="true"[^>]*clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, xml)
            for m in matches:
                x1, y1, x2, y2 = map(int, m)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                area = (x2 - x1) * (y2 - y1)
                input_elements.append({
                    "bounds": (x1, y1, x2, y2),
                    "center": (center_x, center_y),
                    "area": area
                })

        # 按面积排序（大的在前）
        input_elements.sort(key=lambda x: x["area"], reverse=True)
        return input_elements

    def get_current_package(self) -> str:
        """获取当前前台应用"""
        result = self._adb_cmd(["shell", "dumpsys", "window"])
        output = result.stdout
        for line in output.split("\n"):
            if "mCurrentFocus" in line and "Window{" in line:
                match = re.search(r'(\S+)/\S+\}', line)
                if match:
                    return match.group(1)
            elif "mFocusedApp" in line and "ActivityRecord{" in line:
                match = re.search(r'u\d+\s+(\S+)/', line)
                if match:
                    return match.group(1)
        return ""

    def find_and_click_text(self, text: str, delay: float = 1.0) -> bool:
        """查找并点击文本"""
        xml = self.dump_ui_xml()
        if not xml:
            return False

        pattern = rf'text="[^"]*{re.escape(text)}[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        match = re.search(pattern, xml)

        if not match:
            pattern = rf'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*text="[^"]*{re.escape(text)}[^"]*"'
            match = re.search(pattern, xml)

        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            print(f"   找到 '{text}' -> ({center_x}, {center_y})")
            return self.tap(center_x, center_y, delay)
        return False


class XiaohongshuController:
    """小红书 App 控制器"""

    def __init__(self, adb: ADBController):
        self.adb = adb
        self.package = XIAOHONGSHU_PACKAGE

    def launch(self) -> bool:
        """启动小红书"""
        print("\n" + "=" * 50)
        print("步骤 2: 启动小红书 App")
        print("=" * 50)

        self.adb.force_stop_app(self.package)
        time.sleep(1)

        print(f"   启动应用: {self.package}")
        self.adb._adb_cmd([
            "shell", "monkey",
            "-p", self.package,
            "-c", "android.intent.category.LAUNCHER",
            "1"
        ])
        time.sleep(5)

        current = self.adb.get_current_package()
        if self.package in current:
            print("✅ 小红书已启动")
            return True
        else:
            print(f"⚠️ 尝试继续...")
            return True

    def search(self, keyword: str) -> bool:
        """搜索关键词"""
        print("\n" + "=" * 50)
        print(f"步骤 3: 搜索 '{keyword}'")
        print("=" * 50)

        width, height = self.adb.get_screen_size()

        # 点击搜索图标
        print("\n   点击搜索图标")
        self.adb.tap(width - 60, int(height * 0.06), delay=2.0)

        # 尝试点击历史记录
        if self.adb.find_and_click_text(keyword, delay=0.5):
            print(f"   ✅ 点击历史记录: {keyword}")
            time.sleep(3)
            return True

        # 尝试点击搜索建议
        for suggestion in [f"{keyword}学习包", f"{keyword}客观题", keyword]:
            if self.adb.find_and_click_text(suggestion, delay=0.5):
                print(f"   ✅ 点击搜索建议: {suggestion}")
                time.sleep(3)
                return True

        # 手动输入
        print("   手动输入搜索")
        self.adb.tap(width // 2, int(height * 0.03), delay=1.0)
        self.adb.clear_text(30)
        time.sleep(0.3)
        self.adb.input_text(keyword)
        time.sleep(0.5)
        self.adb.tap(width - 80, int(height * 0.03), delay=3.0)

        print("✅ 搜索完成")
        return True

    def switch_to_products_tab(self) -> bool:
        """切换到商品标签"""
        print("\n" + "=" * 50)
        print("步骤 4: 切换到商品标签")
        print("=" * 50)

        if self.adb.find_and_click_text("商品", delay=2.0):
            print("✅ 已切换到商品标签")
            return True

        for text in ["购物", "goods"]:
            if self.adb.find_and_click_text(text, delay=2.0):
                print(f"✅ 通过 '{text}' 切换")
                return True

        print("⚠️ 未找到商品标签")
        return False


class ProductExtractor:
    """商品信息提取器"""

    def __init__(self, adb: ADBController):
        self.adb = adb

    def extract_from_xml(self, xml_content: str) -> Dict:
        """从 UI XML 中提取商品信息"""
        info = {"title": None, "price": None, "shop_name": None}

        if not xml_content:
            return info

        # 提取所有 text
        text_pattern = r'text="([^"]*)"'
        all_texts = [t for t in re.findall(text_pattern, xml_content) if t.strip()]

        # 提取价格
        for text in all_texts:
            if "¥" in text:
                price_match = re.search(r'[\d.]+', text)
                if price_match:
                    try:
                        price = float(price_match.group())
                        if info["price"] is None or price > info["price"]:
                            info["price"] = price
                    except ValueError:
                        pass

        # 提取店铺名
        shop_exclude = ["店铺内", "进店", "商品评价", "店铺推荐", "评价", "详情", "推荐"]
        shop_keywords = ["旗舰店", "专营店", "官方店", "的店", "店铺"]

        for text in all_texts:
            if any(ex in text for ex in shop_exclude):
                continue
            for keyword in shop_keywords:
                if keyword in text and 3 < len(text) < 25:
                    info["shop_name"] = text
                    break
            if info["shop_name"]:
                break

        if not info["shop_name"]:
            for text in all_texts:
                if any(ex in text for ex in shop_exclude):
                    continue
                if "教育" in text and 4 < len(text) < 20:
                    info["shop_name"] = text
                    break

        # 提取标题
        skip_keywords = ["评价", "销量", "发货", "包邮", "优惠", "店铺", "客服", "购物车",
                        "加入", "立即", "搜索", "商品", "详情", "推荐", "粉丝", "已售"]
        for text in all_texts:
            if len(text) > 15 and not info["title"]:
                if not any(kw in text for kw in skip_keywords):
                    info["title"] = text

        return info


# ==================== 举报相关函数 ====================

def generate_report_text(keyword: str, shop_name: str, price: float,
                         title: str = None, original_price: float = 299) -> str:
    """
    生成举报说明文本（200字以内，简洁有力，包含三条关键证据）

    Args:
        keyword: 搜索关键词（品牌名）
        shop_name: 店铺名称
        price: 商品价格
        title: 商品标题（用于提取关键词特征）
        original_price: 正版原价（默认299）

    Returns:
        格式化的举报说明文本
    """
    # 格式化价格
    price_str = f"¥{price:.0f}" if price else "异常低价"
    original_str = f"¥{original_price:.0f}"

    # 检测商品标题中的盗版关键词
    piracy_keywords = []
    if title:
        keyword_patterns = [
            ("百度网盘", "百度网盘"),
            ("网盘", "网盘分发"),
            ("秒发", "秒发"),
            ("电子版", "电子版"),
            ("PDF", "PDF电子版"),
            ("视频课程", "视频课程"),
            ("录屏", "录屏"),
            ("资料包", "资料包"),
            ("全套", "全套资料"),
            ("永久", "永久有效"),
            ("链接", "链接分发"),
        ]
        for pattern, desc in keyword_patterns:
            if pattern in title:
                piracy_keywords.append(desc)

    # 构建关键词描述
    if piracy_keywords:
        keywords_desc = "、".join(piracy_keywords[:3])  # 最多取3个
        keyword_evidence = f'商品描述中包含"{keywords_desc}"等非法分发关键词'
    else:
        keyword_evidence = "商品以电子资料形式销售，涉嫌非法复制分发"

    # 判断店铺类型
    if "旗舰" in shop_name or "官方" in shop_name or "专营" in shop_name:
        shop_type = "冒充官方店铺"
    else:
        shop_type = "个人店铺，无出版社授权证明"

    # 生成三条关键举报理由（约180字，符合200字限制）
    text = f"""该商品涉嫌盗版侵权，具体如下：
1.价格异常：售价显著低于正版定价({original_str} vs {price_str})，明显不符合正规渠道价格
2.分发方式违规：{keyword_evidence}
3.店铺资质存疑："{shop_name}"为{shop_type}，无"{keyword}"正版授权
已截图取证，请平台核实下架。"""

    return text


def upload_evidence_images(adb: ADBController, evidence: EvidenceManager,
                           shop_name: str, max_images: int = 2) -> bool:
    """
    上传证据图片（适配小红书举报页面UI）

    小红书举报页面的图片上传流程：
    1. 点击"+"按钮
    2. 弹出选项菜单，选择"从相册中选择"
    3. 进入相册，选择图片
    4. 确认选择

    Args:
        adb: ADB 控制器
        evidence: 证据管理器
        shop_name: 店铺名称
        max_images: 最多上传图片数量（默认2张）

    Returns:
        是否上传成功
    """
    print("   上传证据图片...")

    width, height = adb.get_screen_size()

    # Step 1: 通过 UI XML 精确定位"+"按钮或"0/3"位置
    print("   Step 1: 查找并点击添加图片按钮...")

    xml = adb.dump_ui_xml()
    add_btn_clicked = False

    if xml:
        # 方法1: 查找"0/3"文字（在"+"按钮旁边）
        pattern = r'text="0/3"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        match = re.search(pattern, xml)
        if not match:
            pattern = r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*text="0/3"'
            match = re.search(pattern, xml)

        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            # "+"按钮在"0/3"左边，点击稍微偏左上的位置
            add_x = x1 - 50
            add_y = (y1 + y2) // 2 - 30
            print(f"   找到 '0/3'，点击左侧的+按钮: ({add_x}, {add_y})")
            adb.tap(add_x, add_y, delay=1.5)
            add_btn_clicked = True

        # 方法2: 查找"图片证据"位置
        if not add_btn_clicked:
            pattern = r'text="图片证据"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
            match = re.search(pattern, xml)
            if not match:
                pattern = r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*text="图片证据"'
                match = re.search(pattern, xml)

            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                # "+"按钮在"图片证据"下方
                add_x = x1 + 60
                add_y = y2 + 60
                print(f"   找到'图片证据'，点击下方+按钮: ({add_x}, {add_y})")
                adb.tap(add_x, add_y, delay=1.5)
                add_btn_clicked = True

    if not add_btn_clicked:
        # 备用方案：根据截图分析，"+"按钮大约在屏幕 60% 高度，左侧 15% 位置
        print("   使用默认位置点击+按钮...")
        adb.tap(int(width * 0.15), int(height * 0.62), delay=1.5)

    time.sleep(1)

    # Step 2: 点击"从相册中选择"
    print("   Step 2: 选择'从相册中选择'...")

    # 查找并点击"从相册中选择"选项
    album_options = ["从相册中选择", "从相册选择", "相册", "选择照片", "照片"]
    option_clicked = False
    for option in album_options:
        if adb.find_and_click_text(option, delay=1.5):
            print(f"   ✅ 点击了: {option}")
            option_clicked = True
            break

    if not option_clicked:
        # 可能直接进入了相册，或者需要点击弹窗中的选项
        print("   未找到相册选项，检查是否已在相册...")

    time.sleep(1.5)

    # 处理权限弹窗
    if adb.find_and_click_text("允许", delay=1.0):
        print("   已授权相册访问")
        time.sleep(1)

    # 处理可能的"仅限此次"或"始终允许"选项
    if adb.find_and_click_text("仅限此次", delay=0.5):
        print("   选择了: 仅限此次")
        time.sleep(1)
    elif adb.find_and_click_text("始终允许", delay=0.5):
        print("   选择了: 始终允许")
        time.sleep(1)

    # Step 3: 现在应该在相册选择界面，选择图片
    print(f"   Step 3: 选择最新的 {max_images} 张图片...")

    # 检查是否在相册界面
    time.sleep(1)

    # 尝试切换到截图相册
    album_names = ["截图", "Screenshots", "屏幕截图", "最近项目", "最近", "全部图片", "全部"]
    for album in album_names:
        if adb.find_and_click_text(album, delay=1.0):
            print(f"   切换到相册: {album}")
            time.sleep(1)
            break

    time.sleep(1)

    # 获取相册界面的 UI XML，查找实际的图片元素位置
    xml_album = adb.dump_ui_xml()
    selected_count = 0

    if xml_album:
        # 方法1: 查找 ImageView 类型的图片元素（相册中的图片通常是 ImageView）
        # 匹配 class 包含 ImageView 且有合理尺寸的元素
        imageview_pattern = r'class="[^"]*ImageView[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        matches = re.findall(imageview_pattern, xml_album)

        if not matches:
            imageview_pattern = r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*class="[^"]*ImageView[^"]*"'
            matches = re.findall(imageview_pattern, xml_album)

        # 筛选出合理尺寸的图片（排除小图标）
        image_positions = []
        min_size = width // 6  # 图片最小边长（约为屏幕宽度的1/6）

        for m in matches:
            x1, y1, x2, y2 = map(int, m)
            w = x2 - x1
            h = y2 - y1
            # 筛选：宽高都大于最小尺寸，且在屏幕中部（排除顶部导航栏）
            if w > min_size and h > min_size and y1 > height * 0.1:
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                image_positions.append((center_x, center_y, y1, x1))

        # 按 y 坐标排序（从上到下），同行按 x 排序（从左到右）
        image_positions.sort(key=lambda p: (p[2], p[3]))

        if image_positions:
            print(f"   通过 UI XML 找到 {len(image_positions)} 张图片")
            # 选择前 max_images 张图片
            for i, (cx, cy, _, _) in enumerate(image_positions[:max_images]):
                print(f"   点击图片 {i + 1}: ({cx}, {cy})")
                adb.tap(cx, cy, delay=0.8)
                selected_count += 1

    # 如果 UI XML 方法未能找到足够的图片，使用备用固定位置方法
    if selected_count < max_images:
        print(f"   UI XML 方法选择了 {selected_count} 张，尝试固定位置补充选择...")

        # 小红书相册通常是 4 列网格，图片从屏幕约 15% 高度开始
        # 每张图片约占 25% 宽度，间距较小
        for i in range(selected_count, max_images):
            col = i % 4
            row = i // 4
            # 图片网格位置 - 调整为更准确的位置
            img_x = int(width * (0.125 + col * 0.25))
            img_y = int(height * (0.18 + row * 0.18))

            print(f"   点击图片 {i + 1} (固定位置): ({img_x}, {img_y})")
            adb.tap(img_x, img_y, delay=0.8)
            selected_count += 1

    time.sleep(1)

    # Step 4: 点击确认按钮
    print("   Step 4: 确认选择...")

    # 先获取当前页面 XML 查找确认按钮的精确位置
    xml_confirm = adb.dump_ui_xml()
    confirmed = False

    if xml_confirm:
        # 查找带有数字的确认按钮，如 "确定(2)" 或 "完成(3)"
        confirm_pattern = r'text="[^"]*(?:确定|完成|确认)[^"]*\(\d+\)[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        match = re.search(confirm_pattern, xml_confirm)
        if not match:
            confirm_pattern = r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*text="[^"]*(?:确定|完成|确认)[^"]*\(\d+\)[^"]*"'
            match = re.search(confirm_pattern, xml_confirm)

        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            print(f"   找到确认按钮，点击: ({center_x}, {center_y})")
            adb.tap(center_x, center_y, delay=1.5)
            confirmed = True

    if not confirmed:
        # 尝试文本匹配
        confirm_buttons = ["确定", "完成", "确认", "下一步", "添加"]
        for btn_text in confirm_buttons:
            if adb.find_and_click_text(btn_text, delay=1.5):
                print(f"   ✅ 点击了: {btn_text}")
                confirmed = True
                break

    if not confirmed:
        # 尝试点击右上角确认按钮
        print("   尝试点击右上角确认...")
        adb.tap(width - 80, int(height * 0.06), delay=1.5)

    print(f"   ✅ 已选择 {selected_count} 张证据图片")
    return selected_count > 0


def fill_report_text(adb: ADBController, text: str, debug: bool = False) -> bool:
    """
    填写举报说明文本（增强版 - 支持调试和多种输入方法）

    Args:
        adb: ADB 控制器
        text: 要填写的文本
        debug: 是否启用调试模式（保存 UI XML 和截图）

    Returns:
        是否填写成功
    """
    print("   填写举报说明...")

    width, height = adb.get_screen_size()

    # 调试模式：保存当前页面信息
    if debug:
        print("   [DEBUG] 保存举报页面 UI 信息...")
        adb.debug_dump_ui(prefix="report_page_before")

    # 获取 UI XML
    xml = adb.dump_ui_xml()
    input_clicked = False
    click_position = None

    if xml:
        print("   分析页面元素...")

        # 方法1: 直接查找 EditText 类型的输入框（最可靠）
        # 使用更通用的正则表达式，匹配节点的所有属性
        edittext_elements = []

        # 匹配所有包含 EditText 的节点
        node_pattern = r'<node[^>]*class="[^"]*EditText[^"]*"[^>]*/>'
        nodes = re.findall(node_pattern, xml)

        for node in nodes:
            bounds_match = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
            if bounds_match:
                x1, y1, x2, y2 = map(int, bounds_match.groups())
                area = (x2 - x1) * (y2 - y1)
                # 提取更多信息用于调试
                text_match = re.search(r'text="([^"]*)"', node)
                hint_text = text_match.group(1) if text_match else ""
                edittext_elements.append({
                    "bounds": (x1, y1, x2, y2),
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                    "area": area,
                    "hint": hint_text
                })

        if edittext_elements:
            print(f"   找到 {len(edittext_elements)} 个 EditText 元素:")
            for i, elem in enumerate(edittext_elements):
                print(f"      [{i}] 位置: {elem['bounds']}, 面积: {elem['area']}, 提示: '{elem['hint'][:20]}...' if len(elem['hint']) > 20 else '{elem['hint']}'")

            # 选择最大的那个（通常是主输入框）
            best_elem = max(edittext_elements, key=lambda x: x["area"])
            center_x, center_y = best_elem["center"]
            click_position = (center_x, center_y)
            print(f"   选择最大的 EditText，点击: ({center_x}, {center_y})")
            adb.tap(center_x, center_y, delay=1.0)
            input_clicked = True

        # 方法2: 如果没找到 EditText，查找包含提示文字的元素
        if not input_clicked:
            print("   未找到 EditText，尝试通过提示文字定位...")
            hints = ["提供更多信息", "有助于举报", "请输入", "举报描述", "0/200", "字"]

            for hint in hints:
                # 使用更宽松的匹配
                pattern = rf'text="[^"]*{re.escape(hint)}[^"]*"'
                if re.search(pattern, xml):
                    # 找到了提示文字，获取其位置
                    full_pattern = rf'<node[^>]*text="[^"]*{re.escape(hint)}[^"]*"[^>]*/>'
                    node_match = re.search(full_pattern, xml)
                    if node_match:
                        bounds_match = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node_match.group())
                        if bounds_match:
                            x1, y1, x2, y2 = map(int, bounds_match.groups())
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            click_position = (center_x, center_y)
                            print(f"   通过提示文字 '{hint}' 找到输入区域，点击: ({center_x}, {center_y})")
                            adb.tap(center_x, center_y, delay=1.0)
                            input_clicked = True
                            break

        # 方法3: 查找 focusable="true" 的大区域元素
        if not input_clicked:
            print("   尝试通过 focusable 属性定位...")
            focusable_pattern = r'<node[^>]*focusable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*/>'
            matches = re.findall(focusable_pattern, xml)

            focusable_elements = []
            for m in matches:
                x1, y1, x2, y2 = map(int, m)
                area = (x2 - x1) * (y2 - y1)
                # 筛选合理大小的元素（输入框通常比较大）
                if area > 10000 and y1 > height * 0.2 and y2 < height * 0.7:
                    focusable_elements.append({
                        "bounds": (x1, y1, x2, y2),
                        "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                        "area": area
                    })

            if focusable_elements:
                # 选择最大的
                best_elem = max(focusable_elements, key=lambda x: x["area"])
                center_x, center_y = best_elem["center"]
                click_position = (center_x, center_y)
                print(f"   通过 focusable 属性找到元素，点击: ({center_x}, {center_y})")
                adb.tap(center_x, center_y, delay=1.0)
                input_clicked = True

    if not input_clicked:
        # 方法4: 使用默认位置（根据小红书举报页面布局）
        print("   使用默认位置点击输入框...")
        # 举报描述输入框通常在页面中部偏上
        default_positions = [
            (int(width * 0.5), int(height * 0.40)),  # 40% 高度
            (int(width * 0.5), int(height * 0.45)),  # 45% 高度
            (int(width * 0.5), int(height * 0.35)),  # 35% 高度
        ]
        for pos in default_positions:
            print(f"   尝试位置: {pos}")
            adb.tap(pos[0], pos[1], delay=0.8)
            click_position = pos
            time.sleep(0.5)
            # 检查是否弹出键盘（简单判断）
            # 这里我们假设点击后继续尝试输入
        input_clicked = True

    # 等待键盘弹出
    time.sleep(1.0)

    # 如果已经点击了位置，再次点击确保焦点
    if click_position:
        print(f"   再次点击确保焦点: {click_position}")
        adb.tap(click_position[0], click_position[1], delay=0.5)

    # 清除可能的已有文本
    print("   清除已有文本...")
    adb.clear_text(50)
    time.sleep(0.3)

    # 输入举报文本 - 使用智能输入方法
    print(f"   输入文本 ({len(text)} 字符)...")

    # 使用智能输入方法，自动选择最佳输入方式
    adb.input_text_smart(text, delay=1.0)

    time.sleep(1.0)

    # 调试模式：保存输入后的页面信息
    if debug:
        print("   [DEBUG] 保存输入后页面信息...")
        adb.debug_dump_ui(prefix="report_page_after")

    # 验证输入是否成功 - 重新获取 XML 检查
    print("   验证输入结果...")
    xml_after = adb.dump_ui_xml()

    input_verified = False
    if xml_after:
        # 检查文本的前几个字符是否出现在页面上
        check_text = text[:15].replace("\n", "")  # 取前15个字符，去掉换行
        if check_text in xml_after:
            print(f"   ✅ 文本输入验证成功 (找到: '{check_text}')")
            input_verified = True
        else:
            # 检查是否有任何新文本出现
            text_pattern = r'text="([^"]+)"'
            texts_after = set(re.findall(text_pattern, xml_after))
            # 查找较长的文本（可能是我们输入的）
            long_texts = [t for t in texts_after if len(t) > 30]
            if long_texts:
                print(f"   ⚠️ 未找到预期文本，但页面有长文本: {long_texts[0][:50]}...")
            else:
                print("   ⚠️ 无法验证文本是否输入成功")

    # 点击空白处收起键盘
    print("   收起键盘...")
    adb.tap(int(width * 0.5), int(height * 0.10), delay=0.5)

    if input_verified:
        print("   ✅ 举报说明填写完成")
    else:
        print("   ⚠️ 举报说明填写可能未成功，继续流程...")

    return True


def report_product(adb: ADBController, evidence: EvidenceManager,
                   shop_name: str, product_index: int,
                   keyword: str = SEARCH_KEYWORD, price: float = 0,
                   title: str = None, debug: bool = False) -> bool:
    """
    执行商品举报流程（适配小红书实际UI - 两级选择）

    流程：
    1. 点击右上角分享按钮
    2. 在底部分享面板向左滑动找到举报
    3. 点击举报
    4. 【第一级】选择举报类型：假货/低质/山寨商品举报
    5. 【第二级】选择举报原因：盗版图书音像制品类
    6. 填写举报描述（0/200字）
    7. 上传图片证据（最多3张，从相册选择最新截图）
    8. 提交举报

    Args:
        adb: ADB 控制器
        evidence: 证据管理器
        shop_name: 店铺名称
        product_index: 商品索引
        keyword: 搜索关键词
        price: 商品价格
        debug: 是否启用调试模式

    Returns:
        是否举报成功
    """
    print(f"\n{'=' * 50}")
    print(f"执行举报流程 - 商品 {product_index + 1}")
    print(f"   店铺: {shop_name}")
    if debug:
        print(f"   [DEBUG] 调试模式已启用")
    print("=" * 50)

    width, height = adb.get_screen_size()

    # Step 1: 点击右上角分享按钮
    print("\n[Step 1] 点击分享按钮...")
    # 小红书商品详情页分享按钮通常在右上角
    share_x = width - 60
    share_y = int(height * 0.06)
    adb.tap(share_x, share_y, delay=2.0)

    # Step 2: 在底部分享面板向左滑动找举报
    print("\n[Step 2] 滑动分享面板找举报按钮...")
    found_report = False

    # 先尝试直接找举报按钮
    if adb.find_and_click_text("举报", delay=1.5):
        found_report = True
    else:
        # 向左滑动最多3次找举报
        for i in range(3):
            adb.swipe_left_bottom(delay=1.0)
            if adb.find_and_click_text("举报", delay=1.5):
                found_report = True
                break

    if not found_report:
        print("   ⚠️ 未找到举报按钮，尝试其他方式...")
        # 尝试点击更多选项
        if adb.find_and_click_text("更多", delay=1.5):
            time.sleep(1)
            adb.find_and_click_text("举报", delay=1.5)
            found_report = True

    if not found_report:
        print("   ❌ 无法找到举报入口")
        adb.back(delay=1.0)  # 关闭分享面板
        return False

    # Step 3: 【第一级】选择举报类型
    print("\n[Step 3] 选择举报类型（第一级）...")
    time.sleep(1.5)

    # 小红书第一级举报类型（按优先级排序）
    first_level_types = [
        "假货/低质/山寨商品举报",  # 首选
        "假货",
        "低质",
        "山寨",
        "商品举报",
        "其他"
    ]
    type_selected = False
    for rt in first_level_types:
        if adb.find_and_click_text(rt, delay=1.5):
            print(f"   ✅ 选择举报类型: {rt}")
            type_selected = True
            break

    if not type_selected:
        print("   ⚠️ 未找到预期的举报类型，尝试点击列表选项...")
        # 尝试点击列表中的选项（通常在屏幕中部）
        adb.tap(int(width * 0.5), int(height * 0.4), delay=1.5)

    time.sleep(1.5)

    # Step 4: 【第二级】选择举报原因
    print("\n[Step 4] 选择举报原因（第二级）...")

    # 小红书第二级举报原因（按优先级排序）
    second_level_reasons = [
        "盗版图书音像制品类",  # 首选
        "盗版图书",
        "音像制品",
        "山寨抄袭商品类",
        "假货商品类",
        "低质劣质商品类",
        "其他"
    ]
    reason_selected = False
    for reason in second_level_reasons:
        if adb.find_and_click_text(reason, delay=1.5):
            print(f"   ✅ 选择举报原因: {reason}")
            reason_selected = True
            break

    if not reason_selected:
        print("   ⚠️ 未找到预期的举报原因，尝试点击第一个选项...")
        adb.tap(int(width * 0.5), int(height * 0.35), delay=1.5)

    time.sleep(1)

    # Step 5: 填写举报描述（举报描述输入框，0/200字）
    print("\n[Step 5] 填写举报描述...")
    report_text = generate_report_text(keyword, shop_name, price, title=title)
    fill_report_text(adb, report_text, debug=debug)

    # Step 6: 上传图片证据（最多3张）
    print("\n[Step 6] 上传图片证据...")
    upload_evidence_images(adb, evidence, shop_name, max_images=3)

    # Step 7: 提交举报
    print("\n[Step 7] 提交举报...")
    submit_buttons = ["提交", "提交举报", "确认提交", "确定"]
    submitted = False
    for btn_text in submit_buttons:
        if adb.find_and_click_text(btn_text, delay=2.0):
            submitted = True
            break

    if submitted:
        print(f"\n✅ 举报提交成功 - 商品 {product_index + 1}")
        time.sleep(1.5)

        # 处理可能的确认弹窗
        adb.find_and_click_text("确定", delay=1.0) or \
        adb.find_and_click_text("知道了", delay=1.0)

        return True
    else:
        print(f"\n⚠️ 举报提交可能失败 - 商品 {product_index + 1}")
        adb.back(delay=1.0)
        return False


def extract_single_product(adb: ADBController, extractor: ProductExtractor,
                           evidence: EvidenceManager, product_index: int,
                           visible_index: int, enable_report: bool = False,
                           keyword: str = SEARCH_KEYWORD,
                           debug: bool = False) -> Optional[Dict]:
    """
    提取单个商品信息（可选举报）

    流程：
    1. 点击商品进入详情页
    2. 立即截图（商品标题+价格）
    3. 提取顶部信息
    4. 向下滑动到店铺区域
    5. 截图（店铺名称）
    6. 提取店铺信息
    7. [可选] 执行举报流程
    8. 返回列表

    Args:
        adb: ADB 控制器
        extractor: 提取器
        evidence: 证据管理器
        product_index: 总商品索引 (0-based)
        visible_index: 当前页面可见位置索引 (0-3)
        enable_report: 是否执行举报流程
        keyword: 搜索关键词
        debug: 是否启用调试模式

    Returns:
        商品信息字典
    """
    print(f"\n{'=' * 50}")
    print(f"提取第 {product_index + 1} 个商品")
    print("=" * 50)

    width, height = adb.get_screen_size()

    # 计算点击位置（双列布局）
    col = visible_index % 2
    row = visible_index // 2

    if col == 0:
        tap_x = width // 4
    else:
        tap_x = (width * 3) // 4

    # 第一行约在 35%，第二行约在 65%
    if row == 0:
        tap_y = int(height * 0.40)
    else:
        tap_y = int(height * 0.70)

    # 步骤1: 点击商品进入详情页
    print(f"\n1. 点击商品 (位置: 列{col+1}, 行{row+1})")
    adb.tap(tap_x, tap_y, delay=2.5)

    # 生成时间戳，确保文件按时间排序（用于相册选择）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 步骤2: 立即截图商品介绍页（标题+价格）- 最关键的第一张图
    print("\n2. 截取商品介绍页（标题+价格）")
    # 使用带时间戳的临时文件名，后续根据店铺名重命名
    temp_product_screenshot = os.path.join(
        evidence.evidence_dir,
        f"temp_{timestamp}_1_product_{product_index + 1}.png"
    )
    adb.screenshot(temp_product_screenshot)

    # 提取顶部信息
    xml_top = adb.dump_ui_xml()
    info_top = extractor.extract_from_xml(xml_top)

    # 步骤3: 向下滑动到店铺信息区域
    print("\n3. 滑动到店铺信息区域")
    adb.swipe_down(delay=1.5)

    # 更新时间戳（确保第二张图时间更新）
    timestamp2 = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 步骤4: 截图店铺信息页
    print("\n4. 截取店铺信息页（店铺名称）")
    temp_shop_screenshot = os.path.join(
        evidence.evidence_dir,
        f"temp_{timestamp2}_2_shop_{product_index + 1}.png"
    )
    adb.screenshot(temp_shop_screenshot)

    # 提取店铺信息
    xml_bottom = adb.dump_ui_xml()
    info_bottom = extractor.extract_from_xml(xml_bottom)

    # 合并信息
    final_info = {
        "index": product_index + 1,
        "title": info_top.get("title") or info_bottom.get("title"),
        "price": info_top.get("price") or info_bottom.get("price"),
        "shop_name": info_bottom.get("shop_name") or info_top.get("shop_name") or f"未知店铺_{product_index + 1}",
    }

    shop_name = final_info["shop_name"]

    # 步骤5: 将临时截图移动到店铺文件夹并重命名
    print(f"\n5. 保存证据到店铺文件夹: {shop_name}")
    shop_dir = evidence.get_shop_dir(shop_name)

    # 生成推送到手机时使用的时间戳文件名（确保在相册中按时间排序）
    push_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 移动截图1: 商品介绍（价格+名称）
    product_screenshot = os.path.join(shop_dir, "1_商品介绍.png")
    if os.path.exists(temp_product_screenshot):
        os.rename(temp_product_screenshot, product_screenshot)
        evidence.save_product_screenshot(shop_name, product_screenshot)
        print(f"   📸 1_商品介绍.png")
        # 如果启用举报，推送到手机相册（使用时间戳文件名确保排序）
        if enable_report:
            # 创建带时间戳的副本用于推送
            push_path = os.path.join(shop_dir, f"{push_timestamp}_1_商品介绍.png")
            import shutil
            shutil.copy2(product_screenshot, push_path)
            adb.push_to_gallery(push_path)

    # 稍等一下确保时间戳不同
    time.sleep(0.5)
    push_timestamp2 = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 移动截图2: 店铺信息
    shop_screenshot = os.path.join(shop_dir, "2_店铺信息.png")
    if os.path.exists(temp_shop_screenshot):
        os.rename(temp_shop_screenshot, shop_screenshot)
        evidence.save_shop_screenshot(shop_name, shop_screenshot)
        print(f"   📸 2_店铺信息.png")
        # 如果启用举报，推送到手机相册（使用时间戳文件名确保排序）
        if enable_report:
            # 创建带时间戳的副本用于推送
            push_path2 = os.path.join(shop_dir, f"{push_timestamp2}_2_店铺信息.png")
            import shutil
            shutil.copy2(shop_screenshot, push_path2)
            adb.push_to_gallery(push_path2)

    # 保存商品信息
    evidence.save_shop_info(shop_name, final_info)

    # 步骤6: 判断是否为官方店铺，决定是否执行举报
    report_success = False
    skip_report = False

    if enable_report:
        # 检查是否为官方店铺
        if is_official_shop(shop_name, keyword):
            print(f"\n6. ✅ 官方店铺，跳过举报: {shop_name}")
            skip_report = True
            final_info["is_official"] = True
            final_info["reported"] = False
        else:
            print("\n6. 执行举报流程...")
            final_info["is_official"] = False
            # 需要先滑动回商品详情页顶部，才能点击分享按钮
            adb.swipe(width // 2, int(height * 0.3), width // 2, int(height * 0.7), 500, 1.0)
            time.sleep(0.5)
            report_success = report_product(
                adb, evidence, shop_name, product_index,
                keyword=keyword,
                price=final_info.get("price", 0),
                title=final_info.get("title"),
                debug=debug
            )
            final_info["reported"] = report_success

    # 步骤7: 返回列表
    step_num = 7 if enable_report else 6
    print(f"\n{step_num}. 返回商品列表")
    adb.back(delay=1.5)

    print(f"\n✅ 商品 {product_index + 1} 完成:")
    print(f"   标题: {final_info['title'] or '未提取到'}")
    print(f"   价格: ¥{final_info['price'] or '未提取到'}")
    print(f"   店铺: {shop_name}")
    if enable_report:
        print(f"   举报: {'✅ 成功' if report_success else '❌ 失败'}")

    return final_info


def run_detection(num_products: int = 3, keyword: str = SEARCH_KEYWORD,
                  enable_report: bool = False, debug: bool = False):
    """
    运行盗版检测

    Args:
        num_products: 要检测的商品数量
        keyword: 搜索关键词
        enable_report: 是否启用举报功能
        debug: 是否启用调试模式
    """
    print("\n" + "=" * 60)
    print("盗版检测 - 小红书商品信息提取")
    if enable_report:
        print("⚠️  举报模式已启用")
    if debug:
        print("🔧 调试模式已启用")
    print("=" * 60)

    print(f"\n检测配置:")
    print(f"   搜索关键词: {keyword}")
    print(f"   检测商品数量: {num_products}")
    print(f"   自动举报: {'是' if enable_report else '否'}")
    print(f"   调试模式: {'是' if debug else '否'}")

    # 初始化
    evidence = EvidenceManager(keyword)
    adb = ADBController(evidence_manager=evidence)

    if not adb.check_connection():
        print("\n❌ 测试终止: 无法连接设备")
        return None

    width, height = adb.get_screen_size()
    print(f"\n屏幕尺寸: {width} x {height}")

    xhs = XiaohongshuController(adb)
    if not xhs.launch():
        return None

    xhs.search(keyword)
    xhs.switch_to_products_tab()

    print("\n等待商品列表加载...")
    time.sleep(2)

    extractor = ProductExtractor(adb)
    results = []

    # 当前页面已处理的商品数
    current_page_processed = 0

    for i in range(num_products):
        # 计算当前商品在可见区域的位置索引
        visible_index = current_page_processed

        # 如果已经处理完当前页的4个商品，需要翻页
        if visible_index >= PRODUCTS_PER_PAGE:
            print(f"\n📜 翻页: 已处理 {current_page_processed} 个商品，滑动加载更多...")
            adb.swipe_up_list(delay=2.0)
            current_page_processed = 0
            visible_index = 0

        try:
            info = extract_single_product(
                adb, extractor, evidence, i, visible_index,
                enable_report=enable_report, keyword=keyword,
                debug=debug
            )
            if info:
                results.append(info)
                current_page_processed += 1
        except Exception as e:
            print(f"\n❌ 提取商品 {i + 1} 时出错: {e}")
            import traceback
            traceback.print_exc()
            adb.back(delay=1.5)
            current_page_processed += 1

        if i < num_products - 1:
            time.sleep(1)

    # 保存报告
    evidence.save_report()

    # 输出总结
    print("\n" + "=" * 60)
    print("检测结果总结")
    print("=" * 60)

    # 统计举报结果
    reported_count = sum(1 for info in results if info.get("reported", False))

    print(f"\n成功检测 {len(results)}/{num_products} 个商品:\n")

    for info in results:
        print(f"[{info['index']}] {info['title'] or '未知标题'}")
        print(f"    店铺: {info['shop_name']}")
        print(f"    价格: ¥{info['price'] or '未提取到'}")
        if enable_report:
            status = '✅ 已举报' if info.get('reported') else '❌ 未举报'
            print(f"    举报: {status}")
        print()

    print(f"📁 证据目录: {evidence.evidence_dir}")
    print(f"   - 共 {len(evidence.shops)} 个店铺文件夹")
    print(f"   - 每个店铺包含: 1_商品介绍.png + 2_店铺信息.png")
    print(f"   - 检测报告: report.json")

    if enable_report:
        print(f"\n📢 举报统计: {reported_count}/{len(results)} 个商品已举报")

    print("\n" + "=" * 60)
    print("检测完成")
    print("=" * 60)

    return results


def run_mock_report_test(keyword: str = SEARCH_KEYWORD):
    """
    Mock 举报流程测试 - 无需真实设备，测试举报流程逻辑

    用于调试和验证举报流程的各个步骤，不需要实际连接手机。
    """
    print("\n" + "=" * 60)
    print("Mock 举报流程测试")
    print("=" * 60)

    # 创建 Mock 数据
    mock_shop_name = "测试盗版店铺"
    mock_price = 29.9
    mock_product_index = 0

    print(f"\n模拟数据:")
    print(f"   搜索关键词: {keyword}")
    print(f"   店铺名称: {mock_shop_name}")
    print(f"   商品价格: ¥{mock_price}")

    # 测试官方店铺判断
    print("\n" + "-" * 40)
    print("测试1: 官方店铺判断")
    print("-" * 40)

    test_shops = [
        "方圆众合教育",
        "众合教育旗舰店",
        "某某盗版店",
        "众合法考官方旗舰店",
        "小明的店",
    ]

    for shop in test_shops:
        is_official = is_official_shop(shop, keyword)
        status = "✅ 官方" if is_official else "❌ 非官方"
        print(f"   {shop}: {status}")

    # 测试举报文本生成
    print("\n" + "-" * 40)
    print("测试2: 举报文本生成")
    print("-" * 40)

    report_text = generate_report_text(keyword, mock_shop_name, mock_price)
    print(f"生成的举报文本 ({len(report_text)} 字符):")
    print("-" * 30)
    print(report_text)
    print("-" * 30)

    # 检查字数限制
    if len(report_text) <= 200:
        print(f"✅ 字数符合要求 ({len(report_text)}/200)")
    else:
        print(f"⚠️ 字数超出限制 ({len(report_text)}/200)")

    # 测试 UI 元素定位逻辑（使用示例 XML）
    print("\n" + "-" * 40)
    print("测试3: UI 元素定位逻辑")
    print("-" * 40)

    # 模拟小红书举报页面的 UI XML
    mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<hierarchy rotation="0">
  <node class="android.widget.FrameLayout" bounds="[0,0][1080,2400]">
    <node class="android.widget.TextView" text="举报" bounds="[450,100][630,160]"/>
    <node class="android.widget.EditText" text="" bounds="[50,400][1030,700]" focusable="true"/>
    <node class="android.widget.TextView" text="0/200" bounds="[950,710][1030,750]"/>
    <node class="android.widget.TextView" text="图片证据" bounds="[50,800][200,850]"/>
    <node class="android.widget.ImageView" bounds="[50,860][150,960]" clickable="true"/>
    <node class="android.widget.Button" text="提交" bounds="[400,2200][680,2280]"/>
  </node>
</hierarchy>'''

    # 测试 EditText 查找
    node_pattern = r'<node[^>]*class="[^"]*EditText[^"]*"[^>]*/>'
    nodes = re.findall(node_pattern, mock_xml)
    print(f"   找到 EditText 元素: {len(nodes)} 个")

    for node in nodes:
        bounds_match = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if bounds_match:
            x1, y1, x2, y2 = map(int, bounds_match.groups())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            print(f"   位置: ({center_x}, {center_y}), 区域: [{x1},{y1}][{x2},{y2}]")

    # 测试提交按钮查找
    submit_pattern = r'text="提交"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
    match = re.search(submit_pattern, mock_xml)
    if match:
        x1, y1, x2, y2 = map(int, match.groups())
        print(f"   找到提交按钮: ({(x1+x2)//2}, {(y1+y2)//2})")
    else:
        print("   未找到提交按钮")

    print("\n" + "=" * 60)
    print("Mock 测试完成")
    print("=" * 60)


def run_debug_report_page(device_id: Optional[str] = None):
    """
    调试举报页面 - 保存当前页面的 UI XML 和截图

    使用方法:
    1. 手动将手机打开到小红书举报页面
    2. 运行此函数
    3. 查看 test/debug/ 目录下的文件
    """
    print("\n" + "=" * 60)
    print("调试举报页面 - 保存 UI 信息")
    print("=" * 60)

    # 初始化 ADB
    adb = ADBController(device_id=device_id)

    if not adb.check_connection():
        print("\n❌ 无法连接设备")
        return

    print("\n请确保手机当前显示的是小红书举报页面...")
    print("按 Enter 继续...")
    input()

    # 保存调试信息
    result = adb.debug_dump_ui(prefix="report_page_debug")

    print("\n" + "-" * 40)
    print("保存的文件:")
    print("-" * 40)
    if result["xml_path"]:
        print(f"   UI XML: {result['xml_path']}")
    if result["screenshot_path"]:
        print(f"   截图: {result['screenshot_path']}")

    # 分析找到的元素
    if result["elements"]:
        print(f"\n找到 {len(result['elements'])} 个有意义的元素:")
        for i, elem in enumerate(result["elements"][:10]):  # 只显示前10个
            text = elem.get("text", "")[:30]
            cls = elem.get("class", "").split(".")[-1]
            bounds = elem.get("bounds", "")
            print(f"   [{i}] {cls}: '{text}' {bounds}")

    # 查找输入框
    print("\n" + "-" * 40)
    print("查找输入框元素:")
    print("-" * 40)
    input_elements = adb.find_input_elements()
    if input_elements:
        for i, elem in enumerate(input_elements):
            print(f"   [{i}] 中心: {elem['center']}, 面积: {elem['area']}")
    else:
        print("   未找到输入框元素")

    print("\n" + "=" * 60)
    print("调试完成 - 请查看 test/debug/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="盗版检测 - 小红书商品信息提取")
    parser.add_argument("-n", "--num", type=int, default=3,
                        help="要检测的商品数量 (默认: 3)")
    parser.add_argument("-k", "--keyword", type=str, default=SEARCH_KEYWORD,
                        help=f"搜索关键词 (默认: {SEARCH_KEYWORD})")
    parser.add_argument("--device", type=str, help="指定设备 ID")
    parser.add_argument("--report", action="store_true",
                        help="启用自动举报功能（截图完成后自动举报）")
    parser.add_argument("--debug", action="store_true",
                        help="启用调试模式（保存 UI XML 和截图用于分析）")
    parser.add_argument("--mock", action="store_true",
                        help="运行 Mock 测试（无需真实设备，测试举报流程逻辑）")
    parser.add_argument("--debug-report-page", action="store_true",
                        help="调试举报页面（保存当前页面 UI 信息）")

    args = parser.parse_args()

    # Mock 测试模式
    if args.mock:
        run_mock_report_test(keyword=args.keyword)
    # 调试举报页面模式
    elif args.debug_report_page:
        run_debug_report_page(device_id=args.device)
    # 正常检测模式
    else:
        run_detection(
            num_products=args.num,
            keyword=args.keyword,
            enable_report=args.report,
            debug=args.debug
        )
