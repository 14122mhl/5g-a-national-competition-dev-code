# 日志中间件
# 记录请求和响应的日志

from flask import request, g
from utils.logger import logger
import time

def log_request(f):
    """
    日志记录装饰器
    :param f: 被装饰的函数
    :return: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"请求开始: {request.method} {request.path}")
        logger.debug(f"请求参数: {request.args}")
        if request.method in ['POST', 'PUT', 'PATCH']:
            logger.debug(f"请求体: {request.get_json()}")
        
        # 执行请求处理函数
        response = f(*args, **kwargs)
        
        # 计算请求处理时间
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        # 记录响应信息
        logger.info(f"请求结束: {request.method} {request.path} - 状态码: {response[1]} - 处理时间: {processing_time:.2f}ms")
        
        return response
    return wrapper
