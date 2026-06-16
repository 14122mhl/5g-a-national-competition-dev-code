from flask import Blueprint, request
from services.device_service import DeviceService
from utils.response import success_response, error_response
from middleware.auth import auth_required, role_required

device_bp = Blueprint('device', __name__)
device_service = DeviceService()

class DeviceController:
    """设备控制器类"""
    
    def __init__(self):
        """初始化设备控制器"""
        self.device_service = DeviceService()

@device_bp.route('/devices', methods=['GET'])
@auth_required
def get_devices():
    """获取所有设备"""
    try:
        devices = device_service.get_all_devices()
        return success_response(devices)
    except Exception as e:
        return error_response(str(e), 500)

@device_bp.route('/devices/<int:device_id>', methods=['GET'])
@auth_required
def get_device(device_id):
    """获取单个设备"""
    try:
        device = device_service.get_device_by_id(device_id)
        if not device:
            return error_response('设备不存在', 404)
        return success_response(device)
    except Exception as e:
        return error_response(str(e), 500)

@device_bp.route('/devices', methods=['POST'])
@auth_required
@role_required(['admin'])
def create_device():
    """创建设备"""
    try:
        data = request.json
        device = device_service.create_device(data)
        return success_response(device, 201)
    except Exception as e:
        return error_response(str(e), 500)

@device_bp.route('/devices/<int:device_id>', methods=['PUT'])
@auth_required
@role_required(['admin', 'maintenance'])
def update_device(device_id):
    """更新设备信息"""
    try:
        data = request.json
        device = device_service.update_device(device_id, data)
        if not device:
            return error_response('设备不存在', 404)
        return success_response(device)
    except Exception as e:
        return error_response(str(e), 500)

@device_bp.route('/devices/<int:device_id>/status', methods=['PUT'])
@auth_required
def update_device_status(device_id):
    """更新设备状态"""
    try:
        data = request.json
        device = device_service.update_device_status(device_id, data['status'])
        if not device:
            return error_response('设备不存在', 404)
        return success_response(device)
    except Exception as e:
        return error_response(str(e), 500)

@device_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@auth_required
@role_required(['admin'])
def delete_device(device_id):
    """删除设备"""
    try:
        result = device_service.delete_device(device_id)
        if not result:
            return error_response('设备不存在', 404)
        return success_response({'message': '设备删除成功'})
    except Exception as e:
        return error_response(str(e), 500)