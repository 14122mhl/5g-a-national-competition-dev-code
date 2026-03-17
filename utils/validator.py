# 请求验证工具
# 验证请求数据

from flask import request, jsonify
from jsonschema import validate, ValidationError

def validate_request(schema):
    """
    验证请求数据
    :param schema: 验证模式
    :return: 验证结果
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "success": False,
                        "message": "请求数据不能为空",
                        "errors": "请求体为空"
                    }), 400
                validate(instance=data, schema=schema)
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({
                    "success": False,
                    "message": "请求数据验证失败",
                    "errors": str(e)
                }), 400
        return wrapper
    return decorator
