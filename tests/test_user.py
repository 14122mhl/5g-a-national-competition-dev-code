import unittest
from backend.services.user_service import UserService

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()
    
    def test_get_all_users(self):
        """测试获取所有用户"""
        users = self.user_service.get_all_users()
        self.assertIsInstance(users, list)
    
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        user = self.user_service.get_user_by_id(1)
        self.assertIsInstance(user, dict)
    
    def test_get_user_by_username(self):
        """测试根据用户名获取用户"""
        user = self.user_service.get_user_by_username('admin')
        self.assertIsInstance(user, dict)
    
    def test_create_user(self):
        """测试创建用户"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'user'
        }
        user = self.user_service.create_user(user_data)
        self.assertIsInstance(user, dict)
    
    def test_update_user(self):
        """测试更新用户"""
        user_data = {
            'email': 'updated@example.com'
        }
        user = self.user_service.update_user(1, user_data)
        self.assertIsInstance(user, dict)
    
    def test_delete_user(self):
        """测试删除用户"""
        result = self.user_service.delete_user(1)
        self.assertTrue(result)
    
    def test_login(self):
        """测试用户登录"""
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        result = self.user_service.login(login_data)
        self.assertIsInstance(result, dict)
        self.assertIn('token', result)

if __name__ == '__main__':
    unittest.main()