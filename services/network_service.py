# ============================================
# 网络服务 - 数据库版本
# 管理网络切片和边缘节点
# ============================================

import logging
import random
from datetime import datetime
from database import db
from models.db_models import NetworkSlice, EdgeNode, SimulationRecord, DashboardMetric

logger = logging.getLogger(__name__)


class NetworkService:

    # --- 网络切片 ---
    def get_all_slices(self, slice_type=None, status=None, search=None):
        query = NetworkSlice.query
        if slice_type:
            query = query.filter_by(slice_type=slice_type)
        if status:
            query = query.filter_by(status=status)
        slices = query.all()
        if search:
            search = search.lower()
            slices = [s for s in slices if search in s.name.lower() or (s.description and search in s.description.lower())]
        return [s.to_dict() for s in slices]

    def get_slice_by_id(self, slice_id):
        s = NetworkSlice.query.get(slice_id)
        return s.to_dict() if s else None

    def create_slice(self, data):
        s = NetworkSlice(
            name=data['name'],
            slice_type=data.get('type', 'civil'),
            size=int(data.get('size', 100)),
            description=data.get('description', ''),
            status='active',
            latency=float(data.get('latency', 10.0)),
            bandwidth=int(data.get('bandwidth', 200)),
            sla_compliance=float(data.get('sla_compliance', 99.9))
        )
        db.session.add(s)
        db.session.commit()
        logger.info(f"创建网络切片: {s.name} (ID:{s.id})")
        return s.to_dict()

    def update_slice(self, slice_id, data):
        s = NetworkSlice.query.get(slice_id)
        if not s:
            return None

        for field in ['name', 'description', 'status']:
            if field in data:
                setattr(s, field, data[field])
        if 'type' in data:
            s.slice_type = data['type']
        if 'size' in data:
            s.size = int(data['size'])
        if 'latency' in data:
            s.latency = float(data['latency'])
        if 'bandwidth' in data:
            s.bandwidth = int(data['bandwidth'])
        if 'sla_compliance' in data:
            s.sla_compliance = float(data['sla_compliance'])

        db.session.commit()
        logger.info(f"更新网络切片: {s.name} (ID:{slice_id})")
        return s.to_dict()

    def delete_slice(self, slice_id):
        s = NetworkSlice.query.get(slice_id)
        if not s:
            return None
        name = s.name
        db.session.delete(s)
        db.session.commit()
        logger.info(f"删除网络切片: {name} (ID:{slice_id})")
        return name

    def batch_delete_slices(self, ids):
        deleted = []
        for sid in ids:
            name = self.delete_slice(sid)
            if name:
                deleted.append(name)
        return deleted

    # --- 边缘节点 ---
    def get_all_edge_nodes(self):
        nodes = EdgeNode.query.all()
        # 实时更新CPU/内存（模拟真实设备波动）
        for node in nodes:
            if node.status == 'online':
                node.cpu = round(min(100, node.cpu + random.uniform(-5, 5)), 1)
                node.memory = round(min(100, node.memory + random.uniform(-3, 3)), 1)
        db.session.commit()
        return [n.to_dict() for n in nodes]

    def get_edge_node_tasks(self, node_id):
        node = EdgeNode.query.get(node_id)
        if not node:
            return None
        tasks = [
            {"id": i + 1, "name": f"推理任务-{i + 1}",
             "model": random.choice(["YOLOv8", "ResNet", "BERT", "LSTM"]),
             "status": random.choice(["running", "completed", "queued"]),
             "latency": round(random.uniform(2, 15), 1),
             "throughput": random.randint(10, 200)}
            for i in range(random.randint(3, 8))
        ]
        return {"node": node.to_dict(), "tasks": tasks}

    # --- 仿真记录 ---
    def get_simulation_history(self, limit=20):
        records = SimulationRecord.query.order_by(SimulationRecord.created_at.desc()).limit(limit).all()
        return [r.to_dict() for r in records]

    def clear_simulation_history(self):
        SimulationRecord.query.delete()
        db.session.commit()
        logger.info("仿真历史记录已清空")

    def save_simulation_record(self, scenario, slice_type, result_json, task_count,
                               latency_improvement, throughput_improvement, energy_saving):
        record = SimulationRecord(
            scenario=scenario,
            slice_type=slice_type,
            result_json=result_json,
            task_count=task_count,
            latency_improvement=latency_improvement,
            throughput_improvement=throughput_improvement,
            energy_saving=energy_saving
        )
        db.session.add(record)
        db.session.commit()
        return record.to_dict()

    # --- 仪表盘指标 ---
    def get_dashboard_metrics(self):
        slices = NetworkSlice.query.filter_by(status='active').all()
        edges = EdgeNode.query.filter_by(status='online').all()

        metric = DashboardMetric(
            air_peak_rate=f"{round(random.uniform(9.5, 10.5), 1)} Gbps",
            uplink_peak_rate=f"{round(random.uniform(0.9, 1.1), 1)} Gbps",
            urllc_latency=f"{round(random.uniform(0.8, 1.2), 1)} ms",
            v2x_latency=f"{round(random.uniform(4.5, 5.5), 1)} ms",
            sla_compliance=f"{round(99.95 + random.random() * 0.04, 2)}%",
            sensing_accuracy=f"{round(98.0 + random.random() * 2, 1)}%",
            reliability=f"{round(99.99 + random.random() * 0.009, 4)}%",
            slices_active=len(slices),
            edges_online=len(edges),
            alerts_count=random.randint(0, 3)
        )
        db.session.add(metric)
        db.session.commit()

        return {
            "network": {
                "air_peak_rate": metric.air_peak_rate,
                "uplink_peak_rate": metric.uplink_peak_rate,
                "urllc_latency": metric.urllc_latency,
                "v2x_latency": metric.v2x_latency,
                "sla_compliance": metric.sla_compliance,
                "sensing_accuracy": metric.sensing_accuracy,
                "reliability": metric.reliability
            },
            "slices": {"total": NetworkSlice.query.count(), "active": metric.slices_active},
            "edge_nodes": {"total": EdgeNode.query.count(), "online": metric.edges_online},
            "alerts": metric.alerts_count,
            "timestamp": datetime.now().isoformat()
        }

    def get_network_status(self):
        slices = NetworkSlice.query.filter_by(status='active').all()
        edges = EdgeNode.query.filter_by(status='online').all()
        return {
            "network_nodes": len(edges),
            "online_nodes": len(edges),
            "active_slices": len(slices),
            "packet_loss_rate": round(random.uniform(0.01, 0.08), 3),
            "average_latency": round(random.uniform(1.5, 3.5), 1),
            "bandwidth_utilization": round(random.uniform(45, 75), 1)
        }


network_service = NetworkService()