# ============================================
# 佳帮手兴平智造基地 - 确定性网络调度数据生成引擎
# 基于真实制造业业务规则生成数据
# 数据量：约45000+条，具有业务逻辑一致性
# ============================================

import math
from datetime import datetime, timedelta
from database import db
from models.db_models import (
    User, Product, Order, OrderItem, ProductionLine,
    Device, NetworkSlice, EdgeNode, SimulationRecord,
    AIAnalysisLog, SensingMetric, DashboardMetric,
    AGVTask, NetworkLoadEvent
)
from utils.password import hash_password

# ============================================
# 企业场景设定 - 陕西佳帮手集团 兴平智造基地
# ============================================
COMPANY_NAME = "佳帮手集团"
COMPANY_FULL = "陕西佳帮手集团控股有限公司 - 兴平智造基地"
AREA_ACRES = 500
TOTAL_EQUIPMENT = 1000
TOTAL_AGVS = 80

# 佳帮手主营产品类别
PRODUCT_TYPES = {
    '清洁工具': {
        '拖把系列': ['旋转拖把-双驱动', '平板拖把-铝合金', '胶棉拖把-对折式', '喷雾拖把-免手洗', '电动拖把-无线'],
        '扫把系列': ['扫把簸箕套装-不锈钢', '扫把簸箕套装-塑料', '魔术扫把-硅胶', '静电扫把-轻便'],
        '玻璃清洁': ['玻璃擦-双面磁吸', '玻璃刮-伸缩杆', '玻璃清洁器-电动'],
        '马桶清洁': ['马桶刷套装-壁挂', '马桶刷套装-落地', '一次性马桶刷-替换头'],
        '百洁布': ['百洁布套装-3片', '百洁布套装-5片', '纳米海绵-100片'],
    },
    '收纳整理': {
        '收纳箱': ['收纳箱-30L透明', '收纳箱-50L透明', '收纳箱-80L透明', '收纳箱-120L', '收纳箱-200L'],
        '收纳盒': ['收纳盒-小号', '收纳盒-中号', '收纳盒-大号', '抽屉式收纳盒-3层', '抽屉式收纳盒-5层'],
        '收纳柜': ['收纳柜-3层', '收纳柜-5层', '收纳柜-带轮', '儿童收纳架'],
        '衣架系列': ['衣架-塑料10只', '衣架-不锈钢10只', '衣架-防滑10只', '裤架-5只装'],
    },
    '卫浴用品': {
        '盆桶系列': ['洗脸盆-小号', '洗脸盆-中号', '洗脸盆-大号', '水桶-15L', '水桶-25L'],
        '浴室收纳': ['肥皂盒-壁挂', '牙刷架-壁挂', '浴室置物架-三角', '浴室置物架-双层'],
        '垃圾桶': ['垃圾桶-5L', '垃圾桶-10L', '垃圾桶-15L', '分类垃圾桶-双桶', '脚踏垃圾桶-不锈钢'],
    },
    '厨房用品': {
        '保鲜盒': ['保鲜盒套装-3件', '保鲜盒套装-5件', '保鲜盒套装-10件', '玻璃保鲜盒-圆形'],
        '调料收纳': ['调料盒套装-4格', '调料瓶套装', '油壶-自动开合', '米桶-10kg'],
        '菜板沥水': ['塑料菜板-小号', '塑料菜板-大号', '沥水篮-单层', '沥水篮-双层'],
    },
    '婴童用品': {
        '婴儿用品': ['婴儿浴盆-可折叠', '儿童坐便器', '奶粉盒-便携', '儿童餐具套装'],
    },
}

