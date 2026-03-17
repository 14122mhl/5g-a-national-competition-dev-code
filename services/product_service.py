# 产品服务
# 处理产品相关的业务逻辑

from models.product import Product, ProductStatus
from utils.logger import logger

class ProductService:
    """产品服务类"""
    
    def __init__(self):
        """初始化产品服务"""
        self.products = []  # 内存缓存，实际生产环境使用PostgreSQL数据库
        # 添加默认产品
        self._add_default_products()
    
    def _add_default_products(self):
        """添加默认产品"""
        default_products = [
            {
                "id": 1,
                "name": "智能传感器",
                "description": "5G-A网络兼容的智能传感器",
                "sku": "SENSOR-001",
                "price": 199.99,
                "cost": 120.00,
                "quantity": 100,
                "status": ProductStatus.ACTIVE
            },
            {
                "id": 2,
                "name": "工业机器人",
                "description": "柔性生产用工业机器人",
                "sku": "ROBOT-001",
                "price": 9999.99,
                "cost": 6000.00,
                "quantity": 10,
                "status": ProductStatus.ACTIVE
            },
            {
                "id": 3,
                "name": "控制器",
                "description": "工业控制系统",
                "sku": "CONTROLLER-001",
                "price": 1499.99,
                "cost": 800.00,
                "quantity": 50,
                "status": ProductStatus.ACTIVE
            }
        ]
        
        for product_data in default_products:
            product = Product(**product_data)
            self.products.append(product)
    
    def get_all_products(self, status=None):
        """
        获取所有产品
        :param status: 产品状态过滤
        :return: 产品列表
        """
        logger.info(f"获取所有产品，状态: {status}")
        if status:
            return [product.to_dict() for product in self.products if product.status.value == status]
        return [product.to_dict() for product in self.products]
    
    def get_product_by_id(self, product_id):
        """
        根据ID获取产品
        :param product_id: 产品ID
        :return: 产品对象
        """
        logger.info(f"根据ID获取产品: {product_id}")
        for product in self.products:
            if product.id == product_id:
                return product.to_dict()
        return None
    
    def get_product_by_sku(self, sku):
        """
        根据SKU获取产品
        :param sku: 产品SKU
        :return: 产品对象
        """
        logger.info(f"根据SKU获取产品: {sku}")
        for product in self.products:
            if product.sku == sku:
                return product
        return None
    
    def create_product(self, data):
        """
        创建产品
        :param data: 产品数据
        :return: 创建的产品对象
        """
        logger.info(f"创建产品: {data['name']}")
        # 检查SKU是否已存在
        if self.get_product_by_sku(data['sku']):
            raise Exception("SKU已存在")
        
        # 创建新产品
        new_product = Product(
            id=len(self.products) + 1,
            name=data['name'],
            description=data.get('description', ''),
            sku=data['sku'],
            price=data['price'],
            cost=data['cost'],
            quantity=data.get('quantity', 0),
            status=ProductStatus(data.get('status', 'active'))
        )
        
        self.products.append(new_product)
        return new_product.to_dict()
    
    def update_product(self, product_id, data):
        """
        更新产品
        :param product_id: 产品ID
        :param data: 更新数据
        :return: 更新后的产品对象
        """
        logger.info(f"更新产品: {product_id}")
        for product in self.products:
            if product.id == product_id:
                # 更新产品信息
                if 'name' in data:
                    product.name = data['name']
                if 'description' in data:
                    product.description = data['description']
                if 'sku' in data:
                    # 检查新SKU是否已存在
                    existing_product = self.get_product_by_sku(data['sku'])
                    if existing_product and existing_product.id != product_id:
                        raise Exception("SKU已存在")
                    product.sku = data['sku']
                if 'price' in data:
                    product.price = data['price']
                if 'cost' in data:
                    product.cost = data['cost']
                if 'quantity' in data:
                    product.quantity = data['quantity']
                if 'status' in data:
                    product.status = ProductStatus(data['status'])
                
                return product.to_dict()
        return None
    
    def delete_product(self, product_id):
        """
        删除产品
        :param product_id: 产品ID
        :return: 是否删除成功
        """
        logger.info(f"删除产品: {product_id}")
        for i, product in enumerate(self.products):
            if product.id == product_id:
                self.products.pop(i)
                return True
        return False
    
    def update_stock(self, product_id, quantity_change):
        """
        更新库存
        :param product_id: 产品ID
        :param quantity_change: 库存变化量
        :return: 更新后的库存
        """
        logger.info(f"更新产品库存: {product_id}, 变化量: {quantity_change}")
        for product in self.products:
            if product.id == product_id:
                new_quantity = product.quantity + quantity_change
                if new_quantity < 0:
                    raise Exception("库存不足")
                product.quantity = new_quantity
                return product.quantity
        return None
