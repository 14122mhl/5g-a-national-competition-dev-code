import sqlite3
import os
import threading
import math
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metrics.db')


class MetricsStore:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._local = threading.local()
        self._init_db()

    def _get_conn(self):
        """线程安全的连接获取"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self):
        """创建表结构"""
        conn = self._get_conn()
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS network_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                timestamp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sensing_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS edge_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id INTEGER NOT NULL,
                cpu REAL NOT NULL,
                memory REAL NOT NULL,
                tasks INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                response_time REAL,
                timestamp TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_network_ts ON network_metrics(metric_name, timestamp);
            CREATE INDEX IF NOT EXISTS idx_sensing_ts ON sensing_metrics(sensor_type, metric_name, timestamp);
            CREATE INDEX IF NOT EXISTS idx_edge_ts ON edge_metrics(node_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_access_ts ON access_log(timestamp);
        ''')
        conn.commit()

    def record_network_metric(self, metric_name, value, unit=None, timestamp=None):
        """记录网络指标"""
        ts = timestamp or datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO network_metrics (metric_name, value, unit, timestamp) VALUES (?, ?, ?, ?)",
            (metric_name, value, unit, ts)
        )
        conn.commit()

    def record_sensing_metric(self, sensor_type, metric_name, value, timestamp=None):
        """记录感知指标"""
        ts = timestamp or datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO sensing_metrics (sensor_type, metric_name, value, timestamp) VALUES (?, ?, ?, ?)",
            (sensor_type, metric_name, value, ts)
        )
        conn.commit()

    def record_edge_metric(self, node_id, cpu, memory, tasks, timestamp=None):
        """记录边缘节点指标"""
        ts = timestamp or datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO edge_metrics (node_id, cpu, memory, tasks, timestamp) VALUES (?, ?, ?, ?, ?)",
            (node_id, cpu, memory, tasks, ts)
        )
        conn.commit()

    def record_access(self, endpoint, method, response_time, timestamp=None):
        """记录API访问"""
        ts = timestamp or datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO access_log (endpoint, method, response_time, timestamp) VALUES (?, ?, ?, ?)",
            (endpoint, method, response_time, ts)
        )
        conn.commit()

    def get_network_trend(self, metric_name, hours=24):
        """获取网络指标趋势"""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT timestamp, value FROM network_metrics WHERE metric_name=? AND timestamp>=? ORDER BY timestamp",
            (metric_name, since)
        ).fetchall()
        return rows

    def get_sensing_trend(self, sensor_type, metric_name, hours=24):
        """获取感知指标趋势"""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT timestamp, value FROM sensing_metrics WHERE sensor_type=? AND metric_name=? AND timestamp>=? ORDER BY timestamp",
            (sensor_type, metric_name, since)
        ).fetchall()
        return rows

    def get_edge_trend(self, node_id, hours=24):
        """获取边缘节点趋势"""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT timestamp, cpu, memory, tasks FROM edge_metrics WHERE node_id=? AND timestamp>=? ORDER BY timestamp",
            (node_id, since)
        ).fetchall()
        return rows

    def get_latest_network(self, metric_name):
        """获取最新网络指标值"""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT value, timestamp FROM network_metrics WHERE metric_name=? ORDER BY timestamp DESC LIMIT 1",
            (metric_name,)
        ).fetchone()
        return row

    def get_latest_edge(self, node_id):
        """获取最新边缘节点状态"""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT cpu, memory, tasks, timestamp FROM edge_metrics WHERE node_id=? ORDER BY timestamp DESC LIMIT 1",
            (node_id,)
        ).fetchone()
        return row

    def get_latest_sensing(self, sensor_type, metric_name):
        """获取最新感知指标"""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT value, timestamp FROM sensing_metrics WHERE sensor_type=? AND metric_name=? ORDER BY timestamp DESC LIMIT 1",
            (sensor_type, metric_name)
        ).fetchone()
        return row

    def get_access_stats(self):
        """获取访问统计"""
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) FROM access_log").fetchone()[0]
        today = conn.execute(
            "SELECT COUNT(*) FROM access_log WHERE timestamp >= ?",
            (datetime.now().replace(hour=0, minute=0, second=0).isoformat(),)
        ).fetchone()[0]
        avg_time = conn.execute("SELECT AVG(response_time) FROM access_log").fetchone()[0] or 0
        return {"total_requests": total, "today_requests": today, "avg_response_time": round(avg_time, 2)}

    def get_data_count(self):
        """获取数据点总数"""
        conn = self._get_conn()
        n = conn.execute("SELECT COUNT(*) FROM network_metrics").fetchone()[0]
        s = conn.execute("SELECT COUNT(*) FROM sensing_metrics").fetchone()[0]
        e = conn.execute("SELECT COUNT(*) FROM edge_metrics").fetchone()[0]
        return n + s + e

    def is_seeded(self):
        """检查是否已播种"""
        conn = self._get_conn()
        count = conn.execute("SELECT COUNT(*) FROM network_metrics").fetchone()[0]
        return count > 100

    def seed_historical_data(self):
        """播种7天历史数据"""
        if self.is_seeded():
            return

        now = datetime.now()
        # 每5分钟一个数据点，7天 = 7*24*12 = 2016个点
        points = 7 * 24 * 12

        conn = self._get_conn()

        # 网络指标播种
        network_configs = {
            'air_peak_rate': {'base': 10.0, 'amplitude': 0.3, 'noise': 0.1, 'unit': 'Gbps'},
            'uplink_peak_rate': {'base': 1.0, 'amplitude': 0.05, 'noise': 0.02, 'unit': 'Gbps'},
            'urllc_latency': {'base': 1.0, 'amplitude': 0.15, 'noise': 0.05, 'unit': 'ms'},
            'v2x_latency': {'base': 5.0, 'amplitude': 0.3, 'noise': 0.1, 'unit': 'ms'},
            'sla_compliance': {'base': 99.97, 'amplitude': 0.01, 'noise': 0.005, 'unit': '%'},
            'sensing_accuracy': {'base': 99.0, 'amplitude': 0.5, 'noise': 0.2, 'unit': '%'},
            'reliability': {'base': 99.995, 'amplitude': 0.002, 'noise': 0.001, 'unit': '%'},
        }

        for metric_name, cfg in network_configs.items():
            batch = []
            for i in range(points):
                ts = now - timedelta(minutes=(points - i) * 5)
                hour = ts.hour + ts.minute / 60.0
                # 日周期: 白天高负载
                day_factor = 0.5 * math.sin(2 * math.pi * (hour - 6) / 24)
                # 周周期: 工作日高
                week_factor = 0.2 if ts.weekday() < 5 else -0.1
                # 随机噪声
                noise = random.gauss(0, cfg['noise'])
                # 异常注入 (0.5%)
                anomaly = cfg['amplitude'] * 3 * (1 if random.random() < 0.005 else 0) * random.choice([-1, 1])

                value = cfg['base'] + cfg['amplitude'] * day_factor + week_factor * cfg['amplitude'] + noise + anomaly

                # 对特定指标做约束
                if 'latency' in metric_name:
                    value = max(0.1, value)
                elif 'compliance' in metric_name or 'accuracy' in metric_name or 'reliability' in metric_name:
                    value = min(100.0, max(95.0, value))
                elif 'rate' in metric_name:
                    value = max(0.1, value)

                batch.append((metric_name, round(value, 4), cfg['unit'], ts.isoformat()))

            conn.executemany(
                "INSERT INTO network_metrics (metric_name, value, unit, timestamp) VALUES (?, ?, ?, ?)",
                batch
            )

        # 感知指标播种
        sensing_configs = {
            'temperature': {'precision': 99.5, 'distance': 500, 'refresh': 100},
            'person': {'precision': 99.0, 'distance': 300, 'refresh': 50},
            'device': {'precision': 99.5, 'distance': 400, 'refresh': 75},
            'environment': {'precision': 98.8, 'distance': 450, 'refresh': 80},
            'vibration': {'precision': 99.3, 'distance': 350, 'refresh': 120},
        }

        for sensor_type, cfg in sensing_configs.items():
            batch = []
            for i in range(points):
                ts = now - timedelta(minutes=(points - i) * 5)
                noise_p = random.gauss(0, 0.2)
                noise_d = random.gauss(0, 10)
                noise_r = random.gauss(0, 5)
                batch.append((sensor_type, 'precision', round(cfg['precision'] + noise_p, 2), ts.isoformat()))
                batch.append((sensor_type, 'distance', round(cfg['distance'] + noise_d, 1), ts.isoformat()))
                batch.append((sensor_type, 'refresh_rate', round(cfg['refresh'] + noise_r, 1), ts.isoformat()))

            conn.executemany(
                "INSERT INTO sensing_metrics (sensor_type, metric_name, value, timestamp) VALUES (?, ?, ?, ?)",
                batch
            )

        # 边缘节点播种
        edge_configs = {
            1: {'cpu_base': 45, 'mem_base': 62, 'tasks_base': 12},
            2: {'cpu_base': 33, 'mem_base': 48, 'tasks_base': 8},
            3: {'cpu_base': 78, 'mem_base': 85, 'tasks_base': 25},
        }

        for node_id, cfg in edge_configs.items():
            batch = []
            for i in range(points):
                ts = now - timedelta(minutes=(points - i) * 5)
                hour = ts.hour + ts.minute / 60.0
                day_factor = 0.3 * math.sin(2 * math.pi * (hour - 6) / 24)
                cpu = cfg['cpu_base'] + day_factor * 15 + random.gauss(0, 3)
                mem = cfg['mem_base'] + day_factor * 8 + random.gauss(0, 2)
                tasks = max(1, int(cfg['tasks_base'] + day_factor * 5 + random.gauss(0, 2)))
                batch.append((node_id, round(min(100, max(5, cpu)), 1), round(min(100, max(10, mem)), 1), tasks, ts.isoformat()))

            conn.executemany(
                "INSERT INTO edge_metrics (node_id, cpu, memory, tasks, timestamp) VALUES (?, ?, ?, ?, ?)",
                batch
            )

        conn.commit()
