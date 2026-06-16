from flask import Blueprint, request
from services.ai_service import AIService
from utils.response import success_response, error_response
from middleware.auth import auth_required, role_required

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()

class AIController:
    """AI控制器类"""
    
    def __init__(self):
        """初始化AI控制器"""
        self.ai_service = AIService()

@ai_bp.route('/ai/schedule', methods=['POST'])
@auth_required
@role_required(['admin', 'production'])
def schedule_production():
    """生产调度优化"""
    try:
        data = request.json
        result = ai_service.optimize_production_schedule(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)

@ai_bp.route('/ai/predict', methods=['POST'])
@auth_required
def predict_demand():
    """需求预测"""
    try:
        data = request.json
        result = ai_service.predict_demand(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)

@ai_bp.route('/ai/quality', methods=['POST'])
@auth_required
def predict_quality():
    """质量预测"""
    try:
        data = request.json
        result = ai_service.predict_quality(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)

@ai_bp.route('/ai/maintenance', methods=['POST'])
@auth_required
@role_required(['admin', 'maintenance'])
def predict_maintenance():
    """设备维护预测"""
    try:
        data = request.json
        result = ai_service.predict_maintenance(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)

@ai_bp.route('/ai/energy', methods=['POST'])
@auth_required
def optimize_energy():
    """能源优化"""
    try:
        data = request.json
        result = ai_service.optimize_energy_consumption(data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)