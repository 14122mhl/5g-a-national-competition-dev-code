# ============================================
# 产品服务 - 数据库版本
# ============================================

import logging
from database import db
from models.db_models import Product

logger = logging.getLogger(__name__)


class ProductService:

    def get_all_products(self, category=None, status=None):
        query = Product.query
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)
        products = query.all()
        return [p.to_dict() for p in products]

    def get_product_by_id(self, product_id):
        product = Product.query.get(product_id)
        return product.to_dict() if product else None

    def get_product_by_sku(self, sku):
        product = Product.query.filter_by(sku=sku).first()
        return product.to_dict() if product else None

    def create_product(self, data):
        if Product.query.filter_by(sku=data['sku']).first():
            raise Exception("产品SKU已存在")

        product = Product(
            name=data['name'],
            sku=data['sku'],
            category=data.get('category', '未分类'),
            price=float(data.get('price', 0)),
            quantity=int(data.get('quantity', 0)),
            unit=data.get('unit', '台'),
            description=data.get('description', ''),
            min_stock=int(data.get('min_stock', 10)),
            max_stock=int(data.get('max_stock', 500))
        )
        db.session.add(product)
        db.session.commit()
        logger.info(f"创建产品: {product.name} (ID:{product.id})")
        return product.to_dict()

    def update_product(self, product_id, data):
        product = Product.query.get(product_id)
        if not product:
            return None

        for field in ['name', 'sku', 'category', 'description', 'unit', 'status']:
            if field in data:
                setattr(product, field, data[field])
        if 'price' in data:
            product.price = float(data['price'])
        if 'quantity' in data:
            product.quantity = int(data['quantity'])
        if 'min_stock' in data:
            product.min_stock = int(data['min_stock'])
        if 'max_stock' in data:
            product.max_stock = int(data['max_stock'])

        db.session.commit()
        logger.info(f"更新产品: {product.name} (ID:{product_id})")
        return product.to_dict()

    def delete_product(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            return False
        db.session.delete(product)
        db.session.commit()
        logger.info(f"删除产品: {product.name} (ID:{product_id})")
        return True

    def update_stock(self, product_id, delta):
        """更新库存(delta可为负数)"""
        product = Product.query.get(product_id)
        if not product:
            raise Exception(f"产品不存在: {product_id}")
        new_quantity = product.quantity + delta
        if new_quantity < 0:
            raise Exception(f"库存不足: {product.name}")
        product.quantity = new_quantity
        db.session.commit()
        return product.to_dict()


product_service = ProductService()