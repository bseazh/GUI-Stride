#!/usr/bin/env python3
"""
WebSocket API 服务器

功能：
1. 提供 WebSocket 实时日志推送
2. 提供 HTTP API 获取检测状态
3. 将 test_detection.py 的输出实时传输到前端

启动方式:
    cd /Users/Apple/Documents/GUI/anti_piracy_system
    source venv/bin/activate
    python api_server.py

前端连接:
    WebSocket: ws://localhost:8766
    HTTP API: http://localhost:8765/api/...
"""

import asyncio
import json
import sys
import os
import subprocess
import threading
import queue
from datetime import datetime
from typing import Any, Dict, List, Set, Optional, Tuple, Union

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import websockets
except ImportError:
    print("请安装 websockets: pip install websockets")
    sys.exit(1)

try:
    from aiohttp import web
except ImportError:
    print("请安装 aiohttp: pip install aiohttp")
    sys.exit(1)


# 全局状态
connected_clients: Set = set()
log_queue: queue.Queue = queue.Queue()
detection_process: Optional[subprocess.Popen] = None
is_running: bool = False
stop_event = threading.Event()


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
    return default


def _as_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed


def _as_str(value: Any, default: str) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else default
    return str(value)


def _parse_keywords(params: Dict[str, Any], fallback_keyword: str) -> List[str]:
    keywords: List[str] = []

    raw_keywords = params.get("keywords")
    if isinstance(raw_keywords, list):
        for item in raw_keywords:
            if isinstance(item, str) and item.strip():
                keywords.append(item.strip())

    if not keywords:
        keyword = _as_str(params.get("keyword"), fallback_keyword)
        keywords = [keyword]

    # 去重但保持顺序
    seen: Set[str] = set()
    deduped: List[str] = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            deduped.append(kw)
    return deduped


