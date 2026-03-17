# 产品模型
# 包含产品相关的字段和方法

from sqlalchemy import Column, String, Float, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class ProductStatus(enum.Enum):
    """产品状态枚举"""
    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃

class Product(BaseModel):
    """产品模型"""
    __tablename__ = 'products'
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sku = Column(String(50), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    status = Column(SQLEnum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE)
    
    # 关系
    order_items = relationship('OrderItem', back_populates='product')
    
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
