# 订单项模型
# 包含订单项相关的字段和方法

from .base import BaseModel

class OrderItem(BaseModel):
    """订单项模型"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.order_id = kwargs.get('order_id')
        self.product_id = kwargs.get('product_id')
        self.quantity = kwargs.get('quantity', 0)
        self.unit_price = kwargs.get('unit_price', 0.0)
        self.subtotal = kwargs.get('subtotal', 0.0)
        self.order = kwargs.get('order')
        self.product = kwargs.get('product')
    
    def to_dict(self):
        """将模型转换为字典"""
        data = super().to_dict()
        data.update({
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        })
        return data
