# 用户服务
# 处理用户相关的业务逻辑

from backend.models.user import User, UserRole
from backend.utils.password import hash_password, verify_password
from backend.utils.jwt import generate_token
from backend.utils.logger import logger

class UserService:
    """用户服务类"""
    
    def __init__(self):
        """初始化用户服务"""
        self.users = []  # 内存缓存，实际生产环境使用PostgreSQL数据库
        # 添加默认管理员用户
        self._add_default_admin()
    
    def _add_default_admin(self):
        """添加默认管理员用户"""
        admin_user = User(
            id=1,
            username="admin",
            password_hash=hash_password("admin123"),
            email="admin@example.com",
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_active=True
        )
        self.users.append(admin_user)
    
    def get_all_users(self):
        """
        获取所有用户
        :return: 用户列表
        """
        logger.info("获取所有用户")
        return [user.to_dict() for user in self.users]
    
    def get_user_by_id(self, user_id):
        """
        根据ID获取用户
        :param user_id: 用户ID
        :return: 用户对象
        """
        logger.info(f"根据ID获取用户: {user_id}")
        for user in self.users:
            if user.id == user_id:
                return user.to_dict()
        return None
    
    def get_user_by_username(self, username):
        """
        根据用户名获取用户
        :param username: 用户名
        :return: 用户对象
        """
        logger.info(f"根据用户名获取用户: {username}")
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def create_user(self, data):
        """
        创建用户
        :param data: 用户数据
        :return: 创建的用户对象
        """
        logger.info(f"创建用户: {data['username']}")
        # 检查用户名是否已存在
        if self.get_user_by_username(data['username']):
            raise Exception("用户名已存在")
        
        # 创建新用户
        new_user = User(
            id=len(self.users) + 1,
            username=data['username'],
            password_hash=hash_password(data['password']),
            email=data['email'],
            full_name=data['full_name'],
            role=UserRole(data.get('role', 'viewer')),
            is_active=True
        )
        
        self.users.append(new_user)
        return new_user.to_dict()
    
    def update_user(self, user_id, data):
        """
        更新用户
        :param user_id: 用户ID
        :param data: 更新数据
        :return: 更新后的用户对象
        """
        logger.info(f"更新用户: {user_id}")
        for user in self.users:
            if user.id == user_id:
                # 更新用户信息
                if 'username' in data:
                    user.username = data['username']
                if 'email' in data:
                    user.email = data['email']
                if 'full_name' in data:
                    user.full_name = data['full_name']
                if 'role' in data:
                    user.role = UserRole(data['role'])
                if 'is_active' in data:
                    user.is_active = data['is_active']
                if 'password' in data:
                    user.password_hash = hash_password(data['password'])
                
                return user.to_dict()
        return None
    
    def delete_user(self, user_id):
        """
        删除用户
        :param user_id: 用户ID
        :return: 是否删除成功
        """
        logger.info(f"删除用户: {user_id}")
        for i, user in enumerate(self.users):
            if user.id == user_id:
                self.users.pop(i)
                return True
        return False
    
    def login(self, username, password):
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return: 登录结果
        """
        logger.info(f"用户登录: {username}")
        user = self.get_user_by_username(username)
        if not user:
            raise Exception("用户名或密码错误")
        
        if not verify_password(password, user.password_hash):
            raise Exception("用户名或密码错误")
        
        if not user.is_active:
            raise Exception("用户已被禁用")
        
        # 生成JWT令牌
        token = generate_token(user.id, user.role.value)
        
        return {
            "token": token,
            "user": user.to_dict()
        }
