# 错误处理中间件
# 处理应用程序中的错误

from flask import jsonify
from utils.logger import logger

def error_handler(f):
    """
    错误处理装饰器
    :param f: 被装饰的函数
    :return: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # 记录错误日志
            logger.error(f"错误发生: {str(e)}", exc_info=True)
            
            # 返回错误响应
            return jsonify({
                "success": False,
                "message": "服务器内部错误",
                "errors": str(e)
            }), 500
    return wrapper
