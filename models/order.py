# 订单模型
# 包含订单相关的字段和方法

from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class OrderStatus(enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class Order(BaseModel):
    """订单模型"""
    __tablename__ = 'orders'
    
    order_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    
    # 关系
    user = relationship('User', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    
    def to_dict(self):
        """将模型转换为字典"""
        data = super().to_dict()
        data.update({
            'order_number': self.order_number,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'status': self.status.value
        })
        return data
