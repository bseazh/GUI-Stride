"""
系统配置路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import os

router = APIRouter()

# 数据模型
class DeviceStatus(BaseModel):
    connected: bool
    device_id: Optional[str] = None
    device_type: Optional[str] = None
    status_message: str

class PlatformInfo(BaseModel):
    key: str
    name: str
    description: str
    supported: bool

class SystemConfig(BaseModel):
    phone_agent_base_url: str
    phone_agent_model: str
    debug_mode: bool

# 支持的平台列表
SUPPORTED_PLATFORMS = {
    "xiaohongshu": {
        "name": "小红书",
        "description": "小红书电商平台",
        "supported": True
    },
    "xianyu": {
        "name": "闲鱼",
        "description": "闲鱼二手交易平台",
        "supported": True
    },
    "taobao": {
        "name": "淘宝",
        "description": "淘宝电商平台",
        "supported": True
    }
}

@router.get("/platforms", response_model=List[PlatformInfo])
async def get_supported_platforms():
    """获取支持的平台列表"""
    platforms = []
    for key, info in SUPPORTED_PLATFORMS.items():
        platforms.append(PlatformInfo(
            key=key,
            name=info["name"],
            description=info["description"],
            supported=info["supported"]
        ))
    return platforms

@router.get("/device/status", response_model=DeviceStatus)
async def get_device_status():
    """获取设备连接状态"""
    # TODO: 实现实际的设备状态检查
    # 这里先返回模拟数据
    device_id = os.getenv("DEFAULT_DEVICE_ID")
    if device_id:
        return DeviceStatus(
            connected=True,
            device_id=device_id,
            device_type=os.getenv("DEFAULT_DEVICE_TYPE", "adb"),
            status_message="设备已连接"
        )
    else:
        return DeviceStatus(
            connected=False,
            status_message="未检测到设备连接，请连接设备后刷新"
        )

@router.get("/system", response_model=SystemConfig)
async def get_system_config():
    """获取系统配置"""
    return SystemConfig(
        phone_agent_base_url=os.getenv("PHONE_AGENT_BASE_URL", ""),
        phone_agent_model=os.getenv("PHONE_AGENT_MODEL", ""),
        debug_mode=os.getenv("DEBUG", "false").lower() == "true"
    )