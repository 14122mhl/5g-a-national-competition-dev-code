import unittest
from backend.services.order_service import OrderService

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.order_service = OrderService()
    
    def test_get_all_orders(self):
        """测试获取所有订单"""
        orders = self.order_service.get_all_orders()
        self.assertIsInstance(orders, list)
    
    def test_get_order_by_id(self):
        """测试根据ID获取订单"""
        order = self.order_service.get_order_by_id(1)
        self.assertIsInstance(order, dict)
    
    def test_get_order_by_number(self):
        """测试根据订单号获取订单"""
        order = self.order_service.get_order_by_number('ORD-2024-0001')
        self.assertIsInstance(order, dict)
    
    def test_create_order(self):
        """测试创建订单"""
        order_data = {
            'user_id': 1,
            'items': [
                {'product_id': 1, 'quantity': 2},
                {'product_id': 2, 'quantity': 1}
            ],
            'total_amount': 300.0
        }
        order = self.order_service.create_order(order_data)
        self.assertIsInstance(order, dict)
    
    def test_update_order_status(self):
        """测试更新订单状态"""
        order = self.order_service.update_order_status(1, 'shipped')
        self.assertIsInstance(order, dict)
    
    def test_cancel_order(self):
        """测试取消订单"""
        order = self.order_service.cancel_order(1)
        self.assertIsInstance(order, dict)
    
    def test_get_user_orders(self):
        """测试获取用户订单"""
        orders = self.order_service.get_user_orders(1)
        self.assertIsInstance(orders, list)

if __name__ == '__main__':
    unittest.main()