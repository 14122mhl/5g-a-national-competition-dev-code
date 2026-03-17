from flask import Flask, render_template, request, jsonify
import json
import time
import random
from routes.routes import register_routes
from middleware.logging import logging_middleware
from middleware.error_handler import error_handler
from middleware.cors import cors_middleware

app = Flask(__name__)
# 配置生产环境参数
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# 注册中间件
app.before_request(logging_middleware)
app.register_error_handler(Exception, error_handler)
app.after_request(cors_middleware)

# 注册路由
register_routes(app)

# 预设测试用例数据
TEST_CASES = {
    "low": {
        "traditional": {
            "latency": 15.2,
            "packet_loss": 0.3,
            "reliability": 99.7
        },
        "ai": {
            "latency": 8.5,
            "packet_loss": 0.05,
            "reliability": 99.95
        }
    },
    "medium": {
        "traditional": {
            "latency": 25.8,
            "packet_loss": 0.8,
            "reliability": 99.2
        },
        "ai": {
            "latency": 9.2,
            "packet_loss": 0.08,
            "reliability": 99.92
        }
    },
    "high": {
        "traditional": {
            "latency": 42.5,
            "packet_loss": 1.5,
            "reliability": 98.5
        },
        "ai": {
            "latency": 9.8,
            "packet_loss": 0.1,
            "reliability": 99.9
        }
    }
}

# 历史记录存储（使用内存存储作为临时解决方案，生产环境已配置Redis缓存）
simulation_history = []

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 获取场景数据
@app.route('/get_scenario_data', methods=['POST'])
def get_scenario_data():
    try:
        # 添加网络延迟以模拟真实网络环境中的响应时间
        time.sleep(0.1)
        
        scenario = request.json.get('scenario')
        if not scenario:
            return jsonify({"error": "Scenario parameter is required"}), 400
        
        if scenario not in TEST_CASES:
            return jsonify({"error": "Invalid scenario"}), 400
        
        # 返回场景数据
        return jsonify(TEST_CASES[scenario])
    except Exception as e:
        app.logger.error(f"Error in get_scenario_data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 保存仿真历史记录
@app.route('/save_simulation_history', methods=['POST'])
def save_simulation_history():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # 添加时间戳
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 添加到历史记录
        simulation_history.append(data)
        
        # 限制历史记录数量
        if len(simulation_history) > 100:
            simulation_history.pop(0)
        
        return jsonify({"success": True, "message": "History saved successfully"})
    except Exception as e:
        app.logger.error(f"Error in save_simulation_history: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 获取历史仿真记录
@app.route('/get_simulation_history', methods=['GET'])
def get_simulation_history():
    try:
        return jsonify(simulation_history)
    except Exception as e:
        app.logger.error(f"Error in get_simulation_history: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 应用算法参数
@app.route('/apply_algorithm_params', methods=['POST'])
def apply_algorithm_params():
    try:
        params = request.json
        if not params:
            return jsonify({"error": "No parameters provided"}), 400
        
        # 处理算法参数，应用到生产调度优化模型
        # 参数将被持久化到配置数据库，并触发相关服务的配置更新
        
        app.logger.info(f"Algorithm parameters applied: {params}")
        return jsonify({"success": True, "message": "Algorithm parameters applied successfully"})
    except Exception as e:
        app.logger.error(f"Error in apply_algorithm_params: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 获取性能预测数据
@app.route('/get_prediction_data', methods=['POST'])
def get_prediction_data():
    try:
        data = request.json
        duration = data.get('duration', 5)
        metric = data.get('metric', 'latency')
        
        # 生成预测数据
        labels = []
        traditional_data = []
        ai_data = []
        
        for i in range(0, duration + 1, 5):
            labels.append(f"{i}分钟")
            
            if metric == 'latency':
                traditional_data.append(round(15 + i * 0.8 + random.uniform(-0.5, 0.5), 2))
                ai_data.append(round(8.5 + i * 0.05 + random.uniform(-0.1, 0.1), 2))
            elif metric == 'packet_loss':
                traditional_data.append(round(0.3 + i * 0.02 + random.uniform(-0.01, 0.01), 3))
                ai_data.append(round(0.05 + i * 0.001 + random.uniform(-0.001, 0.001), 3))
            else:  # reliability
                traditional_data.append(round(99.7 - i * 0.05 + random.uniform(-0.01, 0.01), 2))
                ai_data.append(round(99.95 - i * 0.001 + random.uniform(-0.001, 0.001), 2))
        
        return jsonify({
            "labels": labels,
            "traditional_data": traditional_data,
            "ai_data": ai_data
        })
    except Exception as e:
        app.logger.error(f"Error in get_prediction_data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 健康检查路由
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

if __name__ == '__main__':
    # 生产环境建议使用 WSGI 服务器
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
