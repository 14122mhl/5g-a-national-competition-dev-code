# ============================================
# 设备服务 - 数据库版本
# ============================================

import logging
from database import db
from models.db_models import Device, ProductionLine

logger = logging.getLogger(__name__)


class DeviceService:

    def get_all_devices(self, device_type=None, status=None, line_id=None):
        query = Device.query
        if device_type:
            query = query.filter_by(type=device_type)
        if status:
            query = query.filter_by(status=status)
        if line_id:
            query = query.filter_by(line_id=line_id)
        devices = query.all()
        return [d.to_dict() for d in devices]

    def get_device_by_id(self, device_id):
        device = Device.query.get(device_id)
        return device.to_dict() if device else None

    def create_device(self, data):
        device = Device(
            name=data['name'],
            code=data['code'],
            type=data.get('type', 'sensor'),
            line_id=data.get('line_id'),
            status=data.get('status', 'online'),
            ip_address=data.get('ip_address'),
            firmware_version=data.get('firmware_version')
        )
        db.session.add(device)
        db.session.commit()
        logger.info(f"创建设备: {device.name} (ID:{device.id})")
        return device.to_dict()

    def update_device(self, device_id, data):
        device = Device.query.get(device_id)
        if not device:
            return None

        for field in ['name', 'code', 'type', 'status', 'ip_address', 'firmware_version']:
            if field in data:
                setattr(device, field, data[field])
        if 'line_id' in data:
            device.line_id = data['line_id']
        if 'metrics_json' in data:
            import json
            device.metrics_json = json.dumps(data['metrics_json'], ensure_ascii=False)

        db.session.commit()
        logger.info(f"更新设备: {device.name} (ID:{device_id})")
        return device.to_dict()

    def delete_device(self, device_id):
        device = Device.query.get(device_id)
        if not device:
            return False
        db.session.delete(device)
        db.session.commit()
        logger.info(f"删除设备: {device.name} (ID:{device_id})")
        return True

    def get_device_stats(self):
        devices = Device.query.all()
        total = len(devices)
        online = sum(1 for d in devices if d.status == 'online')
        offline = sum(1 for d in devices if d.status == 'offline')
        maintenance = sum(1 for d in devices if d.status == 'maintenance')

        return {
            'total': total,
            'online': online,
            'offline': offline,
            'maintenance': maintenance,
            'online_rate': round(online / max(total, 1) * 100, 1)
        }


device_service = DeviceService()