# 佳帮手生产区域（兴平基地）
PRODUCTION_ZONES = [
    # 注塑车间（核心：1000+台注塑机）
    {'name': '注塑车间A区', 'code': 'IM-A', 'zone_type': 'injection_molding', 'category': 'production', 'capacity': 200, 'network_priority': 1, 'location': '1号厂房东侧', 'device_count': 120},
    {'name': '注塑车间B区', 'code': 'IM-B', 'zone_type': 'injection_molding', 'category': 'production', 'capacity': 200, 'network_priority': 1, 'location': '1号厂房西侧', 'device_count': 120},
    {'name': '注塑车间C区', 'code': 'IM-C', 'zone_type': 'injection_molding', 'category': 'production', 'capacity': 200, 'network_priority': 1, 'location': '2号厂房', 'device_count': 100},
    # 模具加工车间（200+精密设备）
    {'name': '模具加工车间', 'code': 'MD-01', 'zone_type': 'mold_manufacturing', 'category': 'production', 'capacity': 50, 'network_priority': 1, 'location': '模具工厂', 'device_count': 200},
    # 组装线
    {'name': '组装线1号', 'code': 'AS-01', 'zone_type': 'assembly', 'category': 'production', 'capacity': 100, 'network_priority': 2, 'location': '3号厂房', 'device_count': 40},
    {'name': '组装线2号', 'code': 'AS-02', 'zone_type': 'assembly', 'category': 'production', 'capacity': 100, 'network_priority': 2, 'location': '3号厂房', 'device_count': 40},
    {'name': '组装线3号', 'code': 'AS-03', 'zone_type': 'assembly', 'category': 'production', 'capacity': 100, 'network_priority': 2, 'location': '4号厂房', 'device_count': 40},
    # 质检区
    {'name': '质检中心', 'code': 'QC-01', 'zone_type': 'quality', 'category': 'quality', 'capacity': 80, 'network_priority': 2, 'location': '3号厂房', 'device_count': 60},
    # 包装区
    {'name': '包装车间A区', 'code': 'PK-A', 'zone_type': 'packaging', 'category': 'packaging', 'capacity': 150, 'network_priority': 3, 'location': '4号厂房', 'device_count': 30},
    {'name': '包装车间B区', 'code': 'PK-B', 'zone_type': 'packaging', 'category': 'packaging', 'capacity': 150, 'network_priority': 3, 'location': '4号厂房', 'device_count': 30},
    # 仓库
    {'name': '原料仓', 'code': 'WH-RM', 'zone_type': 'storage', 'category': 'storage', 'capacity': 500, 'network_priority': 3, 'location': '仓储区北侧', 'device_count': 20},
    {'name': '半成品仓', 'code': 'WH-SF', 'zone_type': 'storage', 'category': 'storage', 'capacity': 300, 'network_priority': 3, 'location': '仓储区中央', 'device_count': 15},
    {'name': '成品仓A区', 'code': 'WH-FA', 'zone_type': 'storage', 'category': 'storage', 'capacity': 800, 'network_priority': 3, 'location': '仓储区南侧', 'device_count': 25},
    {'name': '成品仓B区', 'code': 'WH-FB', 'zone_type': 'storage', 'category': 'storage', 'capacity': 800, 'network_priority': 3, 'location': '仓储区南侧', 'device_count': 25},
    # 发货区
    {'name': '发货月台A', 'code': 'SH-A', 'zone_type': 'shipping', 'category': 'outbound', 'capacity': 200, 'network_priority': 4, 'location': '仓储区西侧', 'device_count': 10},
    {'name': '发货月台B', 'code': 'SH-B', 'zone_type': 'shipping', 'category': 'outbound', 'capacity': 200, 'network_priority': 4, 'location': '仓储区西侧', 'device_count': 10},
    # 中控室
    {'name': '中控调度中心', 'code': 'CC-01', 'zone_type': 'control_center', 'category': 'control', 'capacity': 20, 'network_priority': 1, 'location': '综合楼', 'device_count': 30},
]

# 网络切片定义（佳帮手定制）
NETWORK_SLICES = [
    {'name': 'URLLC-注塑模具调度', 'slice_type': 'industrial', 'size': 100, 'latency': 0.5, 'bandwidth': 500, 'sla': 99.999, 'desc': '超低时延切片，用于注塑机和模具加工中心实时控制，时延<1ms'},
    {'name': 'URLLC-AGV物流调度', 'slice_type': 'industrial', 'size': 100, 'latency': 1.0, 'bandwidth': 300, 'sla': 99.99, 'desc': 'AGV物流调度切片，保障80台AGV实时调度通信'},
    {'name': 'eMBB-质检高清传输', 'slice_type': 'civil', 'size': 200, 'latency': 5.0, 'bandwidth': 2000, 'sla': 99.9, 'desc': '大带宽切片，用于质检高清图像和AR远程协助'},
    {'name': 'mMTC-传感器采集', 'slice_type': 'vehicle', 'size': 300, 'latency': 20.0, 'bandwidth': 200, 'sla': 99.5, 'desc': '海量连接切片，1000+传感器温湿度/振动/能耗数据采集'},
    {'name': 'eMBB-安防监控', 'slice_type': 'civil', 'size': 150, 'latency': 8.0, 'bandwidth': 1500, 'sla': 99.9, 'desc': '安防监控切片，用于全厂区高清视频监控'},
]

