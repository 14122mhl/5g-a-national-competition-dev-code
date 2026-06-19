# ============================================
# 5G-A 确定性网络智能调度平台 v3.0
# 主应用程序入口 - 集成MySQL数据库和DeepSeek AI
# ============================================

from flask import Flask, request, jsonify, send_file, g
import time
import random
import uuid
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 数据库 - 必须在创建app后立即初始化
from database import db, init_database, check_db_connection

# 导入算法模块
from algorithms.scheduler import ProductionScheduler
from algorithms.predictor import PerformancePredictor
from algorithms.sensing import SensingProcessor
from algorithms.optimizer import NetworkOptimizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
app.config['START_TIME'] = time.time()

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'root')}"
    f"@{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}"
    f"/{os.getenv('DB_NAME', '5g_a_industry')}?charset=utf8mb4"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10, 'max_overflow': 20,
    'pool_recycle': 3600, 'pool_pre_ping': True,
}

# ===== 关键修复：创建app后立即注册db，确保所有线程和请求中db._app_engines可用 =====
db.init_app(app)

# 导入服务层（在db.init_app之后，确保model的metadata正确绑定）
from services.user_service import user_service
from services.product_service import product_service
from services.order_service import order_service
from services.production_service import production_service
from services.device_service import device_service
from services.network_service import network_service
from services.ai_agent import ai_agent

# 初始化算法模块
production_scheduler = ProductionScheduler()
performance_predictor = PerformancePredictor()
sensing_processor = SensingProcessor()
network_optimizer = NetworkOptimizer()

# ============================================
# 中间件
# ============================================
@app.before_request
def before_request_handler():
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())[:8]
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
        logger.debug(f"[{g.request_id}] {request.method} {request.path} body={request.get_json(silent=True)}")


