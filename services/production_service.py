# 生产服务
# 处理生产线相关的业务逻辑

from backend.models.production_line import ProductionLine, ProductionLineStatus
from backend.utils.logger import logger

class ProductionService:
    """生产服务类"""
    
    def __init__(self):
        """初始化生产服务"""
        self.production_lines = []  # 内存缓存，实际生产环境使用PostgreSQL数据库
        # 添加默认生产线
        self._add_default_production_lines()
    
    def _add_default_production_lines(self):
        """添加默认生产线"""
        default_lines = [
            {
                "id": 1,
                "name": "智能传感器生产线",
                "description": "生产智能传感器的生产线",
                "code": "LINE-001",
                "status": ProductionLineStatus.RUNNING,
                "is_active": True
            },
            {
                "id": 2,
                "name": "工业机器人生产线",
                "description": "生产工业机器人的生产线",
                "code": "LINE-002",
                "status": ProductionLineStatus.STOPPED,
                "is_active": True
            },
            {
                "id": 3,
                "name": "控制器生产线",
                "description": "生产控制器的生产线",
                "code": "LINE-003",
                "status": ProductionLineStatus.RUNNING,
                "is_active": True
            }
        ]
        
        for line_data in default_lines:
            line = ProductionLine(**line_data)
            self.production_lines.append(line)
    
    def get_all_production_lines(self, status=None):
        """
        获取所有生产线
        :param status: 生产线状态过滤
        :return: 生产线列表
        """
        logger.info(f"获取所有生产线，状态: {status}")
        if status:
            return [line.to_dict() for line in self.production_lines if line.status.value == status]
        return [line.to_dict() for line in self.production_lines]
    
    def get_production_line_by_id(self, line_id):
        """
        根据ID获取生产线
        :param line_id: 生产线ID
        :return: 生产线对象
        """
        logger.info(f"根据ID获取生产线: {line_id}")
        for line in self.production_lines:
            if line.id == line_id:
                return line.to_dict()
        return None
    
    def get_production_line_by_code(self, code):
        """
        根据代码获取生产线
        :param code: 生产线代码
        :return: 生产线对象
        """
        logger.info(f"根据代码获取生产线: {code}")
        for line in self.production_lines:
            if line.code == code:
                return line
        return None
    
    def create_production_line(self, data):
        """
        创建生产线
        :param data: 生产线数据
        :return: 创建的生产线对象
        """
        logger.info(f"创建生产线: {data['name']}")
        # 检查代码是否已存在
        if self.get_production_line_by_code(data['code']):
            raise Exception("生产线代码已存在")
        
        # 创建新生产线
        new_line = ProductionLine(
            id=len(self.production_lines) + 1,
            name=data['name'],
            description=data.get('description', ''),
            code=data['code'],
            status=ProductionLineStatus(data.get('status', 'stopped')),
            is_active=data.get('is_active', True)
        )
        
        self.production_lines.append(new_line)
        return new_line.to_dict()
    
    def update_production_line(self, line_id, data):
        """
        更新生产线
        :param line_id: 生产线ID
        :param data: 更新数据
        :return: 更新后的生产线对象
        """
        logger.info(f"更新生产线: {line_id}")
        for line in self.production_lines:
            if line.id == line_id:
                # 更新生产线信息
                if 'name' in data:
                    line.name = data['name']
                if 'description' in data:
                    line.description = data['description']
                if 'code' in data:
                    # 检查新代码是否已存在
                    existing_line = self.get_production_line_by_code(data['code'])
                    if existing_line and existing_line.id != line_id:
                        raise Exception("生产线代码已存在")
                    line.code = data['code']
                if 'status' in data:
                    line.status = ProductionLineStatus(data['status'])
                if 'is_active' in data:
                    line.is_active = data['is_active']
                
                return line.to_dict()
        return None
    
    def delete_production_line(self, line_id):
        """
        删除生产线
        :param line_id: 生产线ID
        :return: 是否删除成功
        """
        logger.info(f"删除生产线: {line_id}")
        for i, line in enumerate(self.production_lines):
            if line.id == line_id:
                if line.status == ProductionLineStatus.RUNNING:
                    raise Exception("运行中的生产线不能删除")
                self.production_lines.pop(i)
                return True
        return False
    
    def start_production_line(self, line_id):
        """
        启动生产线
        :param line_id: 生产线ID
        :return: 启动后的生产线对象
        """
        logger.info(f"启动生产线: {line_id}")
        for line in self.production_lines:
            if line.id == line_id:
                if not line.is_active:
                    raise Exception("生产线已禁用")
                line.status = ProductionLineStatus.RUNNING
                return line.to_dict()
        return None
    
    def stop_production_line(self, line_id):
        """
        停止生产线
        :param line_id: 生产线ID
        :return: 停止后的生产线对象
        """
        logger.info(f"停止生产线: {line_id}")
        for line in self.production_lines:
            if line.id == line_id:
                line.status = ProductionLineStatus.STOPPED
                return line.to_dict()
        return None
    
    def put_production_line_in_maintenance(self, line_id):
        """
        将生产线置于维护状态
        :param line_id: 生产线ID
        :return: 维护状态的生产线对象
        """
        logger.info(f"将生产线置于维护状态: {line_id}")
        for line in self.production_lines:
            if line.id == line_id:
                line.status = ProductionLineStatus.MAINTENANCE
                return line.to_dict()
        return None
