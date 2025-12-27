"""
任务管理器 - 负责执行巡查任务并捕获实时日志
"""

import sys
import io
import threading
import queue
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# 尝试导入反盗版系统模块
try:
    # 添加项目根目录到路径
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from anti_piracy_system.anti_piracy_agent import AntiPiracyAgent
    from anti_piracy_system.config_anti_piracy import SUPPORTED_PLATFORMS
    from phone_agent.model import ModelConfig
    ANTI_PIRACY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Anti-piracy modules not available: {e}")
    ANTI_PIRACY_AVAILABLE = False
    AntiPiracyAgent = None
    ModelConfig = None
    SUPPORTED_PLATFORMS = {}


class TaskLog:
    """任务日志管理器"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.logs: List[Dict[str, Any]] = []  # 日志条目列表
        self.log_lock = threading.Lock()
        self.log_buffer = io.StringIO()
        self.log_queue = queue.Queue()  # 用于实时推送日志

    def add_log(self, message: str, level: str = "info"):
        """添加日志条目"""
        log_entry = {
            "id": f"{self.task_id}_{len(self.logs)}",
            "timestamp": datetime.now().isoformat(),
            "timestamp_display": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message
        }

        with self.log_lock:
            self.logs.append(log_entry)
            # 限制日志数量，防止内存泄漏
            if len(self.logs) > 1000:
                self.logs = self.logs[-500:]

        # 放入队列供实时消费
        try:
            self.log_queue.put(log_entry, block=False)
        except queue.Full:
            pass  # 如果队列满，丢弃旧日志

    def get_logs(self, since_id: int = 0) -> List[Dict[str, Any]]:
        """获取日志（支持增量获取）"""
        with self.log_lock:
            if since_id >= len(self.logs):
                return []
            return self.logs[since_id:]

    def get_new_logs(self) -> List[Dict[str, Any]]:
        """获取新日志（非阻塞）"""
        new_logs = []
        while True:
            try:
                log_entry = self.log_queue.get_nowait()
                new_logs.append(log_entry)
            except queue.Empty:
                break
        return new_logs


class PatrolTask:
    """巡查任务"""

    def __init__(self, task_id: str, platform: str, keyword: str, max_items: int, test_mode: bool = True):
        self.task_id = task_id
        self.platform = platform
        self.keyword = keyword
        self.max_items = max_items
        self.test_mode = test_mode

        self.status = "pending"  # pending, running, completed, failed
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

        self.log_manager = TaskLog(task_id)
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """启动任务（在后台线程中）"""
        if self.status != "pending":
            return

        self.thread = threading.Thread(target=self._run_task, daemon=True)
        self.thread.start()

    def _run_task(self):
        """在后台线程中运行任务"""
        self.status = "running"
        self.start_time = datetime.now()

        try:
            # 添加启动日志
            self.log_manager.add_log(f"开始巡查任务: 平台={self.platform}, 关键词={self.keyword}, 最大检查数={self.max_items}, 测试模式={'是' if self.test_mode else '否'}", "info")

            if not ANTI_PIRACY_AVAILABLE:
                # 模拟模式：生成模拟日志和结果
                self.log_manager.add_log(f"⚠️ 反盗版系统模块不可用，运行模拟模式", "warning")
                self.log_manager.add_log(f"📱 模拟启动 {self.platform} 应用...", "info")
                self.log_manager.add_log(f"🔍 模拟搜索关键词: {self.keyword}", "info")

                import time
                # 模拟巡查过程
                for i in range(min(self.max_items, 10)):
                    time.sleep(0.5)
                    self.log_manager.add_log(f"📦 模拟检查第 {i+1} 个商品...", "info")
                    if i % 3 == 1:
                        self.log_manager.add_log(f"⚠️ 模拟发现疑似盗版商品: 价格异常", "warning")

                # 模拟结果
                result = {
                    "checked_count": min(self.max_items, 10),
                    "piracy_count": min(self.max_items, 10) // 3,
                    "reported_count": 0 if self.test_mode else min(self.max_items, 10) // 3
                }

                self.log_manager.add_log(f"✅ 模拟巡查完成", "info")

            else:
                # 真实模式：使用 AntiPiracyAgent
                # 配置模型（使用默认值，可以从环境变量读取）
                model_config = ModelConfig(
                    base_url="http://localhost:8000/v1",  # 默认本地模型服务
                    model_name="autoglm-phone-9b",
                    api_key="EMPTY"
                )

                # 创建 Agent
                agent = AntiPiracyAgent(
                    model_config=model_config,
                    platform=self.platform,
                    test_mode=self.test_mode
                )

                # 重定向标准输出到日志捕获器
                import contextlib
                from io import StringIO

                class LogRedirector:
                    def __init__(self, log_manager):
                        self.log_manager = log_manager
                        self.buffer = StringIO()

                    def write(self, text):
                        self.buffer.write(text)
                        # 每次换行时记录日志
                        if text.endswith('\n'):
                            line = self.buffer.getvalue().strip()
                            if line:  # 忽略空行
                                self.log_manager.add_log(line, "info")
                            self.buffer.truncate(0)
                            self.buffer.seek(0)

                    def flush(self):
                        pass

                redirector = LogRedirector(self.log_manager)

                with contextlib.redirect_stdout(redirector), contextlib.redirect_stderr(redirector):
                    # 执行巡查
                    result = agent.start_patrol(
                        keyword=self.keyword,
                        max_items=self.max_items
                    )

            # 记录结果
            self.result = {
                "checked_count": result.get("checked_count", 0),
                "piracy_count": result.get("piracy_count", 0),
                "reported_count": result.get("reported_count", 0)
            }

            self.log_manager.add_log(f"巡查任务完成: 检查{self.result['checked_count']}个商品, 发现{self.result['piracy_count']}个疑似盗版, 举报{self.result['reported_count']}个", "info")
            self.status = "completed"

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.log_manager.add_log(f"巡查任务失败: {e}", "error")
            import traceback
            self.log_manager.add_log(traceback.format_exc(), "error")

        finally:
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
            self.log_manager.add_log(f"任务结束，耗时{duration:.1f}秒", "info")

    def get_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": self.result,
            "error": self.error,
            "log_count": len(self.log_manager.logs)
        }


class TaskManager:
    """全局任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, PatrolTask] = {}
        self.task_lock = threading.Lock()

    def create_task(self, platform: str, keyword: str, max_items: int, test_mode: bool = True) -> str:
        """创建新任务并返回任务ID"""
        task_id = f"patrol_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.tasks)}"

        task = PatrolTask(
            task_id=task_id,
            platform=platform,
            keyword=keyword,
            max_items=max_items,
            test_mode=test_mode
        )

        with self.task_lock:
            self.tasks[task_id] = task

        # 异步启动任务
        task.start()

        return task_id

    def get_task(self, task_id: str) -> Optional[PatrolTask]:
        """获取任务"""
        with self.task_lock:
            return self.tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.get_task(task_id)
        return task.get_status() if task else None

    def get_task_logs(self, task_id: str, since_id: int = 0) -> List[Dict[str, Any]]:
        """获取任务日志"""
        task = self.get_task(task_id)
        if not task:
            return []
        return task.log_manager.get_logs(since_id)

    def get_new_task_logs(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务新日志（实时）"""
        task = self.get_task(task_id)
        if not task:
            return []
        return task.log_manager.get_new_logs()


# 全局任务管理器实例
task_manager = TaskManager()