# 边缘节点定义
EDGE_NODES = [
    {'name': '注塑车间A区边缘节点', 'location': '注塑车间A区', 'cpu': 65.0, 'memory': 70.0, 'tasks': 12, 'ip': '192.168.10.11'},
    {'name': '注塑车间B区边缘节点', 'location': '注塑车间B区', 'cpu': 60.0, 'memory': 65.0, 'tasks': 10, 'ip': '192.168.10.12'},
    {'name': '注塑车间C区边缘节点', 'location': '注塑车间C区', 'cpu': 55.0, 'memory': 60.0, 'tasks': 8, 'ip': '192.168.10.13'},
    {'name': '模具车间边缘节点', 'location': '模具加工车间', 'cpu': 75.0, 'memory': 80.0, 'tasks': 15, 'ip': '192.168.10.14'},
    {'name': '组装线边缘节点', 'location': '组装线1-3号', 'cpu': 50.0, 'memory': 55.0, 'tasks': 8, 'ip': '192.168.10.15'},
    {'name': '质检中心边缘节点', 'location': '质检中心', 'cpu': 70.0, 'memory': 75.0, 'tasks': 10, 'ip': '192.168.10.16'},
    {'name': '仓储区边缘节点', 'location': '仓储区', 'cpu': 45.0, 'memory': 50.0, 'tasks': 6, 'ip': '192.168.10.17'},
    {'name': '中控中心调度节点', 'location': '中控调度中心', 'cpu': 85.0, 'memory': 90.0, 'tasks': 20, 'ip': '192.168.10.10'},
]

# 用户定义
USERS = [
    {'username': 'admin', 'password': 'admin123', 'email': 'admin@jiabs.com', 'full_name': '系统管理员', 'role': 'admin'},
    {'username': 'production_mgr', 'password': 'prod123', 'email': 'pm@jiabs.com', 'full_name': '生产经理-李齐', 'role': 'admin'},
    {'username': 'workshop_chief', 'password': 'ws123', 'email': 'ws@jiabs.com', 'full_name': '车间主任-刘涛', 'role': 'operator'},
    {'username': 'agv_operator', 'password': 'agv123', 'email': 'agv@jiabs.com', 'full_name': 'AGV调度员-何美莉', 'role': 'operator'},
    {'username': 'network_eng', 'password': 'net123', 'email': 'net@jiabs.com', 'full_name': '网络工程师', 'role': 'operator'},
    {'username': 'quality_inspector', 'password': 'qc123', 'email': 'qc@jiabs.com', 'full_name': '质检组长-孔轩轩', 'role': 'operator'},
    {'username': 'inventory_mgr', 'password': 'inv123', 'email': 'inv@jiabs.com', 'full_name': '仓储主管', 'role': 'operator'},
    {'username': 'shift_leader', 'password': 'shift123', 'email': 'shift@jiabs.com', 'full_name': '值班长', 'role': 'operator'},
    {'username': 'maintenance_eng', 'password': 'maint123', 'email': 'maint@jiabs.com', 'full_name': '设备维护工程师', 'role': 'operator'},
    {'username': 'viewer', 'password': 'viewer123', 'email': 'viewer@jiabs.com', 'full_name': '访客', 'role': 'viewer'},
]

