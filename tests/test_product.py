import unittest
from backend.services.product_service import ProductService

class TestProductService(unittest.TestCase):
    def setUp(self):
        self.product_service = ProductService()
    
    def test_get_all_products(self):
        """测试获取所有产品"""
        products = self.product_service.get_all_products()
        self.assertIsInstance(products, list)
    
    def test_get_product_by_id(self):
        """测试根据ID获取产品"""
        product = self.product_service.get_product_by_id(1)
        self.assertIsInstance(product, dict)
    
    def test_get_product_by_sku(self):
        """测试根据SKU获取产品"""
        product = self.product_service.get_product_by_sku('PROD-001')
        self.assertIsInstance(product, dict)
    
    def test_create_product(self):
        """测试创建产品"""
        product_data = {
            'name': '测试产品',
            'sku': 'TEST-001',
            'description': '测试产品描述',
            'price': 100.0,
            'stock': 100
        }
        product = self.product_service.create_product(product_data)
        self.assertIsInstance(product, dict)
    
    def test_update_product(self):
        """测试更新产品"""
        product_data = {
            'price': 150.0
        }
        product = self.product_service.update_product(1, product_data)
        self.assertIsInstance(product, dict)
    
    def test_delete_product(self):
        """测试删除产品"""
        result = self.product_service.delete_product(1)
        self.assertTrue(result)
    
    def test_update_stock(self):
        """测试更新库存"""
        result = self.product_service.update_stock(1, 50)
        self.assertIsInstance(result, dict)

if __name__ == '__main__':
    unittest.main()