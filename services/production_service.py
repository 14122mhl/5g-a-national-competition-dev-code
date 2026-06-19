# ============================================
# 生产服务 - 数据库版本
# ============================================

import logging
from database import db
from models.db_models import ProductionLine, Device

logger = logging.getLogger(__name__)


class ProductionService:

    def get_all_lines(self, status=None, category=None):
        query = ProductionLine.query
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        lines = query.all()
        return [l.to_dict() for l in lines]

    def get_line_by_id(self, line_id):
        line = ProductionLine.query.get(line_id)
        return line.to_dict() if line else None

    def create_line(self, data):
        line = ProductionLine(
            name=data['name'],
            code=data['code'],
            category=data.get('category', 'assembly'),
            status=data.get('status', 'idle'),
            capacity=int(data.get('capacity', 100)),
            efficiency=float(data.get('efficiency', 100)),
            current_task=data.get('current_task'),
            location=data.get('location'),
            oee=float(data.get('oee', 85))
        )
        db.session.add(line)
        db.session.commit()
        logger.info(f"创建生产线: {line.name} (ID:{line.id})")
        return line.to_dict()

    def update_line(self, line_id, data):
        line = ProductionLine.query.get(line_id)
        if not line:
            return None

        for field in ['name', 'code', 'category', 'status', 'current_task', 'location']:
            if field in data:
                setattr(line, field, data[field])
        if 'capacity' in data:
            line.capacity = int(data['capacity'])
        if 'efficiency' in data:
            line.efficiency = float(data['efficiency'])
        if 'oee' in data:
            line.oee = float(data['oee'])

        db.session.commit()
        logger.info(f"更新生产线: {line.name} (ID:{line_id})")
        return line.to_dict()

    def delete_line(self, line_id):
        line = ProductionLine.query.get(line_id)
        if not line:
            return False
        db.session.delete(line)
        db.session.commit()
        logger.info(f"删除生产线: {line.name} (ID:{line_id})")
        return True

    def get_line_devices(self, line_id):
        line = ProductionLine.query.get(line_id)
        if not line:
            return None
        devices = Device.query.filter_by(line_id=line_id).all()
        return {
            'line': line.to_dict(),
            'devices': [d.to_dict() for d in devices]
        }

    def get_production_stats(self):
        lines = ProductionLine.query.all()
        total = len(lines)
        running = sum(1 for l in lines if l.status == 'running')
        idle = sum(1 for l in lines if l.status == 'idle')
        maintenance = sum(1 for l in lines if l.status == 'maintenance')
        avg_oee = sum(l.oee for l in lines if l.oee) / max(total, 1)

        return {
            'total_lines': total,
            'running': running,
            'idle': idle,
            'maintenance': maintenance,
            'avg_oee': round(avg_oee, 1),
            'utilization_rate': round(running / max(total, 1) * 100, 1)
        }


production_service = ProductionService()