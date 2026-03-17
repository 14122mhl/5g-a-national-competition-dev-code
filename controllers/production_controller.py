from flask import Blueprint, request
from services.production_service import ProductionService
from utils.response import success_response, error_response
from middleware.auth import require_auth, require_role

production_bp = Blueprint('production', __name__)
production_service = ProductionService()

@production_bp.route('/production-lines', methods=['GET'])
@require_auth
def get_production_lines():
    """获取所有生产线"""
    try:
        lines = production_service.get_all_production_lines()
        return success_response(lines)
    except Exception as e:
        return error_response(str(e), 500)

@production_bp.route('/production-lines/<int:line_id>', methods=['GET'])
@require_auth
def get_production_line(line_id):
    """获取单个生产线"""
    try:
        line = production_service.get_production_line_by_id(line_id)
        if not line:
            return error_response('生产线不存在', 404)
        return success_response(line)
    except Exception as e:
        return error_response(str(e), 500)

@production_bp.route('/production-lines', methods=['POST'])
@require_auth
@require_role(['admin'])
def create_production_line():
    """创建生产线"""
    try:
        data = request.json
        line = production_service.create_production_line(data)
        return success_response(line, 201)
    except Exception as e:
        return error_response(str(e), 500)

@production_bp.route('/production-lines/<int:line_id>/status', methods=['PUT'])
@require_auth
def update_production_line_status(line_id):
    """更新生产线状态"""
    try:
        data = request.json
        line = production_service.update_production_line_status(line_id, data['status'])
        if not line:
            return error_response('生产线不存在', 404)
        return success_response(line)
    except Exception as e:
        return error_response(str(e), 500)

@production_bp.route('/production-lines/<int:line_id>/maintenance', methods=['POST'])
@require_auth
@require_role(['admin', 'maintenance'])
def schedule_maintenance(line_id):
    """安排生产线维护"""
    try:
        data = request.json
        result = production_service.schedule_maintenance(line_id, data)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)