# 设备模型
# 包含设备相关的字段和方法

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
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
    __tablename__ = 'devices'
    
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    device_id = Column(String(50), unique=True, nullable=False)
    type = Column(SQLEnum(DeviceType), nullable=False)
    status = Column(SQLEnum(DeviceStatus), nullable=False, default=DeviceStatus.OFFLINE)
    production_line_id = Column(Integer, ForeignKey('production_lines.id'), nullable=True)
    ip_address = Column(String(50))
    firmware_version = Column(String(50))
    is_active = Column(Boolean, default=True)
    
    # 关系
    production_line = relationship('ProductionLine', back_populates='devices')
    
    def to_dict(self):
        """将模型转换为字典"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'device_id': self.device_id,
            'type': self.type.value,
            'status': self.status.value,
            'production_line_id': self.production_line_id,
            'ip_address': self.ip_address,
            'firmware_version': self.firmware_version,
            'is_active': self.is_active
        })
        return data
