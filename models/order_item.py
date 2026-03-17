# 订单项模型
# 包含订单项相关的字段和方法

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class OrderItem(BaseModel):
    """订单项模型"""
    __tablename__ = 'order_items'
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # 关系
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')
    
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
