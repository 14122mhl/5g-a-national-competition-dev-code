# 生产线模型
# 包含生产线相关的字段和方法

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class ProductionLineStatus(enum.Enum):
    """生产线状态枚举"""
    RUNNING = "running"  # 运行中
    STOPPED = "stopped"  # 已停止
    MAINTENANCE = "maintenance"  # 维护中

class ProductionLine(BaseModel):
    """生产线模型"""
    __tablename__ = 'production_lines'
    
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    code = Column(String(50), unique=True, nullable=False)
    status = Column(SQLEnum(ProductionLineStatus), nullable=False, default=ProductionLineStatus.STOPPED)
    is_active = Column(Boolean, default=True)
    
    # 关系
    devices = relationship('Device', back_populates='production_line')
    
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