@app.after_request
def after_request_handler(response):
    elapsed = (time.time() - g.get('start_time', time.time())) * 1000
    response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
    response.headers['X-Response-Time'] = f"{elapsed:.2f}ms"
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    # 记录API访问日志到数据库
    try:
        from models.db_models import APIAccessLog
        log = APIAccessLog(
            endpoint=request.path,
            method=request.method,
            request_id=g.get('request_id', ''),
            response_time=round(elapsed, 2),
            status_code=response.status_code,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        logger.debug(f"API日志记录失败: {e}")

    logger.info(f"[{g.get('request_id', '?')}] {request.method} {request.path} -> {response.status_code} ({elapsed:.1f}ms)")
    return response


@app.errorhandler(405)
def method_not_allowed_handler(e):
    return jsonify({"success": False, "message": "请求方法不允许"}), 405


@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({"success": False, "message": "请求的资源不存在"}), 404


@app.errorhandler(Exception)
def global_error_handler(e):
    logger.error(f"未捕获异常: {e}", exc_info=True)
    return jsonify({"success": False, "message": "服务器内部错误", "error": str(e)}), 500


@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return '', 204


# ============================================
# 页面路由
# ============================================
@app.route('/')
def index():
    return send_file('dev.html')


@app.route('/health')
def health_check():
    db_ok, db_msg = check_db_connection()
    return jsonify({
        "status": "healthy",
        "version": "3.0.0",
        "database": {"connected": db_ok, "message": db_msg},
        "ai": ai_agent.get_ai_status(),
        "timestamp": datetime.now().isoformat(),
        "uptime": round(time.time() - app.config.get('START_TIME', time.time()), 1)
    })


# ============================================
# 用户认证 API
# ============================================
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')
    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400
    try:
        result = user_service.login(username, password)
        return jsonify({"success": True, "data": result, "message": "登录成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 401


@app.route('/api/users', methods=['GET'])
def get_users():
    users = user_service.get_all_users()
    return jsonify({"success": True, "data": users, "total": len(users)})


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True) or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400
    try:
        user = user_service.create_user(data)
        return jsonify({"success": True, "data": user, "message": "用户创建成功"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "用户不存在"}), 404
    return jsonify({"success": True, "data": user})


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    user = user_service.update_user(user_id, data)
    if not user:
        return jsonify({"success": False, "message": "用户不存在"}), 404
    return jsonify({"success": True, "data": user, "message": "用户更新成功"})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not user_service.delete_user(user_id):
        return jsonify({"success": False, "message": "用户不存在"}), 404
    return jsonify({"success": True, "message": "用户删除成功"})


# ============================================
# 产品管理 API
# ============================================
@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    status = request.args.get('status')
    products = product_service.get_all_products(category, status)
    return jsonify({"success": True, "data": products, "total": len(products)})


@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json(silent=True) or {}
    if not data.get('name') or not data.get('sku'):
        return jsonify({"success": False, "message": "产品名称和SKU不能为空"}), 400
    try:
        product = product_service.create_product(data)
        return jsonify({"success": True, "data": product, "message": "产品创建成功"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = product_service.get_product_by_id(product_id)
    if not product:
        return jsonify({"success": False, "message": "产品不存在"}), 404
    return jsonify({"success": True, "data": product})


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json(silent=True) or {}
    product = product_service.update_product(product_id, data)
    if not product:
        return jsonify({"success": False, "message": "产品不存在"}), 404
    return jsonify({"success": True, "data": product, "message": "产品更新成功"})


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if not product_service.delete_product(product_id):
        return jsonify({"success": False, "message": "产品不存在"}), 404
    return jsonify({"success": True, "message": "产品删除成功"})


# ============================================
# 订单管理 API
# ============================================
@app.route('/api/orders', methods=['GET'])
def get_orders():
    status = request.args.get('status')
    orders = order_service.get_all_orders(status)
    return jsonify({"success": True, "data": orders, "total": len(orders)})


@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 1)
    items = data.get('items', [])
    if not items:
        return jsonify({"success": False, "message": "订单项不能为空"}), 400
    try:
        order = order_service.create_order(user_id, items)
        return jsonify({"success": True, "data": order, "message": "订单创建成功"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({"success": False, "message": "订单不存在"}), 404
    return jsonify({"success": True, "data": order})


@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if not status:
        return jsonify({"success": False, "message": "状态不能为空"}), 400
    order = order_service.update_order_status(order_id, status)
    if not order:
        return jsonify({"success": False, "message": "订单不存在"}), 404
    return jsonify({"success": True, "data": order, "message": "订单状态更新成功"})


@app.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    try:
        if not order_service.cancel_order(order_id):
            return jsonify({"success": False, "message": "订单不存在"}), 404
        return jsonify({"success": True, "message": "订单取消成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ============================================
# 生产线管理 API
# ============================================
@app.route('/api/production/lines', methods=['GET'])
def get_production_lines():
    status = request.args.get('status')
    category = request.args.get('category')
    lines = production_service.get_all_lines(status, category)
    return jsonify({"success": True, "data": lines, "total": len(lines)})


@app.route('/api/production/lines', methods=['POST'])
def create_production_line():
    data = request.get_json(silent=True) or {}
    if not data.get('name') or not data.get('code'):
        return jsonify({"success": False, "message": "名称和编码不能为空"}), 400
    line = production_service.create_line(data)
    return jsonify({"success": True, "data": line, "message": "生产线创建成功"}), 201


@app.route('/api/production/lines/<int:line_id>', methods=['GET'])
def get_production_line(line_id):
    line = production_service.get_line_by_id(line_id)
    if not line:
        return jsonify({"success": False, "message": "生产线不存在"}), 404
    return jsonify({"success": True, "data": line})


@app.route('/api/production/lines/<int:line_id>', methods=['PUT'])
def update_production_line(line_id):
    data = request.get_json(silent=True) or {}
    line = production_service.update_line(line_id, data)
    if not line:
        return jsonify({"success": False, "message": "生产线不存在"}), 404
    return jsonify({"success": True, "data": line, "message": "生产线更新成功"})


@app.route('/api/production/lines/<int:line_id>', methods=['DELETE'])
def delete_production_line(line_id):
    if not production_service.delete_line(line_id):
        return jsonify({"success": False, "message": "生产线不存在"}), 404
    return jsonify({"success": True, "message": "生产线删除成功"})


@app.route('/api/production/stats', methods=['GET'])
def get_production_stats():
    stats = production_service.get_production_stats()
    return jsonify({"success": True, "data": stats})


# ============================================
# 设备管理 API
# ============================================
@app.route('/api/devices', methods=['GET'])
def get_devices():
    device_type = request.args.get('type')
    status = request.args.get('status')
    line_id = request.args.get('line_id', type=int)
    devices = device_service.get_all_devices(device_type, status, line_id)
    return jsonify({"success": True, "data": devices, "total": len(devices)})


@app.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = device_service.get_device_by_id(device_id)
    if not device:
        return jsonify({"success": False, "message": "设备不存在"}), 404
    return jsonify({"success": True, "data": device})


@app.route('/api/devices', methods=['POST'])
def create_device():
    data = request.get_json(silent=True) or {}
    if not data.get('name') or not data.get('code'):
        return jsonify({"success": False, "message": "名称和编码不能为空"}), 400
    device = device_service.create_device(data)
    return jsonify({"success": True, "data": device, "message": "设备创建成功"}), 201


@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    data = request.get_json(silent=True) or {}
    device = device_service.update_device(device_id, data)
    if not device:
        return jsonify({"success": False, "message": "设备不存在"}), 404
    return jsonify({"success": True, "data": device, "message": "设备更新成功"})


@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    if not device_service.delete_device(device_id):
        return jsonify({"success": False, "message": "设备不存在"}), 404
    return jsonify({"success": True, "message": "设备删除成功"})


@app.route('/api/devices/stats', methods=['GET'])
def get_device_stats():
    stats = device_service.get_device_stats()
    return jsonify({"success": True, "data": stats})


# ============================================
# 核心仪表盘 API
# ============================================
@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    metrics = network_service.get_dashboard_metrics()
    return jsonify({"success": True, "data": metrics})


@app.route('/api/dashboard/refresh', methods=['POST'])
def refresh_dashboard():
    return get_dashboard_metrics()


# ============================================
# 网络切片管理 API
# ============================================
@app.route('/api/slices', methods=['GET'])
def get_slices():
    slice_type = request.args.get('type')
    status = request.args.get('status')
    search = request.args.get('search')
    slices = network_service.get_all_slices(slice_type, status, search)
    return jsonify({"success": True, "data": slices, "total": len(slices)})


@app.route('/api/slices', methods=['POST'])
def create_slice():
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({"success": False, "message": "切片名称不能为空"}), 400
    s = network_service.create_slice(data)
    return jsonify({"success": True, "data": s, "message": "切片创建成功"}), 201


@app.route('/api/slices/<int:slice_id>', methods=['PUT'])
def update_slice(slice_id):
    data = request.get_json(silent=True) or {}
    s = network_service.update_slice(slice_id, data)
    if not s:
        return jsonify({"success": False, "message": "切片不存在"}), 404
    return jsonify({"success": True, "data": s, "message": "切片更新成功"})


@app.route('/api/slices/<int:slice_id>', methods=['DELETE'])
def delete_slice(slice_id):
    name = network_service.delete_slice(slice_id)
    if not name:
        return jsonify({"success": False, "message": "切片不存在"}), 404
    return jsonify({"success": True, "message": f"切片 '{name}' 删除成功"})


@app.route('/api/slices/batch-delete', methods=['POST'])
def batch_delete_slices():
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])
    if not ids:
        return jsonify({"success": False, "message": "请选择要删除的切片"}), 400
    deleted = network_service.batch_delete_slices(ids)
    return jsonify({"success": True, "message": f"成功删除 {len(deleted)} 个切片", "deleted": deleted})


# ============================================
# 通感一体 API
# ============================================
@app.route('/api/sensing/data', methods=['GET'])
def get_sensing_data():
    data = sensing_processor.get_sensing_data()
    env = sensing_processor.get_environment_data()
    return jsonify({"success": True, "data": {"sensing": data, "environment": env}})


@app.route('/api/sensing/filter', methods=['POST'])
def filter_sensing():
    req_data = request.get_json(silent=True) or {}
    sensing_type = req_data.get('type', 'temperature')
    result = sensing_processor.filter_sensing(sensing_type)
    if "error" in result:
        return jsonify({"success": False, "message": result["error"]}), 400
    return jsonify({"success": True, "data": result})


@app.route('/api/sensing/tracking', methods=['GET'])
def get_target_tracking():
    data = sensing_processor.get_target_tracking()
    return jsonify({"success": True, "data": data})


# ============================================
# 仿真调度 API
# ============================================
@app.route('/api/simulation/run', methods=['POST'])
def run_simulation():
    req_data = request.get_json(silent=True) or {}
    scenario = req_data.get('scenario', 'medium')
    slice_type = req_data.get('slice_type', 'industrial')

    if scenario not in ['low', 'medium', 'high']:
        return jsonify({"success": False, "message": "无效的场景类型"}), 400

    opt_result = network_optimizer.optimize_slice(slice_type, scenario)
    tasks = [
        {"id": i + 1, "name": f"任务-{i + 1}", "type": random.choice(["sensor", "robot", "controller", "conveyor"]),
         "workload": round(random.uniform(5, 30), 1), "priority": random.choice([1, 2, 3])}
        for i in range(random.randint(8, 15))
    ]
    schedule = production_scheduler.schedule(tasks)
    report = ai_agent.get_optimization_report(scenario)

    result = {**opt_result, "schedule": schedule, "ai_report": report}

    # 保存仿真记录到数据库
    network_service.save_simulation_record(
        scenario=scenario,
        slice_type=slice_type,
        result_json=json.dumps(result, ensure_ascii=False),
        task_count=len(tasks),
        latency_improvement=float(report.get('metrics', {}).get('latency_improvement', '0').replace('%', '')),
        throughput_improvement=float(report.get('metrics', {}).get('throughput_improvement', '0').replace('%', '')),
        energy_saving=float(report.get('metrics', {}).get('energy_saving', '0').replace('%', ''))
    )

    return jsonify({"success": True, "data": result})


@app.route('/api/simulation/history', methods=['GET'])
def get_simulation_history():
    limit = request.args.get('limit', 20, type=int)
    records = network_service.get_simulation_history(limit)
    return jsonify({"success": True, "data": records, "total": len(records)})


@app.route('/api/simulation/history', methods=['DELETE'])
def clear_simulation_history():
    network_service.clear_simulation_history()
    return jsonify({"success": True, "message": "历史记录已清空"})


# ============================================
# 性能预测 API
# ============================================
@app.route('/api/prediction/performance', methods=['POST'])
def predict_performance():
    req_data = request.get_json(silent=True) or {}
    duration = req_data.get('duration', 30)
    metric = req_data.get('metric', 'latency')
    result = performance_predictor.predict(duration, metric)
    return jsonify({"success": True, "data": result})


@app.route('/api/prediction/demand', methods=['POST'])
def predict_demand():
    req_data = request.get_json(silent=True) or {}
    product_type = req_data.get('product_type', 'sensor')
    horizon = req_data.get('horizon', 7)

    historical = [round(80 + i * 2.5 + random.uniform(-10, 10), 1) for i in range(30)]
    forecast = []
    last = historical[-1]
    for i in range(horizon):
        trend = (historical[-1] - historical[0]) / max(len(historical) - 1, 1)
        seasonal = 5 * (1 if i % 2 == 0 else -1)
        last = last + trend + seasonal + random.uniform(-5, 5)
        forecast.append(round(max(0, last), 1))

    return jsonify({"success": True, "data": {
        "product_type": product_type,
        "horizon": horizon,
        "historical": historical[-14:],
        "forecast": forecast,
        "confidence": round(85 + random.random() * 10, 1),
        "trend": "上升" if forecast[-1] > historical[-1] else "稳定"
    }})


# ============================================
# 设备与边缘算力 API
# ============================================
@app.route('/api/edge/nodes', methods=['GET'])
def get_edge_nodes():
    nodes = network_service.get_all_edge_nodes()
    return jsonify({"success": True, "data": nodes})


@app.route('/api/edge/nodes/<int:node_id>/tasks', methods=['GET'])
def get_edge_tasks(node_id):
    result = network_service.get_edge_node_tasks(node_id)
    if not result:
        return jsonify({"success": False, "message": "节点不存在"}), 404
    return jsonify({"success": True, "data": result})


# ============================================
# 算法参数管理 API
# ============================================
algorithm_params = {
    "priority_weight": 0.4,
    "load_weight": 0.35,
    "efficiency_weight": 0.25,
    "max_iterations": 100,
    "convergence_threshold": 0.01,
    "enable_ai_optimization": True
}


@app.route('/api/algorithm/params', methods=['GET'])
def get_algorithm_params():
    return jsonify({"success": True, "data": algorithm_params})


@app.route('/api/algorithm/params', methods=['PUT'])
def update_algorithm_params():
    data = request.get_json(silent=True) or {}
    for key in data:
        if key in algorithm_params:
            algorithm_params[key] = data[key]
    logger.info(f"算法参数已更新: {data}")
    return jsonify({"success": True, "data": algorithm_params, "message": "参数更新成功"})


# ============================================
# AI分析 API
# ============================================
@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    req_data = request.get_json(silent=True) or {}
    analysis_type = req_data.get('type', 'production')

    if analysis_type == 'production':
        result = ai_agent.analyze_production(req_data.get('data', {}))
    elif analysis_type == 'risk':
        net_data = network_service.get_network_status()
        result = ai_agent.analyze_risk(net_data)
    elif analysis_type == 'report':
        result = ai_agent.get_optimization_report(req_data.get('scenario', 'medium'))
    else:
        return jsonify({"success": False, "message": "不支持的分析类型"}), 400

    return jsonify({"success": True, "data": result})


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    status = ai_agent.get_ai_status()
    return jsonify({"success": True, "data": status})


@app.route('/api/ai/logs', methods=['GET'])
def get_ai_logs():
    limit = request.args.get('limit', 20, type=int)
    logs = ai_agent.get_analysis_logs(limit)
    return jsonify({"success": True, "data": logs, "total": len(logs)})


# ============================================
# API访问日志 API
# ============================================
@app.route('/api/logs/access', methods=['GET'])
def get_access_logs():
    from models.db_models import APIAccessLog
    limit = request.args.get('limit', 50, type=int)
    logs = APIAccessLog.query.order_by(APIAccessLog.timestamp.desc()).limit(limit).all()
    return jsonify({"success": True, "data": [l.to_dict() for l in logs], "total": len(logs)})


# ============================================
# 数据库状态 API
# ============================================
@app.route('/api/db/status', methods=['GET'])
def db_status():
    from models.db_models import (User, Product, Order, ProductionLine,
                                  Device, NetworkSlice, EdgeNode, SimulationRecord,
                                  AIAnalysisLog, DashboardMetric, APIAccessLog)
    db_ok, db_msg = check_db_connection()
    return jsonify({
        "success": True,
        "data": {
            "connected": db_ok,
            "message": db_msg,
            "tables": {
                "users": User.query.count(),
                "products": Product.query.count(),
                "orders": Order.query.count(),
                "production_lines": ProductionLine.query.count(),
                "devices": Device.query.count(),
                "network_slices": NetworkSlice.query.count(),
                "edge_nodes": EdgeNode.query.count(),
                "simulation_records": SimulationRecord.query.count(),
                "ai_analysis_logs": AIAnalysisLog.query.count(),
                "dashboard_metrics": DashboardMetric.query.count(),
                "api_access_logs": APIAccessLog.query.count()
            }
        }
    })


# ============================================
# 应用启动
# ============================================
if __name__ == '__main__':
    # db.init_app(app) 已在模块级调用，此处不再重复
    app.config['START_TIME'] = time.time()

    # 初始化数据库
    try:
        init_database(app)
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        logger.warning("将使用降级模式运行（部分功能不可用）")

    # 插入种子数据
    try:
        from seed_data import seed_all
        with app.app_context():
            seed_all()
    except Exception as e:
        logger.warning(f"种子数据插入失败: {e}")

    logger.info("=" * 50)
    logger.info("5G-A 确定性网络智能调度平台 v3.0")
    logger.info("数据库: MySQL (pymysql)")
    logger.info("AI引擎: DeepSeek")
    logger.info("启动成功，访问 http://127.0.0.1:5000")
    logger.info("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)