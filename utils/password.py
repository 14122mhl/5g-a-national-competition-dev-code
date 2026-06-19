# 密码处理工具
# 使用werkzeug进行密码哈希

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return check_password_hash(hashed_password, plain_password)