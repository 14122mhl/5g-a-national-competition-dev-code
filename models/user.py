# 用户模型
# 包含用户相关的字段和方法

import enum
from .base import BaseModel

class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"  # 管理员
    OPERATOR = "operator"  # 操作员
    VIEWER = "viewer"  # 查看者

class User(BaseModel):
    """用户模型"""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.password_hash = kwargs.get('password_hash')
        self.email = kwargs.get('email')
        self.full_name = kwargs.get('full_name')
        self.role = kwargs.get('role', UserRole.VIEWER)
        self.is_active = kwargs.get('is_active', True)
        self.orders = []
    
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
