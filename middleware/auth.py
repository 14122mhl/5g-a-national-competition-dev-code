# 认证中间件
# 处理用户认证和角色验证

from flask import request, jsonify
from utils.jwt import verify_token
from models.user import UserRole
import functools

def auth_required(f):
    """
    认证装饰器
    :param f: 被装饰的函数
    :return: 装饰后的函数
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                "success": False,
                "message": "未提供认证令牌",
                "errors": "Authorization header is required"
            }), 401
        
        try:
            token = auth_header.split(' ')[1]  # 提取Bearer令牌
            payload = verify_token(token)
            # 将用户信息存储到请求上下文中
            request.user_id = payload['user_id']
            request.user_role = payload['role']
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "认证失败",
                "errors": str(e)
            }), 401
    return wrapper

def role_required(required_role):
    """
    角色验证装饰器
    :param required_role: 所需角色
    :return: 装饰器
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'user_role'):
                return jsonify({
                    "success": False,
                    "message": "未认证",
                    "errors": "User not authenticated"
                }), 401
            
            # 检查角色是否匹配
            if request.user_role != required_role.value:
                return jsonify({
                    "success": False,
                    "message": "权限不足",
                    "errors": f"Required role: {required_role.value}"
                }), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator
