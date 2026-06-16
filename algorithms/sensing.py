# 通感一体感知数据处理算法
# 模拟5G-A通感融合感知环境下的数据采集和处理

import math
import random
from datetime import datetime

class SensingProcessor:
    """通感一体感知数据处理器"""

    def __init__(self):
        self.sensing_types = {
            "temperature": {"precision_base": 99.5, "distance_base": 500, "refresh_base": 100, "desc": "温度感知"},
            "person": {"precision_base": 99.0, "distance_base": 300, "refresh_base": 50, "desc": "人员感知"},
            "device": {"precision_base": 99.5, "distance_base": 400, "refresh_base": 75, "desc": "设备感知"},
            "environment": {"precision_base": 98.8, "distance_base": 450, "refresh_base": 80, "desc": "环境感知"},
            "vibration": {"precision_base": 99.3, "distance_base": 350, "refresh_base": 120, "desc": "振动感知"},
        }

    def get_sensing_data(self):
        """获取通感一体感知数据"""
        data = {}
        for stype, config in self.sensing_types.items():
            data[stype] = {
                "precision": round(config["precision_base"] + random.uniform(-0.3, 0.5), 2),
                "distance": round(config["distance_base"] + random.uniform(-20, 20)),
                "refresh_rate": round(config["refresh_base"] + random.uniform(-10, 10)),
                "online_devices": random.randint(22, 24),
                "total_devices": 24,
                "signal_strength": round(-40 + random.uniform(-10, 5), 1),
            }
        return data

    def filter_sensing(self, sensing_type):
        """根据感知类型筛选数据"""
        if sensing_type not in self.sensing_types:
            return {"error": "不支持的感知类型", "available": list(self.sensing_types.keys())}

        config = self.sensing_types[sensing_type]
        precision = round(config["precision_base"] + random.uniform(-0.3, 0.5), 2)
        distance = round(config["distance_base"] + random.uniform(-20, 20))
        refresh = round(config["refresh_base"] + random.uniform(-10, 10))

        return {
            "type": sensing_type,
            "description": config["desc"],
            "precision": precision,
            "precision_unit": "%",
            "distance": distance,
            "distance_unit": "m",
            "refresh_rate": refresh,
            "refresh_unit": "Hz",
            "coverage": round(95 + random.random() * 4.9, 1),
            "online_rate": 100,
            "system_load": round(25 + random.random() * 15, 1),
            "alert_count": random.randint(0, 2),
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
