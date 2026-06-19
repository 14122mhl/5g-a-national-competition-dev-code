# ============================================
# 数据库种子数据脚本
# 插入初始数据用于系统功能测试和演示
# ============================================

import logging
from datetime import datetime, timedelta
import random
import math

from database import db
from models.db_models import (
    User, Product, Order, OrderItem, ProductionLine,
    Device, NetworkSlice, EdgeNode, SimulationRecord,
    AIAnalysisLog, SensingMetric, DashboardMetric
)
from utils.password import hash_password

logger = logging.getLogger(__name__)


def seed_all():
    """执行所有种子数据插入"""
    seed_users()
    seed_products()
    seed_production_lines()
    seed_devices()
    seed_network_slices()
    seed_edge_nodes()
    seed_sensing_data()
    seed_dashboard_metrics()
    db.session.commit()
    logger.info("所有种子数据已插入完成")


def seed_users():
    """插入默认用户"""
    if User.query.count() > 0:
        return

    users = [
        User(username='admin', password_hash=hash_password('admin123'),
             email='admin@5g-ai.com', full_name='系统管理员', role='admin'),
        User(username='operator', password_hash=hash_password('operator123'),
             email='operator@5g-ai.com', full_name='生产操作员', role='operator'),
        User(username='viewer', password_hash=hash_password('viewer123'),
             email='viewer@5g-ai.com', full_name='访客用户', role='viewer'),
        User(username='engineer', password_hash=hash_password('engineer123'),
             email='engineer@5g-ai.com', full_name='网络工程师', role='operator'),
    ]
    db.session.add_all(users)
    db.session.commit()
    logger.info(f"已创建 {len(users)} 个默认用户")


def seed_products():
    """插入默认产品"""
    if Product.query.count() > 0:
        return

    products = [
        Product(name='工业传感器模组', sku='SN-001', category='传感器', price=199.99,
                quantity=500, unit='套', description='高精度工业传感器模组，支持5G-A通信'),
        Product(name='智能机械臂控制器', sku='RB-002', category='控制器', price=9999.99,
                quantity=50, unit='台', description='6轴智能机械臂控制器，支持URLLC'),
        Product(name='5G-A通信模组', sku='5G-003', category='通信', price=1499.99,
                quantity=200, unit='套', description='5G-A确定性网络通信模组'),
        Product(name='边缘计算网关', sku='EG-004', category='网关', price=2999.99,
                quantity=80, unit='台', description='工业级边缘计算网关'),
        Product(name='工业AI视觉模块', sku='AI-005', category='视觉', price=4999.99,
                quantity=30, unit='套', description='基于大模型的工业视觉检测模块'),
        Product(name='产线协控模组', sku='LC-006', category='控制器', price=3499.99,
                quantity=60, unit='套', description='多设备协同控制模组'),
        Product(name='MEC边缘服务器', sku='ME-007', category='服务器', price=15999.99,
                quantity=15, unit='台', description='多接入边缘计算服务器'),
        Product(name='数字孪生引擎', sku='DT-008', category='软件', price=8999.99,
                quantity=100, unit='套', description='工业数字孪生仿真引擎'),
    ]
    db.session.add_all(products)
    db.session.commit()
    logger.info(f"已创建 {len(products)} 个默认产品")


def seed_production_lines():
    """插入生产线"""
    if ProductionLine.query.count() > 0:
        return

    lines = [
        ProductionLine(name='总装线A', code='PL-A01', category='assembly',
                       status='running', capacity=120, efficiency=95.5,
                       current_task='机械臂总装', location='车间A', oee=92.3),
        ProductionLine(name='加工线B', code='PL-B01', category='machining',
                       status='running', capacity=80, efficiency=88.0,
                       current_task='精密加工', location='车间B', oee=85.7),
        ProductionLine(name='包装线C', code='PL-C01', category='packaging',
                       status='idle', capacity=200, efficiency=98.0,
                       current_task=None, location='车间C', oee=96.5),
        ProductionLine(name='检测线D', code='PL-D01', category='testing',
                       status='running', capacity=60, efficiency=92.0,
                       current_task='AI视觉检测', location='车间D', oee=91.0),
        ProductionLine(name='加工线E', code='PL-E01', category='machining',
                       status='maintenance', capacity=75, efficiency=0,
                       current_task=None, location='车间B', oee=78.2),
    ]
    db.session.add_all(lines)
    db.session.commit()
    logger.info(f"已创建 {len(lines)} 条生产线")


def seed_devices():
    """插入设备"""
    if Device.query.count() > 0:
        return

    devices = [
        # 总装线A设备
        Device(name='机械臂-R01', code='RB-R01', type='robot', line_id=1,
               status='online', ip_address='192.168.10.11', firmware_version='v2.3.1'),
        Device(name='机械臂-R02', code='RB-R02', type='robot', line_id=1,
               status='online', ip_address='192.168.10.12', firmware_version='v2.3.1'),
        Device(name='视觉传感器-V01', code='SN-V01', type='sensor', line_id=1,
               status='online', ip_address='192.168.10.13', firmware_version='v1.8.0'),
        # 加工线B设备
        Device(name='CNC机床-C01', code='CN-C01', type='sensor', line_id=2,
               status='online', ip_address='192.168.10.21', firmware_version='v3.1.0'),
        Device(name='温度传感器-T01', code='SN-T01', type='sensor', line_id=2,
               status='online', ip_address='192.168.10.22', firmware_version='v1.5.0'),
        # 包装线C设备
        Device(name='传送带控制器-CV01', code='CV-C01', type='conveyor', line_id=3,
               status='offline', ip_address='192.168.10.31', firmware_version='v2.0.0'),
        # 检测线D设备
        Device(name='AI视觉相机-AI01', code='CM-AI01', type='camera', line_id=4,
               status='online', ip_address='192.168.10.41', firmware_version='v4.0.0'),
        Device(name='激光扫描仪-LS01', code='SN-LS01', type='sensor', line_id=4,
               status='online', ip_address='192.168.10.42', firmware_version='v2.2.0'),
    ]
    db.session.add_all(devices)
    db.session.commit()
    logger.info(f"已创建 {len(devices)} 个设备")


def seed_network_slices():
    """插入网络切片"""
    if NetworkSlice.query.count() > 0:
        return

    slices = [
        NetworkSlice(name='工业控制切片', slice_type='industrial', size=100,
                     description='用于工业生产控制的URLLC切片，保障超低时延',
                     status='active', latency=1.0, bandwidth=1000, sla_compliance=99.99),
        NetworkSlice(name='车联网切片', slice_type='vehicle', size=200,
                     description='智能交通车联网切片，支持V2X通信',
                     status='active', latency=5.0, bandwidth=500, sla_compliance=99.95),
        NetworkSlice(name='民生服务切片', slice_type='civil', size=150,
                     description='公共服务民生切片，保障基础通信需求',
                     status='active', latency=10.0, bandwidth=200, sla_compliance=99.90),
        NetworkSlice(name='智能仓储切片', slice_type='industrial', size=80,
                     description='AGV和仓储管理专用切片',
                     status='active', latency=2.0, bandwidth=800, sla_compliance=99.97),
    ]
    db.session.add_all(slices)
    db.session.commit()
    logger.info(f"已创建 {len(slices)} 个网络切片")


def seed_edge_nodes():
    """插入边缘节点"""
    if EdgeNode.query.count() > 0:
        return

    nodes = [
        EdgeNode(name='边缘节点-01', location='车间A', cpu=45.2, memory=62.1,
                 status='online', tasks=12, ip='192.168.10.101'),
        EdgeNode(name='边缘节点-02', location='车间B', cpu=32.8, memory=48.5,
                 status='online', tasks=8, ip='192.168.10.102'),
        EdgeNode(name='边缘节点-03', location='数据中心', cpu=78.5, memory=85.3,
                 status='online', tasks=25, ip='192.168.10.103'),
    ]
    db.session.add_all(nodes)
    db.session.commit()
    logger.info(f"已创建 {len(nodes)} 个边缘节点")


def seed_sensing_data():
    """插入感知指标历史数据"""
    if SensingMetric.query.count() > 0:
        return

    now = datetime.now()
    points = 7 * 24 * 12  # 7天，每5分钟一个点

    sensing_configs = {
        'temperature': {'precision': 99.5, 'distance': 500, 'refresh': 100},
        'person': {'precision': 99.0, 'distance': 300, 'refresh': 50},
        'device': {'precision': 99.5, 'distance': 400, 'refresh': 75},
        'environment': {'precision': 98.8, 'distance': 450, 'refresh': 80},
        'vibration': {'precision': 99.3, 'distance': 350, 'refresh': 120},
    }

    batch = []
    for sensor_type, cfg in sensing_configs.items():
        for i in range(points):
            ts = now - timedelta(minutes=(points - i) * 5)
            noise_p = random.gauss(0, 0.2)
            noise_d = random.gauss(0, 10)
            noise_r = random.gauss(0, 5)
            batch.append(SensingMetric(
                sensor_type=sensor_type, metric_name='precision',
                value=round(cfg['precision'] + noise_p, 2), unit='%', timestamp=ts
            ))
            batch.append(SensingMetric(
                sensor_type=sensor_type, metric_name='distance',
                value=round(cfg['distance'] + noise_d, 1), unit='m', timestamp=ts
            ))
            batch.append(SensingMetric(
                sensor_type=sensor_type, metric_name='refresh_rate',
                value=round(cfg['refresh'] + noise_r, 1), unit='Hz', timestamp=ts
            ))

    db.session.bulk_save_objects(batch)
    db.session.commit()
    logger.info(f"已创建 {len(batch)} 条感知指标数据")


def seed_dashboard_metrics():
    """插入仪表盘历史指标"""
    if DashboardMetric.query.count() > 0:
        return

    now = datetime.now()
    metrics = []
    for i in range(7 * 24 * 12):  # 7天
        ts = now - timedelta(minutes=(7 * 24 * 12 - i) * 5)
        metrics.append(DashboardMetric(
            air_peak_rate=f"{round(random.uniform(9.5, 10.5), 1)} Gbps",
            uplink_peak_rate=f"{round(random.uniform(0.9, 1.1), 1)} Gbps",
            urllc_latency=f"{round(random.uniform(0.8, 1.2), 1)} ms",
            v2x_latency=f"{round(random.uniform(4.5, 5.5), 1)} ms",
            sla_compliance=f"{round(99.95 + random.random() * 0.04, 2)}%",
            sensing_accuracy=f"{round(98.0 + random.random() * 2, 1)}%",
            reliability=f"{round(99.99 + random.random() * 0.009, 4)}%",
            slices_active=4, edges_online=3, alerts_count=random.randint(0, 3),
            timestamp=ts
        ))

    db.session.bulk_save_objects(metrics)
    db.session.commit()
    logger.info(f"已创建 {len(metrics)} 条仪表盘指标数据")


if __name__ == '__main__':
    from app import app
    with app.app_context():
        seed_all()