# 产品模型
# 包含产品相关的字段和方法

import enum
from .base import BaseModel

class ProductStatus(enum.Enum):
    """产品状态枚举"""
    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃

class Product(BaseModel):
    """产品模型"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.sku = kwargs.get('sku')
        self.price = kwargs.get('price', 0.0)
        self.cost = kwargs.get('cost', 0.0)
        self.quantity = kwargs.get('quantity', 0)
        self.status = kwargs.get('status', ProductStatus.ACTIVE)
        self.order_items = []
    
    def to_dict(self):
        """将模型转换为字典"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'price': self.price,
            'cost': self.cost,
            'quantity': self.quantity,
            'status': self.status.value
        })
        return data
