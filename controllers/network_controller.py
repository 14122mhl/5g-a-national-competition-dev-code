from flask import Blueprint, request
from backend.services.network_service import NetworkService
from backend.utils.response import success_response, error_response
from backend.middleware.auth import require_auth, require_role

network_bp = Blueprint('network', __name__)
network_service = NetworkService()

@network_bp.route('/network/status', methods=['GET'])
@require_auth
def get_network_status():
    """获取网络状态"""
    try:
        status = network_service.get_network_status()
        return success_response(status)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/devices', methods=['GET'])
@require_auth
@require_role(['admin', 'network'])
def get_network_devices():
    """获取网络设备列表"""
    try:
        devices = network_service.get_network_devices()
        return success_response(devices)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/performance', methods=['GET'])
@require_auth
def get_network_performance():
    """获取网络性能数据"""
    try:
        performance = network_service.get_network_performance()
        return success_response(performance)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/optimize', methods=['POST'])
@require_auth
@require_role(['admin', 'network'])
def optimize_network():
    """网络优化"""
    try:
        data = request.json
        result = network_service.optimize_network(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/simulate', methods=['POST'])
@require_auth
@require_role(['admin', 'network'])
def simulate_network():
    """网络模拟"""
    try:
        data = request.json
        result = network_service.simulate_network_conditions(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)