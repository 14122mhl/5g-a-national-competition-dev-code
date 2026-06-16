# 订单模型
# 包含订单相关的字段和方法

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
    
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.order_number = kwargs.get('order_number')
        self.user_id = kwargs.get('user_id')
        self.total_amount = kwargs.get('total_amount', 0.0)
        self.status = kwargs.get('status', OrderStatus.PENDING)
        self.user = kwargs.get('user')
        self.order_items = kwargs.get('order_items', [])
    
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
