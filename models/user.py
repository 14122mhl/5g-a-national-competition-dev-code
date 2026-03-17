# 用户模型
# 包含用户相关的字段和方法

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"  # 管理员
    OPERATOR = "operator"  # 操作员
    VIEWER = "viewer"  # 查看者

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    
    # 关系
    orders = relationship('Order', back_populates='user')
    
    def to_dict(self):
        """将模型转换为字典"""
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value,
            'is_active': self.is_active
        })
        return data
