# 设备服务
# 处理设备相关的业务逻辑

from backend.models.device import Device, DeviceType, DeviceStatus
from backend.utils.logger import logger

class DeviceService:
    """设备服务类"""
    
    def __init__(self):
        """初始化设备服务"""
        self.devices = []  # 内存缓存，实际生产环境使用PostgreSQL数据库
        # 添加默认设备
        self._add_default_devices()
    
    def _add_default_devices(self):
        """添加默认设备"""
        default_devices = [
            {
                "id": 1,
                "name": "机械臂机器人",
                "description": "用于装配的机械臂机器人",
                "device_id": "DEV-001",
                "type": DeviceType.ROBOT,
                "status": DeviceStatus.ONLINE,
                "production_line_id": 1,
                "ip_address": "192.168.1.101",
                "firmware_version": "v1.0.0",
                "is_active": True
            },
            {
                "id": 2,
                "name": "温度传感器",
                "description": "用于监测温度的传感器",
                "device_id": "DEV-002",
                "type": DeviceType.SENSOR,
                "status": DeviceStatus.ONLINE,
                "production_line_id": 1,
                "ip_address": "192.168.1.102",
                "firmware_version": "v1.1.0",
                "is_active": True
            },
            {
                "id": 3,
                "name": "生产线控制器",
                "description": "控制生产线的控制器",
                "device_id": "DEV-003",
                "type": DeviceType.CONTROLLER,
                "status": DeviceStatus.ONLINE,
                "production_line_id": 1,
                "ip_address": "192.168.1.103",
                "firmware_version": "v2.0.0",
                "is_active": True
            },
            {
                "id": 4,
                "name": "传送带",
                "description": "用于运输物料的传送带",
                "device_id": "DEV-004",
                "type": DeviceType.CONVEYOR,
                "status": DeviceStatus.OFFLINE,
                "production_line_id": 2,
                "ip_address": "192.168.1.104",
                "firmware_version": "v1.0.0",
                "is_active": True
            }
        ]
        
        for device_data in default_devices:
            device = Device(**device_data)
            self.devices.append(device)
    
    def get_all_devices(self, type=None, status=None, production_line_id=None):
        """
        获取所有设备
        :param type: 设备类型过滤
        :param status: 设备状态过滤
        :param production_line_id: 生产线ID过滤
        :return: 设备列表
        """
        logger.info(f"获取所有设备，类型: {type}, 状态: {status}, 生产线ID: {production_line_id}")
        
        filtered_devices = self.devices
        
        if type:
            filtered_devices = [device for device in filtered_devices if device.type.value == type]
        if status:
            filtered_devices = [device for device in filtered_devices if device.status.value == status]
        if production_line_id:
            filtered_devices = [device for device in filtered_devices if device.production_line_id == production_line_id]
        
        return [device.to_dict() for device in filtered_devices]
    
    def get_device_by_id(self, device_id):
        """
        根据ID获取设备
        :param device_id: 设备ID
        :return: 设备对象
        """
        logger.info(f"根据ID获取设备: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                return device.to_dict()
        return None
    
    def get_device_by_device_id(self, device_id):
        """
        根据设备ID获取设备
        :param device_id: 设备ID
        :return: 设备对象
        """
        logger.info(f"根据设备ID获取设备: {device_id}")
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None
    
    def create_device(self, data):
        """
        创建设备
        :param data: 设备数据
        :return: 创建的设备对象
        """
        logger.info(f"创建设备: {data['name']}")
        # 检查设备ID是否已存在
        if self.get_device_by_device_id(data['device_id']):
            raise Exception("设备ID已存在")
        
        # 创建设备
        new_device = Device(
            id=len(self.devices) + 1,
            name=data['name'],
            description=data.get('description', ''),
            device_id=data['device_id'],
            type=DeviceType(data['type']),
            status=DeviceStatus(data.get('status', 'offline')),
            production_line_id=data.get('production_line_id'),
            ip_address=data.get('ip_address'),
            firmware_version=data.get('firmware_version'),
            is_active=data.get('is_active', True)
        )
        
        self.devices.append(new_device)
        return new_device.to_dict()
    
    def update_device(self, device_id, data):
        """
        更新设备
        :param device_id: 设备ID
        :param data: 更新数据
        :return: 更新后的设备对象
        """
        logger.info(f"更新设备: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                # 更新设备信息
                if 'name' in data:
                    device.name = data['name']
                if 'description' in data:
                    device.description = data['description']
                if 'device_id' in data:
                    # 检查新设备ID是否已存在
                    existing_device = self.get_device_by_device_id(data['device_id'])
                    if existing_device and existing_device.id != device_id:
                        raise Exception("设备ID已存在")
                    device.device_id = data['device_id']
                if 'type' in data:
                    device.type = DeviceType(data['type'])
                if 'status' in data:
                    device.status = DeviceStatus(data['status'])
                if 'production_line_id' in data:
                    device.production_line_id = data['production_line_id']
                if 'ip_address' in data:
                    device.ip_address = data['ip_address']
                if 'firmware_version' in data:
                    device.firmware_version = data['firmware_version']
                if 'is_active' in data:
                    device.is_active = data['is_active']
                
                return device.to_dict()
        return None
    
    def delete_device(self, device_id):
        """
        删除设备
        :param device_id: 设备ID
        :return: 是否删除成功
        """
        logger.info(f"删除设备: {device_id}")
        for i, device in enumerate(self.devices):
            if device.id == device_id:
                self.devices.pop(i)
                return True
        return False
    
    def activate_device(self, device_id):
        """
        激活设备
        :param device_id: 设备ID
        :return: 激活后的设备对象
        """
        logger.info(f"激活设备: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                device.is_active = True
                return device.to_dict()
        return None
    
    def deactivate_device(self, device_id):
        """
        停用设备
        :param device_id: 设备ID
        :return: 停用后的设备对象
        """
        logger.info(f"停用设备: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                device.is_active = False
                device.status = DeviceStatus.OFFLINE
                return device.to_dict()
        return None
    
    def set_device_online(self, device_id):
        """
        设置设备在线
        :param device_id: 设备ID
        :return: 在线状态的设备对象
        """
        logger.info(f"设置设备在线: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                if not device.is_active:
                    raise Exception("设备已停用")
                device.status = DeviceStatus.ONLINE
                return device.to_dict()
        return None
    
    def set_device_offline(self, device_id):
        """
        设置设备离线
        :param device_id: 设备ID
        :return: 离线状态的设备对象
        """
        logger.info(f"设置设备离线: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                device.status = DeviceStatus.OFFLINE
                return device.to_dict()
        return None
    
    def set_device_error(self, device_id):
        """
        设置设备错误
        :param device_id: 设备ID
        :return: 错误状态的设备对象
        """
        logger.info(f"设置设备错误: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                device.status = DeviceStatus.ERROR
                return device.to_dict()
        return None
    
    def set_device_maintenance(self, device_id):
        """
        设置设备维护
        :param device_id: 设备ID
        :return: 维护状态的设备对象
        """
        logger.info(f"设置设备维护: {device_id}")
        for device in self.devices:
            if device.id == device_id:
                device.status = DeviceStatus.MAINTENANCE
                return device.to_dict()
        return None
