from flask import Blueprint, request
from services.network_service import NetworkService
from utils.response import success_response, error_response
from middleware.auth import auth_required, role_required

network_bp = Blueprint('network', __name__)
network_service = NetworkService()

class NetworkController:
    """网络控制器类"""
    
    def __init__(self):
        """初始化网络控制器"""
        self.network_service = NetworkService()

@network_bp.route('/network/status', methods=['GET'])
@auth_required
def get_network_status():
    """获取网络状态"""
    try:
        status = network_service.get_network_status()
        return success_response(status)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/devices', methods=['GET'])
@auth_required
@role_required(['admin', 'network'])
def get_network_devices():
    """获取网络设备列表"""
    try:
        devices = network_service.get_network_devices()
        return success_response(devices)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/performance', methods=['GET'])
@auth_required
def get_network_performance():
    """获取网络性能数据"""
    try:
        performance = network_service.get_network_performance()
        return success_response(performance)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/optimize', methods=['POST'])
@auth_required
@role_required(['admin', 'network'])
def optimize_network():
    """网络优化"""
    try:
        data = request.json
        result = network_service.optimize_network(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)

@network_bp.route('/network/simulate', methods=['POST'])
@auth_required
@role_required(['admin', 'network'])
def simulate_network():
    """网络模拟"""
    try:
        data = request.json
        result = network_service.simulate_network_conditions(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)