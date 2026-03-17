# 产品控制器
# 处理产品相关的HTTP请求

from flask import request
from services.product_service import ProductService
from utils.response import success_response, error_response
from middleware.auth import auth_required, role_required
from models.user import UserRole

class ProductController:
    """产品控制器类"""
    
    def __init__(self):
        """初始化产品控制器"""
        self.product_service = ProductService()
    
    def get_all_products(self):
        """
        获取所有产品
        :return: 产品列表
        """
        try:
            status = request.args.get('status')
            products = self.product_service.get_all_products(status)
            return success_response(data=products, message="获取产品列表成功")
        except Exception as e:
            return error_response(message="获取产品列表失败", errors=str(e))
    
    def get_product_by_id(self, product_id):
        """
        根据ID获取产品
        :param product_id: 产品ID
        :return: 产品信息
        """
        try:
            product = self.product_service.get_product_by_id(product_id)
            if not product:
                return error_response(message="产品不存在", status_code=404)
            return success_response(data=product, message="获取产品信息成功")
        except Exception as e:
            return error_response(message="获取产品信息失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def create_product(self):
        """
        创建产品
        :return: 创建结果
        """
        try:
            data = request.get_json()
            product = self.product_service.create_product(data)
            return success_response(data=product, message="创建产品成功", status_code=201)
        except Exception as e:
            return error_response(message="创建产品失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def update_product(self, product_id):
        """
        更新产品
        :param product_id: 产品ID
        :return: 更新结果
        """
        try:
            data = request.get_json()
            product = self.product_service.update_product(product_id, data)
            if not product:
                return error_response(message="产品不存在", status_code=404)
            return success_response(data=product, message="更新产品信息成功")
        except Exception as e:
            return error_response(message="更新产品信息失败", errors=str(e))
    
    @auth_required
    @role_required(UserRole.ADMIN)
    def delete_product(self, product_id):
        """
        删除产品
        :param product_id: 产品ID
        :return: 删除结果
        """
        try:
            success = self.product_service.delete_product(product_id)
            if not success:
                return error_response(message="产品不存在", status_code=404)
            return success_response(message="删除产品成功")
        except Exception as e:
            return error_response(message="删除产品失败", errors=str(e))
    
    @auth_required
    def update_stock(self, product_id):
        """
        更新库存
        :param product_id: 产品ID
        :return: 更新结果
        """
        try:
            data = request.get_json()
            quantity_change = data.get('quantity_change', 0)
            new_quantity = self.product_service.update_stock(product_id, quantity_change)
            if new_quantity is None:
                return error_response(message="产品不存在", status_code=404)
            return success_response(data={"quantity": new_quantity}, message="更新库存成功")
        except Exception as e:
            return error_response(message="更新库存失败", errors=str(e))
