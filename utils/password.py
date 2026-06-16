# 密码处理工具
# 处理密码的哈希和验证

def hash_password(password: str) -> str:
    """
    对密码进行哈希处理
    :param password: 原始密码
    :return: 哈希后的密码
    """
    # 模拟密码哈希，实际项目中应使用passlib
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    :param plain_password: 原始密码
    :param hashed_password: 哈希后的密码
    :return: 验证结果
    """
    # 模拟密码验证，实际项目中应使用passlib
    return hashed_password == f"hashed_{plain_password}"
