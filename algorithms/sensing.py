# 通感一体感知数据处理算法
# 从数据库SensingMetric表读取真实感知数据，数据库无数据时使用模拟算法

import math
import random
from datetime import datetime
from database import db

class SensingProcessor:
    """通感一体感知数据处理器"""

    def __init__(self):
        self.sensing_types = {
            "temperature": {"precision_base": 99.5, "distance_base": 500, "refresh_base": 100, "desc": "温度感知",
                           "icon": "thermometer", "color": "#ff6b6b",
                           "features": ["高精度红外测温", "±0.1°C分辨率", "多点阵列覆盖"],
                           "alert_types": ["温度过高告警", "温度骤变检测"]},
            "person": {"precision_base": 97.5, "distance_base": 200, "refresh_base": 30, "desc": "人员感知",
                      "icon": "person", "color": "#ffa502",
                      "features": ["毫米波人体检测", "跌倒行为识别", "密度统计"],
                      "alert_types": ["非法入侵检测", "人员聚集告警"]},
            "device": {"precision_base": 99.8, "distance_base": 800, "refresh_base": 200, "desc": "设备感知",
                      "icon": "cpu", "color": "#33b5ff",
                      "features": ["设备振动监测", "运行状态检测", "故障预警"],
                      "alert_types": ["设备异常振动", "运转速度异常"]},
            "environment": {"precision_base": 96.2, "distance_base": 1200, "refresh_base": 60, "desc": "环境感知",
                           "icon": "tree", "color": "#33ff88",
                           "features": ["多维环境参数", "气象联合感知", "污染检测"],
                           "alert_types": ["空气质量超标", "环境异常变化"]},
            "vibration": {"precision_base": 99.1, "distance_base": 150, "refresh_base": 500, "desc": "振动感知",
                         "icon": "activity", "color": "#a855f7",
                         "features": ["亚毫米级精度", "三轴加速度", "频谱分析"],
                         "alert_types": ["结构异常振动", "共振风险预警"]},
        }

    def get_sensing_data(self):
        """获取通感一体感知数据 - 优先从数据库读取"""
        from models.db_models import SensingMetric
        from sqlalchemy import func

        # 尝试从数据库获取最新感知数据
        try:
            latest_metrics = SensingMetric.query.filter(
                SensingMetric.timestamp >= datetime.now().replace(minute=0, second=0, microsecond=0)
            ).all()

            if latest_metrics:
                data = {}
                for stype in self.sensing_types:
                    type_metrics = [m for m in latest_metrics if m.sensor_type == stype]
                    if type_metrics:
                        precision_m = next((m for m in type_metrics if m.metric_name == 'precision'), None)
                        distance_m = next((m for m in type_metrics if m.metric_name == 'distance'), None)
                        refresh_m = next((m for m in type_metrics if m.metric_name == 'refresh_rate'), None)
                        data[stype] = {
                            "precision": precision_m.value if precision_m else round(self.sensing_types[stype]["precision_base"] + random.uniform(-0.3, 0.5), 2),
                            "distance": distance_m.value if distance_m else round(self.sensing_types[stype]["distance_base"] + random.uniform(-20, 20)),
                            "refresh_rate": refresh_m.value if refresh_m else round(self.sensing_types[stype]["refresh_base"] + random.uniform(-10, 10)),
                            "online_devices": random.randint(22, 24),
                            "total_devices": 24,
                            "signal_strength": round(-40 + random.uniform(-10, 5), 1),
                        }
                    else:
                        data[stype] = self._simulate_sensing(stype)
                return data
        except Exception as e:
            pass  # 数据库不可用时回退到模拟

        # 回退：模拟数据
        data = {}
        for stype in self.sensing_types:
            data[stype] = self._simulate_sensing(stype)
        return data

    def _simulate_sensing(self, stype):
        """模拟单个感知类型数据"""
        config = self.sensing_types[stype]
        return {
            "precision": round(config["precision_base"] + random.uniform(-0.3, 0.5), 2),
            "distance": round(config["distance_base"] + random.uniform(-20, 20)),
            "refresh_rate": round(config["refresh_base"] + random.uniform(-10, 10)),
            "online_devices": random.randint(22, 24),
            "total_devices": 24,
            "signal_strength": round(-40 + random.uniform(-10, 5), 1),
        }

    def filter_sensing(self, sensing_type):
        """根据感知类型筛选数据 - 优先从数据库读取"""
        if sensing_type not in self.sensing_types:
            return {"error": "不支持的感知类型", "available": list(self.sensing_types.keys())}

        config = self.sensing_types[sensing_type]

        # 尝试从数据库获取
        try:
            from models.db_models import SensingMetric
            type_metrics = SensingMetric.query.filter(
                SensingMetric.sensor_type == sensing_type,
                SensingMetric.timestamp >= datetime.now().replace(minute=0, second=0, microsecond=0)
            ).all()

            if type_metrics:
                precision_m = next((m for m in type_metrics if m.metric_name == 'precision'), None)
                distance_m = next((m for m in type_metrics if m.metric_name == 'distance'), None)
                refresh_m = next((m for m in type_metrics if m.metric_name == 'refresh_rate'), None)
                precision = precision_m.value if precision_m else round(config["precision_base"] + random.uniform(-0.3, 0.5), 2)
                distance = distance_m.value if distance_m else round(config["distance_base"] + random.uniform(-20, 20))
                refresh = refresh_m.value if refresh_m else round(config["refresh_base"] + random.uniform(-10, 10))
        except Exception:
            precision = round(config["precision_base"] + random.uniform(-0.3, 0.5), 2)
            distance = round(config["distance_base"] + random.uniform(-20, 20))
            refresh = round(config["refresh_base"] + random.uniform(-10, 10))

        # 设备在线率根据类型差异化
        online_rates = {"temperature": 100, "person": 95.8, "device": 100, "environment": 91.7, "vibration": 97.5}
        # 系统负载根据类型差异化
        load_bases = {"temperature": 25, "person": 45, "device": 30, "environment": 55, "vibration": 35}

        return {
            "type": sensing_type,
            "description": config["desc"],
            "icon": config.get("icon", "radar"),
            "color": config.get("color", "#33ff88"),
            "precision": precision,
            "precision_unit": "%",
            "distance": distance,
            "distance_unit": "m",
            "refresh_rate": refresh,
            "refresh_unit": "Hz",
            "coverage": round(95 + random.random() * 4.9, 1),
            "online_rate": online_rates.get(sensing_type, 100),
            "system_load": round(load_bases.get(sensing_type, 30) + random.random() * 10, 1),
            "alert_count": random.randint(0, 3),
            "features": config.get("features", []),
            "alert_types": config.get("alert_types", []),
            "device_count": {"online": random.randint(18, 24), "total": 24},
            "timestamp": datetime.now().isoformat()
        }

    def get_environment_data(self):
        """获取环境监测数据"""
        return {
            "temperature": round(22 + random.uniform(-3, 3), 1),
            "humidity": round(55 + random.uniform(-10, 10), 1),
            "pressure": round(1013 + random.uniform(-5, 5), 1),
            "vibration": round(0.1 + random.uniform(0, 0.3), 2),
            "noise_level": round(45 + random.uniform(-5, 10), 1),
            "air_quality": round(85 + random.uniform(-5, 14), 1),
            "timestamp": datetime.now().isoformat()
        }

    def get_target_tracking(self):
        """获取目标追踪数据"""
        return {
            "targets": [
                {
                    "id": i,
                    "type": random.choice(["person", "vehicle", "robot", "equipment"]),
                    "x": round(random.uniform(0, 500), 1),
                    "y": round(random.uniform(0, 500), 1),
                    "speed": round(random.uniform(0, 15), 1),
                    "direction": round(random.uniform(0, 360), 1),
                    "confidence": round(95 + random.random() * 4.9, 1)
                } for i in range(5)
            ],
            "timestamp": datetime.now().isoformat()
        }
