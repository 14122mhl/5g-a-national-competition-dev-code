# 生产线模型
# 包含生产线相关的字段和方法

import enum
from .base import BaseModel

class ProductionLineStatus(enum.Enum):
    """生产线状态枚举"""
    RUNNING = "running"  # 运行中
    STOPPED = "stopped"  # 已停止
    MAINTENANCE = "maintenance"  # 维护中

class ProductionLine(BaseModel):
    """生产线模型"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.code = kwargs.get('code')
        self.status = kwargs.get('status', ProductionLineStatus.STOPPED)
        self.is_active = kwargs.get('is_active', True)
        self.devices = kwargs.get('devices', [])
    
    def to_dict(self):
        """将模型转换为字典"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'status': self.status.value,
            'is_active': self.is_active
        })
        return data
