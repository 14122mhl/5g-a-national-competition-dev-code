# 5G-A 确定性网络智能调度仿真平台
# 主应用程序入口

from flask import Flask, request, jsonify, send_file, g
import time
import random
import uuid
import logging
from datetime import datetime

# 导入算法模块
from algorithms.scheduler import ProductionScheduler
from algorithms.predictor import PerformancePredictor
from algorithms.sensing import SensingProcessor
from algorithms.optimizer import NetworkOptimizer

# 导入AI服务
from services.ai_agent import ai_agent

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

# 初始化算法模块
production_scheduler = ProductionScheduler()
performance_predictor = PerformancePredictor()
sensing_processor = SensingProcessor()
network_optimizer = NetworkOptimizer()

# ============================================
# 数据存储（内存）
# ============================================
network_slices = [
    {"id": 1, "name": "工业控制切片", "type": "industrial", "size": 100,
     "description": "用于工业生产控制的URLLC切片，保障超低时延", "status": "active",
     "latency": 1.0, "bandwidth": 1000, "created_at": "2026-01-15 09:00:00"},
    {"id": 2, "name": "车联网切片", "type": "vehicle", "size": 200,
     "description": "智能交通车联网切片，支持V2X通信", "status": "active",
     "latency": 5.0, "bandwidth": 500, "created_at": "2026-01-15 09:30:00"},
    {"id": 3, "name": "民生服务切片", "type": "civil", "size": 150,
     "description": "公共服务民生切片，保障基础通信需求", "status": "active",
     "latency": 10.0, "bandwidth": 200, "created_at": "2026-01-15 10:00:00"},
]

simulation_history = []
algorithm_params = {
    "priority_weight": 0.4,
    "load_weight": 0.35,
    "efficiency_weight": 0.25,
    "max_iterations": 100,
    "convergence_threshold": 0.01,
    "enable_ai_optimization": True
}
edge_nodes = [
    {"id": 1, "name": "边缘节点-01", "location": "车间A", "cpu": 45.2, "memory": 62.1,
     "status": "online", "tasks": 12, "ip": "192.168.10.101"},
    {"id": 2, "name": "边缘节点-02", "location": "车间B", "cpu": 32.8, "memory": 48.5,
     "status": "online", "tasks": 8, "ip": "192.168.10.102"},
    {"id": 3, "name": "边缘节点-03", "location": "数据中心", "cpu": 78.5, "memory": 85.3,
     "status": "online", "tasks": 25, "ip": "192.168.10.103"},
]

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
    logger.info(f"[{g.get('request_id', '?')}] {request.method} {request.path} -> {response.status_code} ({elapsed:.1f}ms)")
    return response


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
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": round(time.time() - app.config.get('START_TIME', time.time()), 1)
    })

# ============================================# 核心仪表盘 API
# ============================================
@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """获取核心仪表盘实时指标"""
    net_status = network_optimizer.get_network_status()
    slices_active = sum(1 for s in network_slices if s["status"] == "active")
    edges_online = sum(1 for e in edge_nodes if e["status"] == "online")

    return jsonify({
        "success": True,
        "data": {
            "network": {
                "air_peak_rate": f"{round(random.uniform(9.5, 10.5), 1)} Gbps",
                "uplink_peak_rate": f"{round(random.uniform(0.9, 1.1), 1)} Gbps",
                "urllc_latency": f"{round(random.uniform(0.8, 1.2), 1)} ms",
                "v2x_latency": f"{round(random.uniform(4.5, 5.5), 1)} ms",
                "sla_compliance": f"{round(99.95 + random.random() * 0.04, 2)}%",
                "sensing_accuracy": f"{round(98.0 + random.random() * 2, 1)}%",
                "reliability": f"{round(99.99 + random.random() * 0.009, 4)}%"
            },
            "slices": {"total": len(network_slices), "active": slices_active},
            "edge_nodes": {"total": len(edge_nodes), "online": edges_online},
            "alerts": random.randint(0, 3),
            "timestamp": datetime.now().isoformat()
        }
    })


@app.route('/api/dashboard/refresh', methods=['POST'])
def refresh_dashboard():
    """刷新仪表盘数据"""
    return get_dashboard_metrics()