# 设备类型定义（佳帮手：1000+设备）
DEVICE_CONFIG = {
    'injection_molding': {'type': 'machine', 'subtype': 'injection_molding', 'count': 340, 'slice': 'URLLC-注塑模具调度'},
    'robot_arm': {'type': 'robot', 'subtype': 'robot_arm', 'count': 80, 'slice': 'URLLC-注塑模具调度'},
    'agv': {'type': 'robot', 'subtype': 'agv', 'count': 80, 'slice': 'URLLC-AGV物流调度'},
    'stacker': {'type': 'robot', 'subtype': 'stacker', 'count': 20, 'slice': 'URLLC-AGV物流调度'},
    'cnc_5axis': {'type': 'machine', 'subtype': 'cnc_5axis', 'count': 2, 'slice': 'URLLC-注塑模具调度'},
    'cnc_gantry': {'type': 'machine', 'subtype': 'cnc_gantry', 'count': 6, 'slice': 'URLLC-注塑模具调度'},
    'cnc_horizontal': {'type': 'machine', 'subtype': 'cnc_horizontal', 'count': 4, 'slice': 'URLLC-注塑模具调度'},
    'cnc_highspeed': {'type': 'machine', 'subtype': 'cnc_highspeed', 'count': 56, 'slice': 'URLLC-注塑模具调度'},
    'edm': {'type': 'machine', 'subtype': 'edm', 'count': 20, 'slice': 'URLLC-注塑模具调度'},
    'wire_cut': {'type': 'machine', 'subtype': 'wire_cut', 'count': 20, 'slice': 'URLLC-注塑模具调度'},
    'cmm': {'type': 'sensor', 'subtype': 'cmm', 'count': 5, 'slice': 'eMBB-质检高清传输'},
    'dryer': {'type': 'machine', 'subtype': 'dryer', 'count': 50, 'slice': 'mMTC-传感器采集'},
    'screen_printer': {'type': 'machine', 'subtype': 'screen_printer', 'count': 30, 'slice': 'URLLC-注塑模具调度'},
    'crusher': {'type': 'machine', 'subtype': 'crusher', 'count': 15, 'slice': 'mMTC-传感器采集'},
    'laser_marker': {'type': 'machine', 'subtype': 'laser_marker', 'count': 20, 'slice': 'URLLC-注塑模具调度'},
    'conveyor': {'type': 'conveyor', 'subtype': 'conveyor', 'count': 40, 'slice': 'URLLC-AGV物流调度'},
    'sensor_temp': {'type': 'sensor', 'subtype': 'temperature', 'count': 200, 'slice': 'mMTC-传感器采集'},
    'sensor_humidity': {'type': 'sensor', 'subtype': 'humidity', 'count': 100, 'slice': 'mMTC-传感器采集'},
    'sensor_vibration': {'type': 'sensor', 'subtype': 'vibration', 'count': 80, 'slice': 'mMTC-传感器采集'},
    'camera': {'type': 'camera', 'subtype': 'camera', 'count': 60, 'slice': 'eMBB-安防监控'},
    'rfid_reader': {'type': 'sensor', 'subtype': 'rfid_reader', 'count': 50, 'slice': 'mMTC-传感器采集'},
}


# ============================================
# 数据生成函数
# ============================================

def _build_sku(sub_cat, name, idx):
    """构建SKU编码"""
    cat_short = sub_cat[:2].upper()
    return f"JBS-{cat_short}-{idx:04d}"


def generate_users():
    """生成10个用户"""
    if User.query.count() > 0:
        return []
    users = []
    for u in USERS:
        user = User(
            username=u['username'],
            password_hash=hash_password(u['password']),
            email=u['email'],
            full_name=u['full_name'],
            role=u['role']
        )
        db.session.add(user)
        users.append(user)
    db.session.flush()
    return users


def generate_zones():
    """生成17个生产区域（佳帮手兴平基地）"""
    if ProductionLine.query.filter(ProductionLine.zone_type.isnot(None)).count() > 0:
        return ProductionLine.query.all()
    zones = []
    for z in PRODUCTION_ZONES:
        zone = ProductionLine(
            name=z['name'],
            code=z['code'],
            category=z['category'],
            zone_type=z['zone_type'],
            status='running',
            capacity=z['capacity'],
            efficiency=95.0 + (hash(z['code']) % 50) / 10.0,
            location=z['location'],
            oee=92.0 + (hash(z['code']) % 60) / 10.0,
            network_priority=z['network_priority'],
            device_count=z['device_count'],
            temperature=22.0 + (hash(z['code']) % 80) / 10.0,
            humidity=50.0 + (hash(z['code']) % 30) / 1.0,
        )
        db.session.add(zone)
        zones.append(zone)
    db.session.flush()
    return zones


def generate_products(count=8000):
    """生成8000个产品（10x，按佳帮手真实品类）"""
    if Product.query.count() > 0:
        return Product.query.all()
    products = []
    zones = ProductionLine.query.all()
    zone_map = {
        'production': [z for z in zones if z.category == 'production'],
        'storage': [z for z in zones if z.category == 'storage'],
    }

    idx = 0
    for main_cat, sub_cats in PRODUCT_TYPES.items():
        for sub_cat, names in sub_cats.items():
            for name in names:
                zone_list = zone_map.get('storage', zones)
                zone = zone_list[idx % len(zone_list)] if zone_list else None
                qty = 500 + (idx * 23) % 10000
                price = round(5.0 + (idx * 3.7) % 200, 2)
                weight = round(0.1 + (idx * 0.5) % 15, 2)

                p = Product(
                    name=name,
                    sku=_build_sku(sub_cat, name, idx),
                    category=main_cat,
                    material_type=sub_cat,
                    price=price,
                    quantity=qty,
                    unit='件',
                    description=f"{name} - {COMPANY_NAME} {main_cat}",
                    status='active',
                    min_stock=max(50, qty // 10),
                    max_stock=qty * 5,
                    warehouse_zone_id=zone.id if zone else None,
                    shelf_life_days=730,
                    weight_kg=weight
                )
                db.session.add(p)
                products.append(p)
                idx += 1

    db.session.flush()
    return products


def generate_network_slices():
    """生成5个网络切片（佳帮手定制）"""
    if NetworkSlice.query.count() > 0:
        return NetworkSlice.query.all()
    slices = []
    for s in NETWORK_SLICES:
        ns = NetworkSlice(
            name=s['name'], slice_type=s['slice_type'], size=s['size'],
            description=s['desc'], status='active',
            latency=s['latency'], bandwidth=s['bandwidth'], sla_compliance=s['sla']
        )
        db.session.add(ns)
        slices.append(ns)
    db.session.flush()
    return slices


def generate_devices(zones, slices):
    """生成1200+台设备（注塑机+机械臂+AGV+模具设备+传感器）"""
    if Device.query.filter(Device.device_subtype.isnot(None)).count() > 0:
        return Device.query.all()
    devices = []
    slice_map = {s.name: s for s in slices}
    zone_map = {z.zone_type: z for z in zones if z.zone_type}
    all_zones = list(zones)

    for dev_type, cfg in DEVICE_CONFIG.items():
        for i in range(cfg['count']):
            # 智能分配区域
            if dev_type in ('injection_molding', 'robot_arm', 'dryer', 'screen_printer', 'crusher', 'laser_marker'):
                im_zones = [z for z in zones if z.zone_type == 'injection_molding']
                zone = im_zones[i % len(im_zones)] if im_zones else all_zones[i % len(all_zones)]
            elif dev_type in ('cnc_5axis', 'cnc_gantry', 'cnc_horizontal', 'cnc_highspeed', 'edm', 'wire_cut'):
                mold_zones = [z for z in zones if z.zone_type == 'mold_manufacturing']
                zone = mold_zones[0] if mold_zones else all_zones[i % len(all_zones)]
            elif dev_type in ('agv', 'stacker', 'conveyor'):
                storage_zones = [z for z in zones if z.zone_type == 'storage']
                zone = storage_zones[i % len(storage_zones)] if storage_zones else all_zones[i % len(all_zones)]
            elif dev_type == 'cmm':
                qc_zones = [z for z in zones if z.zone_type == 'quality']
                zone = qc_zones[0] if qc_zones else all_zones[i % len(all_zones)]
            elif dev_type in ('sensor_temp', 'sensor_humidity', 'sensor_vibration'):
                zone = all_zones[i % len(all_zones)]
            elif dev_type == 'camera':
                zone = all_zones[i % len(all_zones)]
            elif dev_type == 'rfid_reader':
                storage_zones = [z for z in zones if z.zone_type in ('storage', 'shipping')]
                zone = storage_zones[i % len(storage_zones)] if storage_zones else all_zones[i % len(all_zones)]
            else:
                zone = all_zones[i % len(all_zones)]

            battery = round(100.0 - (i * 3.5) % 40, 1) if dev_type in ('agv', 'stacker') else None
            speed = 1.0 + (i % 5) * 0.3 if dev_type in ('agv', 'stacker', 'conveyor') else None
            load_cap = 500 + (i % 10) * 200 if dev_type in ('agv', 'stacker') else None

            code_prefix = dev_type.upper()
            d = Device(
                name=f"{cfg['subtype'].upper()}-{i+1:03d}",
                code=f"{code_prefix}-{i+1:04d}",
                type=cfg['type'],
                device_subtype=cfg['subtype'],
                line_id=zone.id,
                status='online' if i % 15 != 14 else 'maintenance',
                ip_address=f"192.168.{(i // 254) + 1}.{i % 254 + 1}",
                firmware_version=f"v{2 + (i % 3)}.{i % 10}.{i % 20}",
                last_maintenance=datetime.now() - timedelta(days=i % 30),
                battery_level=battery,
                load_capacity_kg=load_cap,
                speed_mps=speed,
                associated_slice_id=slice_map[cfg['slice']].id if cfg['slice'] in slice_map else None,
                metrics_json=f'{{"uptime_h": {720 - i % 720}, "cycles": {i * 50 + 1000}, "error_rate": {0.001 * (i % 5)}}}'
            )
            db.session.add(d)
            devices.append(d)
    db.session.flush()
    return devices


def generate_edge_nodes():
    """生成8个边缘节点"""
    if EdgeNode.query.count() > 0:
        return EdgeNode.query.all()
    nodes = []
    for en in EDGE_NODES:
        node = EdgeNode(
            name=en['name'], location=en['location'],
            cpu=en['cpu'], memory=en['memory'],
            status='online', tasks=en['tasks'], ip=en['ip']
        )
        db.session.add(node)
        nodes.append(node)
    db.session.flush()
    return nodes


def generate_orders(users, zones, products, count=3000):
    """生成3000个生产任务单（10x）"""
    if Order.query.filter(Order.task_type.isnot(None)).count() > 0:
        return Order.query.all()
    orders = []
    user_list = [u for u in users if u.role in ('admin', 'operator')]
    shipping_zones = [z for z in zones if z.zone_type == 'shipping']
    all_zones = [z for z in zones if z.category in ('production', 'storage')]

    statuses = ['completed', 'completed', 'completed', 'completed', 'processing', 'processing', 'processing', 'pending', 'pending', 'shipped']

    for i in range(count):
        day_offset = (count - 1 - i) % 90  # 90天
        dt = datetime.now() - timedelta(days=day_offset, hours=i % 10 + 8)

        if i % 3 == 0:
            task_type = 'inbound'
            zone = all_zones[i % len(all_zones)]
        elif i % 3 == 1:
            task_type = 'outbound'
            zone = shipping_zones[i % len(shipping_zones)] if shipping_zones else all_zones[i % len(all_zones)]
        else:
            task_type = 'production'
            zone = all_zones[i % len(all_zones)]

        total_qty = (i % 50 + 1) * 10
        total = round(total_qty * (5 + i % 200), 2)

        order = Order(
            order_number=f"JBS-{datetime.now().year}{datetime.now().month:02d}-{i+1:06d}",
            user_id=user_list[i % len(user_list)].id,
            task_type=task_type,
            total_amount=total,
            status=statuses[i % len(statuses)],
            priority=(i % 5) + 1,
            target_zone_id=zone.id,
            notes=f"{'原料入库' if task_type == 'inbound' else ('成品出库' if task_type == 'outbound' else '生产任务')} - 第{day_offset+1}批 - {COMPANY_NAME}",
            created_at=dt
        )
        db.session.add(order)
        db.session.flush()

        for j in range(1, 4):
            p = products[(i * 3 + j) % len(products)]
            qty = (i * 7 + j * 13) % 100 + 10
            item = OrderItem(
                order_id=order.id,
                product_id=p.id,
                quantity=qty,
                unit_price=p.price,
                subtotal=round(p.price * qty, 2),
                created_at=dt
            )
            db.session.add(item)
        orders.append(order)
    db.session.flush()
    return orders


def generate_agv_tasks(zones, devices, orders, slices, count=5000):
    """生成5000条AGV调度任务（10x）"""
    if AGVTask.query.count() > 0:
        return []
    tasks = []
    agvs = [d for d in devices if d.device_subtype == 'agv']
    urllc_slice = next((s for s in slices if 'AGV' in s.name), slices[0])
    storage_zones = [z for z in zones if z.zone_type == 'storage']
    shipping_zones = [z for z in zones if z.zone_type == 'shipping']
    production_zones = [z for z in zones if z.category == 'production']
    quality_zones = [z for z in zones if z.zone_type == 'quality']

    task_types = ['transport', 'transport', 'transport', 'retrieve', 'store', 'sort', 'transport', 'retrieve']
    statuses = ['completed', 'completed', 'completed', 'completed', 'in_progress', 'in_progress', 'dispatched', 'pending']

    for i in range(count):
        day_offset = (count - 1 - i) % 90
        dt = datetime.now() - timedelta(days=day_offset, hours=i % 10 + 8)

        task_type = task_types[i % len(task_types)]
        source = storage_zones[i % len(storage_zones)]
        if task_type in ('transport', 'retrieve', 'sort'):
            target = shipping_zones[i % len(shipping_zones)]
        elif task_type == 'store':
            target = storage_zones[(i + 1) % len(storage_zones)]
        else:
            target = production_zones[i % len(production_zones)]

        agv = agvs[i % len(agvs)]
        priority = (i % 5) + 1
        distance = 30 + (i % 50) * 10
        weight = 100 + (i % 15) * 50
        latency_req = 0.5 + (priority - 1) * 0.25
        actual_latency = latency_req * (0.85 + (i % 5) * 0.06)

        task = AGVTask(
            task_no=f"JBS-AGV-{datetime.now().year}-{i+1:06d}",
            task_type=task_type,
            source_zone_id=source.id,
            target_zone_id=target.id,
            device_id=agv.id,
            order_id=orders[i % len(orders)].id if orders else None,
            priority=priority,
            network_slice_id=urllc_slice.id,
            latency_requirement_ms=round(latency_req, 2),
            actual_latency_ms=round(actual_latency, 2),
            distance_m=distance,
            weight_kg=weight,
            status=statuses[i % len(statuses)],
            dispatched_at=dt,
            completed_at=dt + timedelta(seconds=20 + i % 180) if statuses[i % len(statuses)] == 'completed' else None,
            created_at=dt
        )
        db.session.add(task)
        tasks.append(task)
    db.session.flush()
    return tasks


def generate_network_events(zones, slices, count=2000):
    """生成2000条网络负载事件（10x）"""
    if NetworkLoadEvent.query.count() > 0:
        return []
    events = []
    event_types = ['normal', 'normal', 'normal', 'peak', 'normal', 'normal', 'congestion', 'recovery', 'normal', 'normal']
    severities = ['normal', 'normal', 'normal', 'warning', 'normal', 'normal', 'critical', 'normal', 'normal', 'normal']

    for i in range(count):
        day_offset = (count - 1 - i) % 90
        dt = datetime.now() - timedelta(days=day_offset, minutes=i * 7 % 1440)
        zone = zones[i % len(zones)]
        sl = slices[i % len(slices)]

        etype = event_types[i % len(event_types)]
        sev = severities[i % len(severities)]
        active = 10 + i % 50 if etype == 'peak' else (30 + i % 40 if etype == 'congestion' else 5 + i % 15)
        bw = 300 + active * 20 + (i % 10) * 15
        lat = 0.3 + active * 0.2 + (i % 5) * 0.1
        plr = 0.0005 * (i % 5) if etype == 'congestion' else 0.00001

        event = NetworkLoadEvent(
            event_type=etype,
            zone_id=zone.id,
            slice_id=sl.id,
            active_agvs=active,
            bandwidth_usage_mbps=round(bw, 1),
            latency_ms=round(lat, 2),
            packet_loss_rate=round(plr, 4),
            severity=sev,
            description=f"{zone.name} - {ETYPS_CN.get(etype, etype)} - 活跃设备:{active}台 带宽:{bw:.0f}Mbps 时延:{lat:.1f}ms",
            triggered_at=dt,
            resolved_at=dt + timedelta(minutes=10 + i % 60) if etype in ('peak', 'congestion') else None
        )
        db.session.add(event)
        events.append(event)
    db.session.flush()
    return events


ETYPS_CN = {'normal': '正常', 'peak': '峰值负载', 'congestion': '网络拥塞', 'recovery': '负载恢复', 'failure': '链路故障'}


def generate_sensing_data(count=20000):
    """生成20000条传感器数据（10x）"""
    if SensingMetric.query.count() > 0:
        return
    sensor_types = ['temperature'] * 4 + ['humidity'] * 3 + ['vibration'] * 3 + ['person'] * 2 + ['device'] * 2 + ['environment'] * 2
    metric_names = ['precision', 'distance', 'refresh_rate', 'value', 'precision', 'distance', 'refresh_rate', 'count', 'density', 'precision']
    units = ['°C', 'm', 'Hz', '%', '%RH', 'm', 'Hz', '人', '台', 'lux']

    for i in range(count):
        minutes_ago = count - i
        dt = datetime.now() - timedelta(minutes=minutes_ago * 2)
        st = sensor_types[i % len(sensor_types)]
        mn = metric_names[i % len(metric_names)]
        unit = units[i % len(units)]

        if st == 'temperature':
            value = 22.0 + (i % 80) / 10.0
        elif st == 'humidity':
            value = 45.0 + (i % 55) / 1.0
        elif st == 'vibration':
            value = 0.5 + (i % 10) / 10.0
        elif st == 'person':
            value = 5 + (i % 30)
        elif st == 'device':
            value = 50 + (i % 100)
        else:
            value = 300 + (i % 500)

        metric = SensingMetric(
            sensor_type=st, metric_name=mn,
            value=round(value, 2), unit=unit, timestamp=dt
        )
        db.session.add(metric)


def generate_dashboard_metrics(count=10000):
    """生成10000条仪表盘快照（10x）"""
    if DashboardMetric.query.count() > 0:
        return
    for i in range(count):
        minutes_ago = count - i
        dt = datetime.now() - timedelta(minutes=minutes_ago * 15)
        is_peak = (i % 48) in (9, 10, 14, 15, 16)

        dm = DashboardMetric(
            air_peak_rate=f"{4.5 + (i % 15) / 10:.1f}Gbps",
            uplink_peak_rate=f"{2.0 + (i % 10) / 10:.1f}Gbps",
            urllc_latency=f"{0.5 + (i % 5) / 10:.1f}ms",
            v2x_latency=f"{1.0 + (i % 10) / 10:.1f}ms",
            sla_compliance=f"{99.95 + (i % 5) / 100:.2f}%",
            sensing_accuracy=f"{98.0 + (i % 20) / 10:.1f}%",
            reliability=f"{99.99 + (i % 3) / 100:.2f}%",
            slices_active=5,
            edges_online=8,
            alerts_count=i % 8 if is_peak else 0,
            active_agvs=40 + i % 40 if is_peak else 10 + i % 20,
            bandwidth_usage_mbps=800 + i % 400 if is_peak else 300 + i % 200,
            network_load_pct=70 + i % 25 if is_peak else 30 + i % 25,
            pending_tasks=20 + i % 30 if is_peak else 5 + i % 10,
            completed_tasks=500 + i % 200,
            timestamp=dt
        )
        db.session.add(dm)


def generate_simulation_history(count=200):
    """生成200条历史仿真记录（10x）"""
    if SimulationRecord.query.count() > 0:
        return
    scenarios = ['low', 'medium', 'high']
    for i in range(count):
        day_offset = count - i
        sc = scenarios[i % 3]
        sr = SimulationRecord(
            scenario=sc,
            slice_type='industrial',
            result_json=f'{{"scenario": "{sc}", "tasks": {50 + i * 5}, "latency_improvement": {10 + i % 15}, "throughput_improvement": {15 + i % 10}}}',
            task_count=50 + i * 5,
            latency_improvement=10.0 + i % 15,
            throughput_improvement=15.0 + i % 10,
            energy_saving=5.0 + i % 10,
            created_at=datetime.now() - timedelta(days=day_offset)
        )
        db.session.add(sr)


# ============================================
# 主入口
# ============================================

def generate_all():
    """生成全部佳帮手生产基地数据（约45000+条）"""
    print("=" * 60)
    print(f"  {COMPANY_FULL}")
    print("  确定性网络智能调度数据生成")
    print("=" * 60)

    print("\n[Phase 1/10] 生成用户...")
    users = generate_users()
    print(f"  -> {len(users)} 个用户")

    print("\n[Phase 2/10] 生成生产区域...")
    zones = generate_zones()
    print(f"  -> {len(zones)} 个区域（注塑x3/模具/组装x3/质检/包装x2/仓储x4/发货x2/中控）")

    print("\n[Phase 3/10] 生成产品数据...")
    products = generate_products(8000)
    print(f"  -> {len(products)} 个产品（清洁/收纳/卫浴/厨房/婴童）")

    print("\n[Phase 4/10] 生成网络切片...")
    slices = generate_network_slices()
    print(f"  -> {len(slices)} 个切片（URLLCx2/eMBBx2/mMTCx1）")

    print("\n[Phase 5/10] 生成生产设备...")
    devices = generate_devices(zones, slices)
    print(f"  -> {len(devices)} 台设备（注塑机/机械臂/AGV/模具/传感器）")

    print("\n[Phase 6/10] 生成边缘节点...")
    generate_edge_nodes()
    print(f"  -> {len(EDGE_NODES)} 个节点")

    print("\n[Phase 7/10] 生成生产任务单...")
    orders = generate_orders(users, zones, products, 3000)
    print(f"  -> {len(orders)} 个任务单")

    print("\n[Phase 8/10] 生成AGV调度任务...")
    tasks = generate_agv_tasks(zones, devices, orders, slices, 5000)
    print(f"  -> {len(tasks)} 条AGV任务")

    print("\n[Phase 9/10] 生成网络负载事件...")
    generate_network_events(zones, slices, 2000)
    print(f"  -> 2000 条网络事件")

    print("\n[Phase 10/10] 生成传感器/仪表盘/仿真数据...")
    generate_sensing_data(20000)
    print(f"  -> 20000 条传感器数据")
    generate_dashboard_metrics(10000)
    print(f"  -> 10000 条仪表盘快照")
    generate_simulation_history(200)
    print(f"  -> 200 条仿真记录")

    db.session.commit()
    total = len(users) + len(zones) + len(products) + len(slices) + len(devices) + 8 + len(orders) + len(tasks) + 2000 + 20000 + 10000 + 200
    print(f"\n{'=' * 60}")
    print(f"  数据生成完成！总计约 {total} 条记录")
    print(f"  企业: {COMPANY_FULL}")
    print(f"  {'=' * 60}")