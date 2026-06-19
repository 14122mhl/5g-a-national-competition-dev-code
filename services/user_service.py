# ============================================
# 用户服务 - 数据库版本
# ============================================

import logging
from database import db
from models.db_models import User
from utils.password import hash_password, verify_password
from utils.jwt import generate_token

logger = logging.getLogger(__name__)


class UserService:

    def get_all_users(self):
        users = User.query.all()
        return [u.to_dict() for u in users]

    def get_user_by_id(self, user_id):
        user = User.query.get(user_id)
        return user.to_dict() if user else None

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def create_user(self, data):
        if self.get_user_by_username(data['username']):
            raise Exception("用户名已存在")

        user = User(
            username=data['username'],
            password_hash=hash_password(data['password']),
            email=data['email'],
            full_name=data['full_name'],
            role=data.get('role', 'viewer')
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"创建用户: {user.username} (ID:{user.id})")
        return user.to_dict()

    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            return None

        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'password' in data:
            user.password_hash = hash_password(data['password'])

        db.session.commit()
        logger.info(f"更新用户: {user.username} (ID:{user_id})")
        return user.to_dict()

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return False
        db.session.delete(user)
        db.session.commit()
        logger.info(f"删除用户: {user.username} (ID:{user_id})")
        return True

    def login(self, username, password):
        user = self.get_user_by_username(username)
        if not user:
            raise Exception("用户名或密码错误")
        if not verify_password(password, user.password_hash):
            raise Exception("用户名或密码错误")
        if not user.is_active:
            raise Exception("用户已被禁用")

        token = generate_token(user.id, user.role)
        logger.info(f"用户登录成功: {username}")
        return {"token": token, "user": user.to_dict()}


user_service = UserService()