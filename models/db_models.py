# ============================================
# SQLAlchemy 数据模型
# 包含所有业务表的ORM定义
# ============================================

from datetime import datetime
from database import db


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')  # admin / operator / viewer
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Product(db.Model):
    """物料表（原材料/半成品/成品）—— 仓库场景"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # raw_material / semi_finished / finished
    material_type = db.Column(db.String(50))  # plastic / paper / textile / chemical / metal / packaging
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(20), default='件')
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active / inactive / discontinued
    min_stock = db.Column(db.Integer, default=10)
    max_stock = db.Column(db.Integer, default=500)
    warehouse_zone_id = db.Column(db.Integer, db.ForeignKey('production_lines.id'))  # 存放区域
    shelf_life_days = db.Column(db.Integer)  # 保质期(天)
    weight_kg = db.Column(db.Float)  # 单件重量(kg)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    warehouse_zone = db.relationship('ProductionLine', foreign_keys=[warehouse_zone_id])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'category': self.category,
            'material_type': self.material_type,
            'price': round(self.price, 2),
            'quantity': self.quantity,
            'unit': self.unit,
            'description': self.description,
            'status': self.status,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'warehouse_zone_id': self.warehouse_zone_id,
            'warehouse_zone_name': self.warehouse_zone.name if self.warehouse_zone else None,
            'shelf_life_days': self.shelf_life_days,
            'weight_kg': self.weight_kg,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Order(db.Model):
    """出入库任务单 —— 仓库场景"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_type = db.Column(db.String(20), nullable=False, default='outbound')  # inbound / outbound / transfer
    total_amount = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending / processing / completed / cancelled
    priority = db.Column(db.Integer, default=3)  # 1(critical)-5(normal)
    target_zone_id = db.Column(db.Integer, db.ForeignKey('production_lines.id'))  # 目标区域
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    target_zone = db.relationship('ProductionLine', foreign_keys=[target_zone_id])

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'task_type': self.task_type,
            'total_amount': round(self.total_amount, 2),
            'status': self.status,
            'priority': self.priority,
            'target_zone_id': self.target_zone_id,
            'target_zone_name': self.target_zone.name if self.target_zone else None,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OrderItem(db.Model):
    """订单项表"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    product = db.relationship('Product', backref='order_items')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': round(self.unit_price, 2),
            'subtotal': round(self.subtotal, 2),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProductionLine(db.Model):
    """仓库区域 / 生产线表 —— 仓库场景"""
    __tablename__ = 'production_lines'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # assembly / machining / packaging / testing
    zone_type = db.Column(db.String(30))  # inbound_dock / storage / picking / sorting / outbound_dock / quality / returns
    status = db.Column(db.String(20), nullable=False, default='idle')  # idle / running / maintenance / offline
    capacity = db.Column(db.Integer, nullable=False, default=100)  # 每小时产能 / 存储容量(托盘位)
    efficiency = db.Column(db.Float, nullable=False, default=100.0)  # 效率百分比
    current_task = db.Column(db.String(100))
    location = db.Column(db.String(100))
    oee = db.Column(db.Float, default=85.0)  # 设备综合效率
    network_priority = db.Column(db.Integer, default=3)  # 1-5网络优先级
    device_count = db.Column(db.Integer, default=0)
    temperature = db.Column(db.Float)  # 环境温度
    humidity = db.Column(db.Float)  # 环境湿度
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    devices = db.relationship('Device', backref='production_line', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'category': self.category,
            'zone_type': self.zone_type,
            'status': self.status,
            'capacity': self.capacity,
            'efficiency': round(self.efficiency, 1),
            'current_task': self.current_task,
            'location': self.location,
            'oee': round(self.oee, 1) if self.oee else None,
            'network_priority': self.network_priority,
            'device_count': self.devices.count(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Device(db.Model):
    """仓储设备表 —— 仓库场景"""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # sensor / robot / controller / conveyor / camera
    device_subtype = db.Column(db.String(50))  # agv / stacker / sorter / conveyor / rfid_reader / camera
    line_id = db.Column(db.Integer, db.ForeignKey('production_lines.id'), index=True)
    status = db.Column(db.String(20), nullable=False, default='online')  # online / offline / maintenance
    ip_address = db.Column(db.String(45))
    firmware_version = db.Column(db.String(20))
    last_maintenance = db.Column(db.DateTime)
    battery_level = db.Column(db.Float)  # 电池电量(AGV)
    load_capacity_kg = db.Column(db.Float)  # 载重(kg)
    speed_mps = db.Column(db.Float)  # 速度(m/s)
    associated_slice_id = db.Column(db.Integer, db.ForeignKey('network_slices.id'))  # 关联网络切片
    metrics_json = db.Column(db.Text)  # JSON格式存储设备运行指标
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    associated_slice = db.relationship('NetworkSlice', foreign_keys=[associated_slice_id])

    def to_dict(self):
        import json
        metrics = {}
        if self.metrics_json:
            try:
                metrics = json.loads(self.metrics_json)
            except json.JSONDecodeError:
                pass
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type,
            'device_subtype': self.device_subtype,
            'line_id': self.line_id,
            'line_name': self.production_line.name if self.production_line else None,
            'status': self.status,
            'ip_address': self.ip_address,
            'firmware_version': self.firmware_version,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'battery_level': self.battery_level,
            'load_capacity_kg': self.load_capacity_kg,
            'speed_mps': self.speed_mps,
            'associated_slice_id': self.associated_slice_id,
            'associated_slice_name': self.associated_slice.name if self.associated_slice else None,
            'metrics': metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class NetworkSlice(db.Model):
    """网络切片表"""
    __tablename__ = 'network_slices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    slice_type = db.Column(db.String(50), nullable=False)  # industrial / vehicle / civil
    size = db.Column(db.Integer, nullable=False, default=100)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='active')  # active / inactive / configuring
    latency = db.Column(db.Float, nullable=False, default=10.0)  # ms
    bandwidth = db.Column(db.Integer, nullable=False, default=200)  # Mbps
    sla_compliance = db.Column(db.Float, default=99.9)  # SLA合规率
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.slice_type,
            'size': self.size,
            'description': self.description,
            'status': self.status,
            'latency': round(self.latency, 1),
            'bandwidth': self.bandwidth,
            'sla_compliance': round(self.sla_compliance, 2) if self.sla_compliance else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EdgeNode(db.Model):
    """边缘节点表"""
    __tablename__ = 'edge_nodes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    location = db.Column(db.String(100), nullable=False)
    cpu = db.Column(db.Float, nullable=False, default=0)
    memory = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='online')  # online / offline / maintenance
    tasks = db.Column(db.Integer, nullable=False, default=0)
    ip = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'cpu': round(self.cpu, 1),
            'memory': round(self.memory, 1),
            'status': self.status,
            'tasks': self.tasks,
            'ip': self.ip,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SimulationRecord(db.Model):
    """仿真调度记录表"""
    __tablename__ = 'simulation_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scenario = db.Column(db.String(20), nullable=False)  # low / medium / high
    slice_type = db.Column(db.String(50), nullable=False)  # industrial / vehicle / civil
    result_json = db.Column(db.Text)  # JSON格式存储仿真结果
    task_count = db.Column(db.Integer, default=0)
    latency_improvement = db.Column(db.Float)
    throughput_improvement = db.Column(db.Float)
    energy_saving = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        import json
        result = {}
        if self.result_json:
            try:
                result = json.loads(self.result_json)
            except json.JSONDecodeError:
                pass
        return {
            'id': self.id,
            'scenario': self.scenario,
            'slice_type': self.slice_type,
            'task_count': self.task_count,
            'latency_improvement': self.latency_improvement,
            'throughput_improvement': self.throughput_improvement,
            'energy_saving': self.energy_saving,
            'result': result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AIAnalysisLog(db.Model):
    """AI分析日志表"""
    __tablename__ = 'ai_analysis_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_type = db.Column(db.String(50), nullable=False)  # production / risk / report / optimization
    input_data = db.Column(db.Text)
    output_data = db.Column(db.Text)
    api_called = db.Column(db.Boolean, default=False)
    api_response_time = db.Column(db.Float)  # API响应时间(秒)
    tokens_used = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='success')  # success / failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'api_called': self.api_called,
            'api_response_time': self.api_response_time,
            'tokens_used': self.tokens_used,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SensingMetric(db.Model):
    """感知指标存储表"""
    __tablename__ = 'sensing_metrics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_type = db.Column(db.String(50), nullable=False, index=True)  # temperature / person / device / environment / vibration
    metric_name = db.Column(db.String(50), nullable=False)  # precision / distance / refresh_rate
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_type': self.sensor_type,
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class APIAccessLog(db.Model):
    """API访问日志表"""
    __tablename__ = 'api_access_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    endpoint = db.Column(db.String(200), nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)
    request_id = db.Column(db.String(50))
    response_time = db.Column(db.Float)  # 响应时间(ms)
    status_code = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'method': self.method,
            'request_id': self.request_id,
            'response_time': self.response_time,
            'status_code': self.status_code,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class DashboardMetric(db.Model):
    """仪表盘指标快照表"""
    __tablename__ = 'dashboard_metrics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    air_peak_rate = db.Column(db.String(20))
    uplink_peak_rate = db.Column(db.String(20))
    urllc_latency = db.Column(db.String(20))
    v2x_latency = db.Column(db.String(20))
    sla_compliance = db.Column(db.String(20))
    sensing_accuracy = db.Column(db.String(20))
    reliability = db.Column(db.String(20))
    slices_active = db.Column(db.Integer, default=0)
    edges_online = db.Column(db.Integer, default=0)
    alerts_count = db.Column(db.Integer, default=0)
    # 仓库场景新增字段
    active_agvs = db.Column(db.Integer, default=0)
    bandwidth_usage_mbps = db.Column(db.Float)
    network_load_pct = db.Column(db.Float)
    pending_tasks = db.Column(db.Integer, default=0)
    completed_tasks = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'air_peak_rate': self.air_peak_rate,
            'uplink_peak_rate': self.uplink_peak_rate,
            'urllc_latency': self.urllc_latency,
            'v2x_latency': self.v2x_latency,
            'sla_compliance': self.sla_compliance,
            'sensing_accuracy': self.sensing_accuracy,
            'reliability': self.reliability,
            'slices_active': self.slices_active,
            'edges_online': self.edges_online,
            'alerts_count': self.alerts_count,
            'active_agvs': self.active_agvs,
            'bandwidth_usage_mbps': self.bandwidth_usage_mbps,
            'network_load_pct': self.network_load_pct,
            'pending_tasks': self.pending_tasks,
            'completed_tasks': self.completed_tasks,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


# ============================================
# 仓库场景新增表
# ============================================

class AGVTask(db.Model):
    """AGV调度任务表 —— 网络调度核心"""
    __tablename__ = 'agv_tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    task_type = db.Column(db.String(30), nullable=False)  # transport / retrieve / store / charge / sort
    source_zone_id = db.Column(db.Integer, db.ForeignKey('production_lines.id'))
    target_zone_id = db.Column(db.Integer, db.ForeignKey('production_lines.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))  # 执行的AGV
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))  # 关联订单
    priority = db.Column(db.Integer, default=3)  # 1(critical)-5(normal)
    network_slice_id = db.Column(db.Integer, db.ForeignKey('network_slices.id'))  # 关联URLLC切片
    latency_requirement_ms = db.Column(db.Float, default=10.0)  # 时延要求(ms)
    actual_latency_ms = db.Column(db.Float)  # 实际时延(ms)
    distance_m = db.Column(db.Float)  # 搬运距离(米)
    weight_kg = db.Column(db.Float)  # 货物重量(kg)
    status = db.Column(db.String(20), default='pending')  # pending / dispatched / in_progress / completed / failed
    dispatched_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    source_zone = db.relationship('ProductionLine', foreign_keys=[source_zone_id])
    target_zone = db.relationship('ProductionLine', foreign_keys=[target_zone_id])
    device = db.relationship('Device', foreign_keys=[device_id])
    order = db.relationship('Order', foreign_keys=[order_id])
    network_slice = db.relationship('NetworkSlice', foreign_keys=[network_slice_id])

    def to_dict(self):
        return {
            'id': self.id,
            'task_no': self.task_no,
            'task_type': self.task_type,
            'source_zone_id': self.source_zone_id,
            'source_zone_name': self.source_zone.name if self.source_zone else None,
            'target_zone_id': self.target_zone_id,
            'target_zone_name': self.target_zone.name if self.target_zone else None,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'order_id': self.order_id,
            'priority': self.priority,
            'network_slice_id': self.network_slice_id,
            'network_slice_name': self.network_slice.name if self.network_slice else None,
            'latency_requirement_ms': self.latency_requirement_ms,
            'actual_latency_ms': self.actual_latency_ms,
            'distance_m': self.distance_m,
            'weight_kg': self.weight_kg,
            'status': self.status,
            'dispatched_at': self.dispatched_at.isoformat() if self.dispatched_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NetworkLoadEvent(db.Model):
    """网络负载事件表 —— 网络调度监控"""
    __tablename__ = 'network_load_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(30), nullable=False)  # peak / congestion / normal / failure / recovery
    zone_id = db.Column(db.Integer, db.ForeignKey('production_lines.id'))
    slice_id = db.Column(db.Integer, db.ForeignKey('network_slices.id'))
    active_agvs = db.Column(db.Integer, default=0)
    bandwidth_usage_mbps = db.Column(db.Float)
    latency_ms = db.Column(db.Float)
    packet_loss_rate = db.Column(db.Float)
    severity = db.Column(db.String(20), default='normal')  # critical / warning / normal
    description = db.Column(db.Text)
    triggered_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    resolved_at = db.Column(db.DateTime)

    zone = db.relationship('ProductionLine', foreign_keys=[zone_id])
    slice = db.relationship('NetworkSlice', foreign_keys=[slice_id])

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'zone_id': self.zone_id,
            'zone_name': self.zone.name if self.zone else None,
            'slice_id': self.slice_id,
            'slice_name': self.slice.name if self.slice else None,
            'active_agvs': self.active_agvs,
            'bandwidth_usage_mbps': self.bandwidth_usage_mbps,
            'latency_ms': self.latency_ms,
            'packet_loss_rate': self.packet_loss_rate,
            'severity': self.severity,
            'description': self.description,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }