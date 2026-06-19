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
    """产品表"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(20), default='台')
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active / inactive / discontinued
    min_stock = db.Column(db.Integer, default=10)
    max_stock = db.Column(db.Integer, default=500)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'category': self.category,
            'price': round(self.price, 2),
            'quantity': self.quantity,
            'unit': self.unit,
            'description': self.description,
            'status': self.status,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Order(db.Model):
    """订单表"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending / processing / completed / cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'total_amount': round(self.total_amount, 2),
            'status': self.status,
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
    """生产线表"""
    __tablename__ = 'production_lines'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # assembly / machining / packaging / testing
    status = db.Column(db.String(20), nullable=False, default='idle')  # idle / running / maintenance / offline
    capacity = db.Column(db.Integer, nullable=False, default=100)  # 每小时产能
    efficiency = db.Column(db.Float, nullable=False, default=100.0)  # 效率百分比
    current_task = db.Column(db.String(100))
    location = db.Column(db.String(100))
    oee = db.Column(db.Float, default=85.0)  # 设备综合效率
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    devices = db.relationship('Device', backref='production_line', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'category': self.category,
            'status': self.status,
            'capacity': self.capacity,
            'efficiency': round(self.efficiency, 1),
            'current_task': self.current_task,
            'location': self.location,
            'oee': round(self.oee, 1) if self.oee else None,
            'device_count': self.devices.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Device(db.Model):
    """设备表"""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # sensor / robot / controller / conveyor / camera
    line_id = db.Column(db.Integer, db.ForeignKey('production_lines.id'), index=True)
    status = db.Column(db.String(20), nullable=False, default='online')  # online / offline / maintenance
    ip_address = db.Column(db.String(45))
    firmware_version = db.Column(db.String(20))
    last_maintenance = db.Column(db.DateTime)
    metrics_json = db.Column(db.Text)  # JSON格式存储设备运行指标
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

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
            'line_id': self.line_id,
            'line_name': self.production_line.name if self.production_line else None,
            'status': self.status,
            'ip_address': self.ip_address,
            'firmware_version': self.firmware_version,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
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
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }