# JWT工具
import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')


def generate_token(user_id: int, role: str) -> str:
    """生成JWT令牌"""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    """验证JWT令牌"""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise Exception("令牌已过期")
    except jwt.InvalidTokenError:
        raise Exception("无效的令牌")