# ============================================
# 单元测试 - 使用单一测试类避免Flask应用锁定
# SQLite内存数据库，完全隔离于MySQL
# ============================================

import unittest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from utils.password import hash_password, verify_password
from utils.jwt import generate_token, verify_token


def setup_test_db():
    """初始化测试数据库：SQLite内存模式"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.pop('SQLALCHEMY_ENGINE_OPTIONS', None)
    try:
        db.init_app(app)
    except RuntimeError:
        app.extensions.pop('sqlalchemy', None)
        db.init_app(app)
    with app.app_context():
        db.create_all()


class TestAll(unittest.TestCase):
    """所有API测试统一到一个类中"""

    @classmethod
    def setUpClass(cls):
        setup_test_db()
        cls.client = app.test_client()

    # ---- 密码工具 ----
    def test_hash_password(self):
        hashed = hash_password("test123")
        self.assertIsNotNone(hashed)
        self.assertNotEqual(hashed, "test123")
        self.assertTrue(hashed.startswith("pbkdf2:sha256"))

    def test_verify_password(self):
        hashed = hash_password("test123")
        self.assertTrue(verify_password("test123", hashed))
        self.assertFalse(verify_password("wrong", hashed))

    # ---- JWT ----
    def test_generate_token(self):
        token = generate_token(1, "admin")
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_verify_token(self):
        token = generate_token(1, "admin")
        payload = verify_token(token)
        self.assertEqual(payload["user_id"], 1)
        self.assertEqual(payload["role"], "admin")

    def test_invalid_token(self):
        with self.assertRaises(Exception):
            verify_token("invalid.token.here")

    # ---- 健康检查 ----
    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], '3.0.0')

    # ---- 用户API ----
    def test_create_user(self):
        response = self.client.post('/api/users', json={
            "username": "testuser", "password": "test123",
            "email": "test@test.com", "full_name": "测试用户", "role": "operator"
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['username'], 'testuser')

    def test_get_users(self):
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['data'], list)

    def test_login_success(self):
        self.client.post('/api/users', json={
            "username": "loginuser", "password": "pass123",
            "email": "login@test.com", "full_name": "登录测试", "role": "admin"
        })
        response = self.client.post('/api/auth/login', json={
            "username": "loginuser", "password": "pass123"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('token', data['data'])

    def test_login_fail(self):
        response = self.client.post('/api/auth/login', json={
            "username": "nonexistent", "password": "wrong"
        })
        self.assertEqual(response.status_code, 401)

    # ---- 产品API ----
    def test_create_product(self):
        response = self.client.post('/api/products', json={
            "name": "测试传感器", "sku": "TEST-001", "category": "传感器",
            "price": 199.99, "quantity": 100, "description": "测试产品"
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], '测试传感器')

    def test_get_products(self):
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_duplicate_sku(self):
        self.client.post('/api/products', json={
            "name": "产品A", "sku": "DUP-001", "category": "传感器",
            "price": 100, "quantity": 10
        })
        response = self.client.post('/api/products', json={
            "name": "产品B", "sku": "DUP-001", "category": "传感器",
            "price": 200, "quantity": 20
        })
        self.assertEqual(response.status_code, 400)

    # ---- 订单API ----
    def test_create_order(self):
        with app.app_context():
            from models.db_models import User, Product
            user = User(username='orderuser', password_hash=hash_password('pass'),
                        email='order@test.com', full_name='订单用户', role='admin')
            product = Product(name='订单产品', sku='ORD-001', category='传感器',
                              price=99.99, quantity=50)
            db.session.add(user)
            db.session.add(product)
            db.session.commit()

        response = self.client.post('/api/orders', json={
            "user_id": 1, "items": [{"product_id": 1, "quantity": 2}]
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertAlmostEqual(data['data']['total_amount'], 199.98, places=2)

    def test_get_orders(self):
        response = self.client.get('/api/orders')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_insufficient_stock(self):
        pid = None
        with app.app_context():
            from models.db_models import Product
            product = Product(name='库存产品', sku='STK-001', category='传感器',
                              price=50, quantity=5)
            db.session.add(product)
            db.session.commit()
            pid = product.id

        response = self.client.post('/api/orders', json={
            "user_id": 1, "items": [{"product_id": pid, "quantity": 9999}]
        })
        self.assertEqual(response.status_code, 400)

    # ---- 生产线API ----
    def test_create_line(self):
        response = self.client.post('/api/production/lines', json={
            "name": "测试产线", "code": "TEST-L01", "category": "assembly",
            "capacity": 100, "location": "车间A"
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_get_lines(self):
        response = self.client.get('/api/production/lines')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_production_stats(self):
        response = self.client.get('/api/production/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    # ---- 设备API ----
    def test_create_device(self):
        response = self.client.post('/api/devices', json={
            "name": "测试设备", "code": "DEV-T01", "type": "sensor",
            "ip_address": "192.168.1.100"
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_get_devices(self):
        response = self.client.get('/api/devices')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    # ---- 仿真调度API（数据库驱动） ----
    def test_simulation_run_with_db_tasks(self):
        """验证仿真API从数据库获取AGV任务"""
        with app.app_context():
            from models.db_models import AGVTask, ProductionLine, NetworkSlice
            zone = ProductionLine(name='仿真测试区', code='SIM-Z01', category='warehouse', status='active')
            db.session.add(zone)
            db.session.flush()
            task = AGVTask(
                task_no='SIM-TEST-001', task_type='transport',
                source_zone_id=zone.id, target_zone_id=zone.id,
                priority=2, latency_requirement_ms=10.0, weight_kg=25.0,
                status='pending'
            )
            db.session.add(task)
            db.session.commit()

        response = self.client.post('/api/simulation/run', json={
            "scenario": "medium", "slice_type": "industrial"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('ai_report', data['data'])
        self.assertIn('schedule', data['data'])

    def test_simulation_invalid_scenario(self):
        response = self.client.post('/api/simulation/run', json={
            "scenario": "invalid", "slice_type": "industrial"
        })
        self.assertEqual(response.status_code, 400)

    # ---- 需求预测API（数据库驱动） ----
    def test_demand_prediction(self):
        response = self.client.post('/api/prediction/demand', json={
            "product_type": "sensor", "horizon": 7
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('historical', data['data'])
        self.assertIn('forecast', data['data'])
        self.assertEqual(len(data['data']['forecast']), 7)

    # ---- AGV任务管理API ----
    def test_get_agv_tasks(self):
        response = self.client.get('/api/agv/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)

    def test_get_agv_tasks_filtered(self):
        response = self.client.get('/api/agv/tasks?status=pending&priority=2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_get_agv_task_by_id(self):
        with app.app_context():
            from models.db_models import AGVTask, ProductionLine
            zone = ProductionLine(name='AGV测试区', code='AGV-Z01', category='warehouse', status='active')
            db.session.add(zone)
            db.session.flush()
            task = AGVTask(
                task_no='AGV-DETAIL-001', task_type='transport',
                source_zone_id=zone.id, target_zone_id=zone.id,
                priority=1, latency_requirement_ms=5.0, weight_kg=15.0,
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = self.client.get(f'/api/agv/tasks/{task_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['task_no'], 'AGV-DETAIL-001')

    def test_update_agv_task_status(self):
        with app.app_context():
            from models.db_models import AGVTask, ProductionLine
            zone = ProductionLine(name='状态测试区', code='STS-Z01', category='warehouse', status='active')
            db.session.add(zone)
            db.session.flush()
            task = AGVTask(
                task_no='AGV-STATUS-001', task_type='transport',
                source_zone_id=zone.id, target_zone_id=zone.id,
                priority=3, latency_requirement_ms=15.0, weight_kg=30.0,
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = self.client.put(f'/api/agv/tasks/{task_id}/status', json={"status": "dispatched"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'dispatched')

    def test_agv_stats(self):
        response = self.client.get('/api/agv/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('by_status', data['data'])
        self.assertIn('by_type', data['data'])

    # ---- 网络负载事件API ----
    def test_get_network_events(self):
        response = self.client.get('/api/network/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)

    def test_get_network_events_filtered(self):
        response = self.client.get('/api/network/events?severity=critical')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    # ---- 仓库概览API ----
    def test_warehouse_overview(self):
        response = self.client.get('/api/warehouse/overview')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('agv_tasks', data['data'])
        self.assertIn('network_events', data['data'])
        self.assertIn('agv_devices', data['data'])
        self.assertIn('zones', data['data'])

    # ---- 数据库状态API（含新表） ----
    def test_db_status_with_warehouse_tables(self):
        response = self.client.get('/api/db/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        tables = data['data']['tables']
        self.assertIn('agv_tasks', tables)
        self.assertIn('network_load_events', tables)
        self.assertIn('sensing_metrics', tables)


if __name__ == '__main__':
    unittest.main(verbosity=2)