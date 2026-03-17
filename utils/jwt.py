# JWT工具
# 生成和验证JWT令牌

import jwt
from datetime import datetime, timedelta
from backend.config import current_config

def generate_token(user_id: int, role: str) -> str:
    """
    生成JWT令牌
    :param user_id: 用户ID
    :param role: 用户角色
    :return: JWT令牌
    """
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24),  # 令牌有效期24小时
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, current_config.JWT_SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str) -> dict:
    """
    验证JWT令牌
    :param token: JWT令牌
    :return: 令牌负载
    """
    try:
        payload = jwt.decode(token, current_config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("令牌已过期")
    except jwt.InvalidTokenError:
        raise Exception("无效的令牌")
