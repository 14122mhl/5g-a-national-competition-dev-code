import threading
import time
import math
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataCollector:
    """后台数据采集调度器 - 模拟真实传感器数据上报"""

    def __init__(self, store):
        self.store = store
        self.running = False
        self._thread = None
        self._tick = 0

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
        logger.info("数据采集调度器已启动")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _collect_loop(self):
        while self.running:
            try:
                self._collect_network()
                self._collect_sensing()
                self._collect_edge()
                self._tick += 1
            except Exception as e:
                logger.error(f"数据采集异常: {e}")
            time.sleep(10)

    def _time_factor(self):
        """基于当前时间的负载因子"""
        hour = datetime.now().hour + datetime.now().minute / 60.0
        # 日周期: 8:00-18:00高峰
        day = 0.5 * math.sin(2 * math.pi * (hour - 6) / 24)
        # 周周期
        weekday = datetime.now().weekday()
        week = 0.2 if weekday < 5 else -0.1
        return day + week

    def _collect_network(self):
        factor = self._time_factor()
        configs = {
            'air_peak_rate': (10.0, 0.3, 0.08, 'Gbps'),
            'uplink_peak_rate': (1.0, 0.05, 0.02, 'Gbps'),
            'urllc_latency': (1.0, 0.15, 0.04, 'ms'),
            'v2x_latency': (5.0, 0.3, 0.08, 'ms'),
            'sla_compliance': (99.97, 0.01, 0.003, '%'),
            'sensing_accuracy': (99.0, 0.5, 0.15, '%'),
            'reliability': (99.995, 0.002, 0.0008, '%'),
        }
        for metric, (base, amp, noise_std, unit) in configs.items():
            value = base + amp * factor + random.gauss(0, noise_std)
            # 异常注入
            if random.random() < 0.005:
                value += amp * 3 * random.choice([-1, 1])
            # 约束
            if 'latency' in metric:
                value = max(0.1, value)
            elif metric in ('sla_compliance', 'sensing_accuracy', 'reliability'):
                value = min(100.0, max(95.0, value))
            else:
                value = max(0.1, value)
            self.store.record_network_metric(metric, round(value, 4), unit)

    def _collect_sensing(self):
        configs = {
            'temperature': (99.5, 500, 100),
            'person': (99.0, 300, 50),
            'device': (99.5, 400, 75),
            'environment': (98.8, 450, 80),
            'vibration': (99.3, 350, 120),
        }
        for stype, (prec_base, dist_base, ref_base) in configs.items():
            self.store.record_sensing_metric(stype, 'precision', round(prec_base + random.gauss(0, 0.15), 2))
            self.store.record_sensing_metric(stype, 'distance', round(dist_base + random.gauss(0, 8), 1))
            self.store.record_sensing_metric(stype, 'refresh_rate', round(ref_base + random.gauss(0, 4), 1))

    def _collect_edge(self):
        factor = self._time_factor()
        configs = {
            1: (45, 62, 12),
            2: (33, 48, 8),
            3: (78, 85, 25),
        }
        for node_id, (cpu_base, mem_base, tasks_base) in configs.items():
            cpu = min(100, max(5, cpu_base + factor * 12 + random.gauss(0, 2.5)))
            mem = min(100, max(10, mem_base + factor * 6 + random.gauss(0, 1.5)))
            tasks = max(1, int(tasks_base + factor * 4 + random.gauss(0, 1.5)))
            self.store.record_edge_metric(node_id, round(cpu, 1), round(mem, 1), tasks)
