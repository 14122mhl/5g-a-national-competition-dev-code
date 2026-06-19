# ============================================
# 订单服务 - 数据库版本
# ============================================

import uuid
import logging
from database import db
from models.db_models import Order, OrderItem, Product
from services.product_service import product_service

logger = logging.getLogger(__name__)


class OrderService:

    def get_all_orders(self, status=None):
        query = Order.query
        if status:
            query = query.filter_by(status=status)
        orders = query.order_by(Order.created_at.desc()).all()
        return [o.to_dict() for o in orders]

    def get_order_by_id(self, order_id):
        order = Order.query.get(order_id)
        return order.to_dict() if order else None

    def get_order_by_number(self, order_number):
        order = Order.query.filter_by(order_number=order_number).first()
        return order.to_dict() if order else None

    def create_order(self, user_id, items):
        total_amount = 0
        order_items = []

        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                raise Exception(f"产品不存在: {item['product_id']}")
            if product.quantity < item['quantity']:
                raise Exception(f"库存不足: {product.name}")

            subtotal = product.price * item['quantity']
            total_amount += subtotal

            order_item = OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=product.price,
                subtotal=subtotal
            )
            order_items.append(order_item)

        order = Order(
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            total_amount=total_amount,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # 获取order.id

        for oi in order_items:
            oi.order_id = order.id
            db.session.add(oi)
            product_service.update_stock(oi.product_id, -oi.quantity)

        db.session.commit()
        logger.info(f"创建订单: {order.order_number} (ID:{order.id})")
        return order.to_dict()

    def update_order_status(self, order_id, status):
        order = Order.query.get(order_id)
        if not order:
            return None
        order.status = status
        db.session.commit()
        logger.info(f"更新订单状态: {order.order_number} -> {status}")
        return order.to_dict()

    def cancel_order(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            return False
        if order.status == 'completed':
            raise Exception("已完成的订单不能取消")

        for item in order.items:
            product_service.update_stock(item.product_id, item.quantity)

        order.status = 'cancelled'
        db.session.commit()
        logger.info(f"取消订单: {order.order_number}")
        return True


order_service = OrderService()