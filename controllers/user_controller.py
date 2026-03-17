# 用户控制器
# 处理用户相关的HTTP请求

from flask import request
from services.user_service import UserService
from utils.response import success_response, error_response
from middleware.auth import auth_required, role_required
from models.user import UserRole

class UserController:
    """用户控制器类"""
    
    def __init__(self):
        """初始化用户控制器"""
        self.user_service = UserService()
    
    def register(self):
        """
        注册新用户
        :return: 注册结果
        """
        try:
            data = request.get_json()
            user = self.user_service.create_user(data)
            return success_response(data=user, message="注册成功", status_code=201)
        except Exception as e:
            return error_response(message="注册失败", errors=str(e))
    
    def login(self):
        """
        用户登录
        :return: 登录结果
        """
        try:
            data = request.get_json()
            result = self.user_service.login(data['username'], data['password'])
            return success_response(data=result, message="登录成功")
        except Exception as e:
            return error_response(message="登录失败", errors=str(e))
    
    @auth_required
    def get_current_user(self):
        """
        获取当前用户信息
        :return: 当前用户信息
        """
        try:
            user = self.user_service.get_user_by_id(request.user_id)
            if not user:
                return error_response(message="用户不存在", status_code=404)
            return success_response(data=user, message="获取用户信息成功")
        except Exception as e:
            return error_response(message="获取用户信息失败", errors=str(e))
    
    @auth_required
    def update_current_user(self):
        """
        更新当前用户信息
        :return: 更新结果
        """
        try:
            data = request.get_json()
            user = self.user_service.update_user(request.user_id, data)
            if not user:
                return error_response(message="用户不存在", status_code=404)
            return success_response(data=user, message="更新用户信息成功")
        except Exception as e:
            return error_response(message="更新用户信息失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def get_all_users(self):
        """
        获取所有用户
        :return: 用户列表
        """
        try:
            users = self.user_service.get_all_users()
            return success_response(data=users, message="获取用户列表成功")
        except Exception as e:
            return error_response(message="获取用户列表失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def get_user_by_id(self, user_id):
        """
        根据ID获取用户
        :param user_id: 用户ID
        :return: 用户信息
        """
        try:
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return error_response(message="用户不存在", status_code=404)
            return success_response(data=user, message="获取用户信息成功")
        except Exception as e:
            return error_response(message="获取用户信息失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def create_user(self):
        """
        创建用户
        :return: 创建结果
        """
        try:
            data = request.get_json()
            user = self.user_service.create_user(data)
            return success_response(data=user, message="创建用户成功", status_code=201)
        except Exception as e:
            return error_response(message="创建用户失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def update_user(self, user_id):
        """
        更新用户
        :param user_id: 用户ID
        :return: 更新结果
        """
        try:
            data = request.get_json()
            user = self.user_service.update_user(user_id, data)
            if not user:
                return error_response(message="用户不存在", status_code=404)
            return success_response(data=user, message="更新用户信息成功")
        except Exception as e:
            return error_response(message="更新用户信息失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def delete_user(self, user_id):
        """
        删除用户
        :param user_id: 用户ID
        :return: 删除结果
        """
        try:
            success = self.user_service.delete_user(user_id)
            if not success:
                return error_response(message="用户不存在", status_code=404)
            return success_response(message="删除用户成功")
        except Exception as e:
            return error_response(message="删除用户失败", errors=str(e))
