# 设备模型
# 包含设备相关的字段和方法

import enum
from .base import BaseModel

class DeviceType(enum.Enum):
    """设备类型枚举"""
    ROBOT = "robot"  # 机器人
    SENSOR = "sensor"  # 传感器
    CONTROLLER = "controller"  # 控制器
    CONVEYOR = "conveyor"  # 传送带

class DeviceStatus(enum.Enum):
    """设备状态枚举"""
    ONLINE = "online"  # 在线
    OFFLINE = "offline"  # 离线
    ERROR = "error"  # 错误
    MAINTENANCE = "maintenance"  # 维护中

class Device(BaseModel):
    """设备模型"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.device_id = kwargs.get('device_id')
        self.type = kwargs.get('type')
        self.status = kwargs.get('status', DeviceStatus.OFFLINE)
        self.production_line_id = kwargs.get('production_line_id')
        self.ip_address = kwargs.get('ip_address')
        self.firmware_version = kwargs.get('firmware_version')
        self.is_active = kwargs.get('is_active', True)
        self.production_line = kwargs.get('production_line')
    
    def to_dict(self):
        """将模型转换为字典"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'device_id': self.device_id,
            'type': self.type.value if self.type else None,
            'status': self.status.value,
            'production_line_id': self.production_line_id,
            'ip_address': self.ip_address,
            'firmware_version': self.firmware_version,
            'is_active': self.is_active
        })
        return data