# ============================================
# 网络切片管理 API
# ============================================
@app.route('/api/slices', methods=['GET'])
def get_slices():
    """获取所有网络切片"""
    slice_type = request.args.get('type')
    status = request.args.get('status')
    search = request.args.get('search', '').lower()

    result = network_slices
    if slice_type:
        result = [s for s in result if s["type"] == slice_type]
    if status:
        result = [s for s in result if s["status"] == status]
    if search:
        result = [s for s in result if search in s["name"].lower() or search in s["description"].lower()]

    return jsonify({"success": True, "data": result, "total": len(result)})


@app.route('/api/slices', methods=['POST'])
def create_slice():
    """创建网络切片"""
    data = request.get_json(silent=True) or {}
    if not data or not data.get('name'):
        return jsonify({"success": False, "message": "切片名称不能为空"}), 400

    new_slice = {
        "id": len(network_slices) + 1,
        "name": data['name'],
        "type": data.get('type', 'civil'),
        "size": int(data.get('size', 100)),
        "description": data.get('description', ''),
        "status": "active",
        "latency": float(data.get('latency', 10.0)),
        "bandwidth": int(data.get('bandwidth', 200)),
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    network_slices.append(new_slice)
    logger.info(f"创建切片: {new_slice['name']} (ID:{new_slice['id']})")
    return jsonify({"success": True, "data": new_slice, "message": "切片创建成功"}), 201


@app.route('/api/slices/<int:slice_id>', methods=['PUT'])
def update_slice(slice_id):
    """更新网络切片"""
    data = request.get_json(silent=True) or {}
    for s in network_slices:
        if s["id"] == slice_id:
            if 'name' in data: s['name'] = data['name']
            if 'type' in data: s['type'] = data['type']
            if 'size' in data: s['size'] = int(data['size'])
            if 'description' in data: s['description'] = data['description']
            if 'status' in data: s['status'] = data['status']
            if 'latency' in data: s['latency'] = float(data['latency'])
            if 'bandwidth' in data: s['bandwidth'] = int(data['bandwidth'])
            logger.info(f"更新切片: {s['name']} (ID:{slice_id})")
            return jsonify({"success": True, "data": s, "message": "切片更新成功"})
    return jsonify({"success": False, "message": "切片不存在"}), 404


@app.route('/api/slices/<int:slice_id>', methods=['DELETE'])
def delete_slice(slice_id):
    """删除网络切片"""
    global network_slices
    for i, s in enumerate(network_slices):
        if s["id"] == slice_id:
            name = s["name"]
            network_slices.pop(i)
            logger.info(f"删除切片: {name} (ID:{slice_id})")
            return jsonify({"success": True, "message": f"切片 '{name}' 删除成功"})
    return jsonify({"success": False, "message": "切片不存在"}), 404


@app.route('/api/slices/batch-delete', methods=['POST'])
def batch_delete_slices():
    """批量删除网络切片"""
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])
    if not ids:
        return jsonify({"success": False, "message": "请选择要删除的切片"}), 400

    global network_slices
    deleted = []
    for sid in ids:
        for i, s in enumerate(network_slices):
            if s["id"] == sid:
                deleted.append(network_slices.pop(i)["name"])
                break
    logger.info(f"批量删除切片: {deleted}")
    return jsonify({"success": True, "message": f"成功删除 {len(deleted)} 个切片", "deleted": deleted})


# ============================================
# 通感一体 API
# ============================================
@app.route('/api/sensing/data', methods=['GET'])
def get_sensing_data():
    """获取通感一体感知数据"""
    data = sensing_processor.get_sensing_data()
    env = sensing_processor.get_environment_data()
    return jsonify({"success": True, "data": {"sensing": data, "environment": env}})


@app.route('/api/sensing/filter', methods=['POST'])
def filter_sensing():
    """筛选感知类型"""
    req_data = request.get_json(silent=True) or {}
    sensing_type = req_data.get('type', 'temperature')
    result = sensing_processor.filter_sensing(sensing_type)
    if "error" in result:
        return jsonify({"success": False, "message": result["error"]}), 400
    return jsonify({"success": True, "data": result})


@app.route('/api/sensing/tracking', methods=['GET'])
def get_target_tracking():
    """获取目标追踪数据"""
    data = sensing_processor.get_target_tracking()
    return jsonify({"success": True, "data": data})


