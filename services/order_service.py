# 订单服务
# 处理订单相关的业务逻辑

from backend.models.order import Order, OrderStatus
from backend.models.order_item import OrderItem
from backend.services.product_service import ProductService
from backend.utils.logger import logger
import uuid

class OrderService:
    """订单服务类"""
    
    def __init__(self):
        """初始化订单服务"""
        self.orders = []  # 内存缓存，实际生产环境使用PostgreSQL数据库
        self.order_items = []  # 内存缓存，实际生产环境使用PostgreSQL数据库
        self.product_service = ProductService()
        # 添加默认订单
        self._add_default_orders()
    
    def _add_default_orders(self):
        """添加默认订单"""
        # 创建默认订单1
        order1 = Order(
            id=1,
            order_number=f"ORD-{uuid.uuid4()}",
            user_id=1,
            total_amount=2199.98,
            status=OrderStatus.COMPLETED
        )
        self.orders.append(order1)
        
        # 添加订单项
        order_item1 = OrderItem(
            id=1,
            order_id=1,
            product_id=1,
            quantity=2,
            unit_price=199.99,
            subtotal=399.98
        )
        order_item2 = OrderItem(
            id=2,
            order_id=1,
            product_id=2,
            quantity=1,
            unit_price=9999.99,
            subtotal=9999.99
        )
        self.order_items.extend([order_item1, order_item2])
        
        # 创建默认订单2
        order2 = Order(
            id=2,
            order_number=f"ORD-{uuid.uuid4()}",
            user_id=1,
            total_amount=1499.99,
            status=OrderStatus.PROCESSING
        )
        self.orders.append(order2)
        
        # 添加订单项
        order_item3 = OrderItem(
            id=3,
            order_id=2,
            product_id=3,
            quantity=1,
            unit_price=1499.99,
            subtotal=1499.99
        )
        self.order_items.append(order_item3)
    
    def get_all_orders(self, status=None):
        """
        获取所有订单
        :param status: 订单状态过滤
        :return: 订单列表
        """
        logger.info(f"获取所有订单，状态: {status}")
        if status:
            return [self._get_order_with_items(order) for order in self.orders if order.status.value == status]
        return [self._get_order_with_items(order) for order in self.orders]
    
    def get_order_by_id(self, order_id):
        """
        根据ID获取订单
        :param order_id: 订单ID
        :return: 订单对象
        """
        logger.info(f"根据ID获取订单: {order_id}")
        for order in self.orders:
            if order.id == order_id:
                return self._get_order_with_items(order)
        return None
    
    def get_order_by_number(self, order_number):
        """
        根据订单号获取订单
        :param order_number: 订单号
        :return: 订单对象
        """
        logger.info(f"根据订单号获取订单: {order_number}")
        for order in self.orders:
            if order.order_number == order_number:
                return self._get_order_with_items(order)
        return None
    
    def _get_order_with_items(self, order):
        """
        获取订单及其订单项
        :param order: 订单对象
        :return: 包含订单项的订单字典
        """
        order_dict = order.to_dict()
        order_dict['items'] = [item.to_dict() for item in self.order_items if item.order_id == order.id]
        return order_dict
    
    def create_order(self, user_id, items):
        """
        创建订单
        :param user_id: 用户ID
        :param items: 订单项列表
        :return: 创建的订单对象
        """
        logger.info(f"创建订单，用户ID: {user_id}")
        
        # 计算总金额
        total_amount = 0
        order_items = []
        
        for item in items:
            product = self.product_service.get_product_by_id(item['product_id'])
            if not product:
                raise Exception(f"产品不存在: {item['product_id']}")
            
            # 检查库存
            if product['quantity'] < item['quantity']:
                raise Exception(f"库存不足: {product['name']}")
            
            # 计算小计
            subtotal = product['price'] * item['quantity']
            total_amount += subtotal
            
            # 创建订单项
            order_item = OrderItem(
                id=len(self.order_items) + 1,
                order_id=len(self.orders) + 1,  # 临时ID，稍后更新
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=product['price'],
                subtotal=subtotal
            )
            order_items.append(order_item)
            
            # 更新库存
            self.product_service.update_stock(item['product_id'], -item['quantity'])
        
        # 创建订单
        new_order = Order(
            id=len(self.orders) + 1,
            order_number=f"ORD-{uuid.uuid4()}",
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        
        self.orders.append(new_order)
        
        # 更新订单项的订单ID
        for item in order_items:
            item.order_id = new_order.id
            self.order_items.append(item)
        
        return self._get_order_with_items(new_order)
    
    def update_order_status(self, order_id, status):
        """
        更新订单状态
        :param order_id: 订单ID
        :param status: 新状态
        :return: 更新后的订单对象
        """
        logger.info(f"更新订单状态: {order_id}, 新状态: {status}")
        for order in self.orders:
            if order.id == order_id:
                order.status = OrderStatus(status)
                return self._get_order_with_items(order)
        return None
    
    def cancel_order(self, order_id):
        """
        取消订单
        :param order_id: 订单ID
        :return: 是否取消成功
        """
        logger.info(f"取消订单: {order_id}")
        for order in self.orders:
            if order.id == order_id:
                if order.status == OrderStatus.COMPLETED:
                    raise Exception("已完成的订单不能取消")
                
                # 恢复库存
                order_items = [item for item in self.order_items if item.order_id == order_id]
                for item in order_items:
                    self.product_service.update_stock(item.product_id, item.quantity)
                
                # 更新订单状态
                order.status = OrderStatus.CANCELLED
                return True
        return False
