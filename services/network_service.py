# ============================================
# 网络服务 - 数据库版本
# 管理网络切片和边缘节点
# ============================================

import logging
from datetime import datetime, timedelta
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
        return [n.to_dict() for n in nodes]

    def get_edge_node_tasks(self, node_id):
        node = EdgeNode.query.get(node_id)
        if not node:
            return None
        # 从数据库获取该节点区域的AGV任务
        from models.db_models import AGVTask
        tasks = AGVTask.query.filter(
            AGVTask.status.in_(['dispatched', 'in_progress']),
            AGVTask.created_at >= datetime.now() - timedelta(hours=24)
        ).order_by(AGVTask.priority).limit(8).all()
        return {
            "node": node.to_dict(),
            "tasks": [t.to_dict() for t in tasks] if tasks else []
        }

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
        # 从数据库读取最新仪表盘数据
        latest = DashboardMetric.query.order_by(DashboardMetric.timestamp.desc()).first()
        slices_active = NetworkSlice.query.filter_by(status='active').count()
        edges_online = EdgeNode.query.filter_by(status='online').count()
        agv_tasks_pending = 0
        try:
            from models.db_models import AGVTask
            agv_tasks_pending = AGVTask.query.filter_by(status='pending').count()
        except Exception:
            pass

        if latest:
            metric_data = latest.to_dict()
        else:
            # 无历史数据，从真实切片计算
            urllc = NetworkSlice.query.filter_by(slice_type='industrial').first()
            metric_data = {
                'air_peak_rate': '10.0 Gbps',
                'uplink_peak_rate': '1.0 Gbps',
                'urllc_latency': f'{urllc.latency} ms' if urllc else '1.0 ms',
                'v2x_latency': '5.0 ms',
                'sla_compliance': f'{urllc.sla_compliance}%' if urllc else '99.9%',
                'sensing_accuracy': '98.0%',
                'reliability': '99.99%',
                'slices_active': slices_active,
                'edges_online': edges_online,
                'alerts_count': 0,
                'active_agvs': agv_tasks_pending,
                'bandwidth_usage_mbps': 250,
                'network_load_pct': 35,
                'pending_tasks': agv_tasks_pending,
                'completed_tasks': 0,
            }

        return {
            "network": {
                "air_peak_rate": metric_data.get('air_peak_rate', '10.0 Gbps'),
                "uplink_peak_rate": metric_data.get('uplink_peak_rate', '1.0 Gbps'),
                "urllc_latency": metric_data.get('urllc_latency', '1.0 ms'),
                "v2x_latency": metric_data.get('v2x_latency', '5.0 ms'),
                "sla_compliance": metric_data.get('sla_compliance', '99.9%'),
                "sensing_accuracy": metric_data.get('sensing_accuracy', '98.0%'),
                "reliability": metric_data.get('reliability', '99.99%')
            },
            "slices": {"total": NetworkSlice.query.count(), "active": slices_active},
            "edge_nodes": {"total": EdgeNode.query.count(), "online": edges_online},
            "alerts": metric_data.get('alerts_count', 0),
            "warehouse": {
                "active_agvs": metric_data.get('active_agvs', 0),
                "bandwidth_usage_mbps": metric_data.get('bandwidth_usage_mbps', 0),
                "network_load_pct": metric_data.get('network_load_pct', 0),
                "pending_tasks": metric_data.get('pending_tasks', 0),
                "completed_tasks": metric_data.get('completed_tasks', 0),
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_network_status(self):
        slices = NetworkSlice.query.filter_by(status='active').all()
        edges = EdgeNode.query.filter_by(status='online').all()
        # 从真实切片数据计算网络状态
        avg_latency = sum(s.latency for s in slices) / len(slices) if slices else 2.0
        avg_bandwidth = sum(s.bandwidth for s in slices) / len(slices) if slices else 300
        avg_sla = sum(s.sla_compliance for s in slices) / len(slices) if slices else 99.9

        # 从网络负载事件获取最新丢包率
        pkt_loss = 0.01
        try:
            from models.db_models import NetworkLoadEvent
            last_event = NetworkLoadEvent.query.order_by(NetworkLoadEvent.triggered_at.desc()).first()
            if last_event and last_event.packet_loss_rate:
                pkt_loss = last_event.packet_loss_rate
        except Exception:
            pass

        return {
            "network_nodes": len(edges),
            "online_nodes": len(edges),
            "active_slices": len(slices),
            "packet_loss_rate": round(pkt_loss, 4),
            "average_latency": round(avg_latency, 1),
            "bandwidth_utilization": round(min(95, avg_bandwidth / 10), 1),
            "sla_compliance": round(avg_sla, 2)
        }


network_service = NetworkService()