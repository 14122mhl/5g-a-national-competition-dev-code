# 订单控制器
# 处理订单相关的HTTP请求

from flask import request, Blueprint
from services.order_service import OrderService
from utils.response import success_response, error_response
from middleware.auth import auth_required, role_required
from models.user import UserRole

class OrderController:
    """订单控制器类"""
    
    def __init__(self):
        """初始化订单控制器"""
        self.order_service = OrderService()
    
    @auth_required
    def get_all_orders(self):
        """
        获取所有订单
        :return: 订单列表
        """
        try:
            status = request.args.get('status')
            orders = self.order_service.get_all_orders(status)
            return success_response(data=orders, message="获取订单列表成功")
        except Exception as e:
            return error_response(message="获取订单列表失败", errors=str(e))
    
    @auth_required
    def get_order_by_id(self, order_id):
        """
        根据ID获取订单
        :param order_id: 订单ID
        :return: 订单信息
        """
        try:
            order = self.order_service.get_order_by_id(order_id)
            if not order:
                return error_response(message="订单不存在", status_code=404)
            return success_response(data=order, message="获取订单信息成功")
        except Exception as e:
            return error_response(message="获取订单信息失败", errors=str(e))
    
    @auth_required
    def get_order_by_number(self, order_number):
        """
        根据订单号获取订单
        :param order_number: 订单号
        :return: 订单信息
        """
        try:
            order = self.order_service.get_order_by_number(order_number)
            if not order:
                return error_response(message="订单不存在", status_code=404)
            return success_response(data=order, message="获取订单信息成功")
        except Exception as e:
            return error_response(message="获取订单信息失败", errors=str(e))
    
    @auth_required
    def create_order(self):
        """
        创建订单
        :return: 创建结果
        """
        try:
            data = request.get_json()
            order = self.order_service.create_order(request.user_id, data['items'])
            return success_response(data=order, message="创建订单成功", status_code=201)
        except Exception as e:
            return error_response(message="创建订单失败", errors=str(e))
    
    @auth_required
    def update_order_status(self, order_id):
        """
        更新订单状态
        :param order_id: 订单ID
        :return: 更新结果
        """
        try:
            data = request.get_json()
            order = self.order_service.update_order_status(order_id, data['status'])
            if not order:
                return error_response(message="订单不存在", status_code=404)
            return success_response(data=order, message="更新订单状态成功")
        except Exception as e:
            return error_response(message="更新订单状态失败", errors=str(e))
    
    @auth_required
    def cancel_order(self, order_id):
        """
        取消订单
        :param order_id: 订单ID
        :return: 取消结果
        """
        try:
            success = self.order_service.cancel_order(order_id)
            if not success:
                return error_response(message="订单不存在", status_code=404)
            return success_response(message="取消订单成功")
        except Exception as e:
            return error_response(message="取消订单失败", errors=str(e))

# 初始化蓝图和控制器实例
order_bp = Blueprint('order', __name__)
order_controller = OrderController()

# 路由注册
@order_bp.route('/', methods=['GET'])
def get_all_orders():
    return order_controller.get_all_orders()

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    return order_controller.get_order_by_id(order_id)

@order_bp.route('/number/<string:order_number>', methods=['GET'])
def get_order_by_number(order_number):
    return order_controller.get_order_by_number(order_number)

@order_bp.route('/', methods=['POST'])
def create_order():
    return order_controller.create_order()

@order_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    return order_controller.update_order_status(order_id)

@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    return order_controller.cancel_order(order_id)