def _parse_device_id(params: Dict[str, Any]) -> Optional[str]:
    raw = params.get("device")
    if isinstance(raw, str):
        cleaned = raw.strip()
        return cleaned or None
    if isinstance(raw, list) and raw:
        first = raw[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
    return None


def list_adb_devices(timeout_s: int = 10) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    列出本机通过 ADB 连接的设备。

    Returns:
        (devices, error) - error 为 None 表示成功
    """
    try:
        result = subprocess.run(
            ["adb", "devices", "-l"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except FileNotFoundError:
        return [], "未找到 adb 命令，请先安装 Android Platform Tools 并加入 PATH"
    except subprocess.TimeoutExpired:
        return [], "执行 adb devices 超时"
    except Exception as e:
        return [], f"执行 adb devices 失败: {e}"

    lines = result.stdout.strip().split("\n")
    if not lines:
        return [], "adb 输出为空"

    devices: List[Dict[str, Any]] = []
    for line in lines[1:]:
        if not line.strip():
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        device_id, state = parts[0], parts[1]
        model = None
        for part in parts[2:]:
            if part.startswith("model:"):
                model = part.split("model:", 1)[1]
                break

        devices.append(
            {
                "id": device_id,
                "state": state,
                "status": "online" if state == "device" else "offline",
                "model": model,
            }
        )

    return devices, None


class LogBroadcaster:
    """日志广播器 - 将日志发送到所有连接的客户端"""

    @staticmethod
    async def broadcast(message: dict):
        """广播消息到所有客户端"""
        if connected_clients:
            message_str = json.dumps(message, ensure_ascii=False)
            await asyncio.gather(
                *[client.send(message_str) for client in connected_clients],
                return_exceptions=True
            )

    @staticmethod
    def create_log_entry(message: str, log_type: str = "info") -> dict:
        """创建日志条目"""
        return {
            "id": str(datetime.now().timestamp()),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": log_type,  # info, action, performance
            "message": message
        }


async def websocket_handler(websocket):
    """WebSocket 连接处理器"""
    connected_clients.add(websocket)
    client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
    print(f"[WS] 新客户端连接: {client_ip}, 当前连接数: {len(connected_clients)}")

    # 发送欢迎消息
    welcome = LogBroadcaster.create_log_entry(
        "已连接到 GUI-Stride 后端服务", "info"
    )
    await websocket.send(json.dumps(welcome, ensure_ascii=False))

    try:
        async for message in websocket:
            # 处理来自前端的命令
            try:
                data = json.loads(message)
                command = data.get("command")

                if command == "start_detection":
                    # 启动检测
                    params = data.get("params", {})
                    asyncio.create_task(start_detection(params))

                elif command == "stop_detection":
                    # 停止检测
                    stop_detection()

                elif command == "ping":
                    # 心跳响应
                    await websocket.send(json.dumps({"type": "pong"}))

            except json.JSONDecodeError:
                pass

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"[WS] 客户端断开: {client_ip}, 当前连接数: {len(connected_clients)}")


async def start_detection(params: dict):
    """启动检测任务"""
    global detection_process, is_running

    if is_running:
        await LogBroadcaster.broadcast(
            LogBroadcaster.create_log_entry("检测任务正在运行中...", "performance")
        )
        return

    is_running = True
    stop_event.clear()

    script_path = os.path.join("test", "test_detection.py")
    cmd: List[str] = [sys.executable, script_path, "-n", "3", "--report"]
    cmd_human = f"python {script_path} -n 3 --report"

    await LogBroadcaster.broadcast(
        LogBroadcaster.create_log_entry(
            f"[EXE] 启动检测: {cmd_human}",
            "action"
        )
    )

    # 在后台线程运行检测
    def run_detection():
        global detection_process, is_running
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env.setdefault("PYTHONIOENCODING", "utf-8")
            log_queue.put(f"[EXE] 启动: {cmd_human}")

            detection_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(__file__),
                env=env,
            )

            assert detection_process.stdout is not None
            for line in iter(detection_process.stdout.readline, ""):
                if stop_event.is_set():
                    try:
                        detection_process.terminate()
                    except Exception:
                        pass
                    break
                if line:
                    log_queue.put(line.rstrip("\n"))

            try:
                detection_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    detection_process.kill()
                except Exception:
                    pass
                detection_process.wait()

            return_code = detection_process.returncode
            detection_process = None
            log_queue.put(f"[EXE] 结束 (code={return_code})")
        except Exception as e:
            log_queue.put(f"[ERROR] 检测出错: {str(e)}")
        finally:
            is_running = False
            detection_process = None
            if stop_event.is_set():
                log_queue.put("[DONE] 检测任务已停止")
            else:
                log_queue.put("[DONE] 检测任务完成")

    thread = threading.Thread(target=run_detection, daemon=True)
    thread.start()


def stop_detection():
    """停止检测任务"""
    global detection_process

    stop_event.set()
    log_queue.put("[STOP] 已请求停止检测任务")

    if detection_process and detection_process.poll() is None:
        try:
            detection_process.terminate()
        except Exception:
            pass


async def log_consumer():
    """日志消费者 - 从队列读取日志并广播"""
    while True:
        try:
            # 非阻塞检查队列
            while not log_queue.empty():
                message = log_queue.get_nowait()

                # 解析日志类型
                log_type = "info"
                if "[EXE]" in message or "启动" in message:
                    log_type = "action"
                elif "❌" in message or "⚠️" in message or "ERROR" in message:
                    log_type = "performance"
                elif "✅" in message or "成功" in message:
                    log_type = "action"

                await LogBroadcaster.broadcast(
                    LogBroadcaster.create_log_entry(message, log_type)
                )
        except Exception as e:
            print(f"日志消费错误: {e}")

        await asyncio.sleep(0.1)


# HTTP API 路由
async def handle_status(request):
    """获取系统状态"""
    return web.json_response({
        "status": "stopping" if (is_running and stop_event.is_set()) else ("running" if is_running else "idle"),
        "connected_clients": len(connected_clients),
        "timestamp": datetime.now().isoformat()
    })


async def handle_devices(request):
    """列出 ADB 设备"""
    devices, error = list_adb_devices()
    payload: Dict[str, Any] = {
        "devices": devices,
        "timestamp": datetime.now().isoformat(),
    }
    if error:
        payload["error"] = error
    return web.json_response(payload)


async def handle_start(request):
    """启动检测 (HTTP API)"""
    try:
        data = await request.json()
    except:
        data = {}

    asyncio.create_task(start_detection(data))
    return web.json_response({"success": True, "message": "检测任务已启动"})


async def handle_stop(request):
    """停止检测 (HTTP API)"""
    stop_detection()
    return web.json_response({"success": True, "message": "检测任务已停止"})


async def handle_cors(request):
    """处理 CORS 预检请求"""
    return web.Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )


@web.middleware
async def cors_middleware(request, handler):
    """CORS 中间件"""
    if request.method == "OPTIONS":
        return await handle_cors(request)

    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


async def main():
    """主函数"""
    print("=" * 50)
    print("GUI-Stride 后端服务")
    print("=" * 50)

    # 启动日志消费者
    asyncio.create_task(log_consumer())

    # HTTP 服务器
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/api/status", handle_status)
    app.router.add_get("/api/devices", handle_devices)
    app.router.add_post("/api/start", handle_start)
    app.router.add_post("/api/stop", handle_stop)

    runner = web.AppRunner(app)
    await runner.setup()
    http_site = web.TCPSite(runner, "0.0.0.0", 8765)
    await http_site.start()
    print(f"HTTP API:    http://localhost:8765/api/status")

    # WebSocket 服务器
    ws_server = await websockets.serve(websocket_handler, "0.0.0.0", 8766)
    print(f"WebSocket:   ws://localhost:8766")

    print("=" * 50)
    print("服务已启动，等待连接...")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)

    # 保持运行
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务已停止")
