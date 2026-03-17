# 响应格式化工具
# 格式化API响应

from flask import jsonify

def success_response(data=None, message="操作成功", status_code=200):
    """
    成功响应
    :param data: 响应数据
    :param message: 响应消息
    :param status_code: 状态码
    :return: 格式化的响应
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message="操作失败", status_code=400, errors=None):
    """
    错误响应
    :param message: 错误消息
    :param status_code: 状态码
    :param errors: 错误详情
    :return: 格式化的响应
    """
    response = {
        "success": False,
        "message": message,
        "errors": errors
    }
    return jsonify(response), status_code