# ============================================
# 仿真调度 API
# ============================================
@app.route('/api/simulation/run', methods=['POST'])
def run_simulation():
    """运行仿真调度"""
    req_data = request.get_json(silent=True) or {}
    scenario = req_data.get('scenario', 'medium')
    slice_type = req_data.get('slice_type', 'industrial')

    if scenario not in ['low', 'medium', 'high']:
        return jsonify({"success": False, "message": "无效的场景类型"}), 400

    opt_result = network_optimizer.optimize_slice(slice_type, scenario)
    tasks = [
        {"id": i+1, "name": f"任务-{i+1}", "type": random.choice(["sensor","robot","controller","conveyor"]),
         "workload": round(random.uniform(5, 30), 1), "priority": random.choice([1,2,3])}
        for i in range(random.randint(8, 15))
    ]
    schedule = production_scheduler.schedule(tasks)
    report = ai_agent.get_optimization_report(scenario)

    result = {
        **opt_result,
        "schedule": schedule,
        "ai_report": report
    }

    simulation_history.append({
        "id": len(simulation_history) + 1,
        "scenario": scenario,
        "slice_type": slice_type,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    if len(simulation_history) > 100:
        simulation_history.pop(0)

    return jsonify({"success": True, "data": result})


@app.route('/api/simulation/history', methods=['GET'])
def get_simulation_history():
    """获取仿真历史记录"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify({"success": True, "data": simulation_history[-limit:], "total": len(simulation_history)})


@app.route('/api/simulation/history', methods=['DELETE'])
def clear_simulation_history():
    """清空仿真历史"""
    global simulation_history
    simulation_history = []
    return jsonify({"success": True, "message": "历史记录已清空"})


# ============================================
# 性能预测 API
# ============================================
@app.route('/api/prediction/performance', methods=['POST'])
def predict_performance():
    """性能预测"""
    req_data = request.get_json(silent=True) or {}
    duration = req_data.get('duration', 30)
    metric = req_data.get('metric', 'latency')
    result = performance_predictor.predict(duration, metric)
    return jsonify({"success": True, "data": result})


@app.route('/api/prediction/demand', methods=['POST'])
def predict_demand():
    """需求预测"""
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
    """获取边缘节点列表"""
    for node in edge_nodes:
        if node["status"] == "online":
            node["cpu"] = round(min(100, node["cpu"] + random.uniform(-5, 5)), 1)
            node["memory"] = round(min(100, node["memory"] + random.uniform(-3, 3)), 1)
    return jsonify({"success": True, "data": edge_nodes})


@app.route('/api/edge/nodes/<int:node_id>/tasks', methods=['GET'])
def get_edge_tasks(node_id):
    """获取边缘节点任务列表"""
    for node in edge_nodes:
        if node["id"] == node_id:
            tasks = [
                {"id": i+1, "name": f"推理任务-{i+1}", "model": random.choice(["YOLOv8","ResNet","BERT","LSTM"]),
                 "status": random.choice(["running","completed","queued"]),
                 "latency": round(random.uniform(2, 15), 1), "throughput": random.randint(10, 200)}
                for i in range(random.randint(3, 8))
            ]
            return jsonify({"success": True, "data": {"node": node, "tasks": tasks}})
    return jsonify({"success": False, "message": "节点不存在"}), 404


# ============================================
# 算法参数管理 API
# ============================================
@app.route('/api/algorithm/params', methods=['GET'])
def get_algorithm_params():
    """获取算法参数"""
    return jsonify({"success": True, "data": algorithm_params})


@app.route('/api/algorithm/params', methods=['PUT'])
def update_algorithm_params():
    """更新算法参数"""
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
    """AI智能分析"""
    req_data = request.get_json(silent=True) or {}
    analysis_type = req_data.get('type', 'production')

    if analysis_type == 'production':
        result = ai_agent.analyze_production(req_data.get('data', {}))
    elif analysis_type == 'risk':
        net_data = network_optimizer.get_network_status()
        result = ai_agent.analyze_risk(net_data)
    elif analysis_type == 'report':
        result = ai_agent.get_optimization_report(req_data.get('scenario', 'medium'))
    else:
        return jsonify({"success": False, "message": "不支持的分析类型"}), 400

    return jsonify({"success": True, "data": result})


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """检查AI服务状态"""
    return jsonify({
        "success": True,
        "data": {
            "deepseek_enabled": ai_agent._is_api_available(),
            "algorithm_modules": ["scheduler", "predictor", "sensing", "optimizer"],
            "status": "ready"
        }
    })


# ============================================
# 应用启动
# ============================================
if __name__ == '__main__':
    app.config['START_TIME'] = time.time()
    logger.info("=" * 50)
    logger.info("5G-A 确定性网络智能调度仿真平台 v2.0")
    logger.info("启动成功，访问 http://127.0.0.1:5000")
    logger.info("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
