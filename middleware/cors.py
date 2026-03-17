# CORS中间件
# 处理跨域请求

from flask import request, make_response

def cors_middleware(f):
    """
    CORS中间件
    :param f: 被装饰的函数
    :return: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        # 执行请求处理函数
        response = f(*args, **kwargs)
        
        # 添加CORS头部
        if isinstance(response, tuple):
            # 对于返回值为元组的情况 (响应, 状态码)
            resp = make_response(response[0], response[1])
        else:
            # 对于返回值为响应对象的情况
            resp = make_response(response)
        
        # 添加CORS头部
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return resp
    return wrapper
