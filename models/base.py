# 基础模型类
# 所有模型的基类，包含共同的字段和方法

import datetime

# 模拟SQLAlchemy的基础模型
class BaseModel:
    """基础模型类"""
    
    def __init__(self):
        if not hasattr(self, 'id'):
            self.id = None
        if not hasattr(self, 'created_at'):
            self.created_at = datetime.datetime.now()
        if not hasattr(self, 'updated_at'):
            self.updated_at = datetime.datetime.now()
    
    def to_dict(self):
        """将模型转换为字典"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
