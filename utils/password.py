# 密码处理工具
# 处理密码的哈希和验证

from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    """
    对密码进行哈希处理
    :param password: 原始密码
    :return: 哈希后的密码
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    :param plain_password: 原始密码
    :param hashed_password: 哈希后的密码
    :return: 验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)
