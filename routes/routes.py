from flask import Flask
from controllers.user_controller import user_bp
from controllers.product_controller import product_bp
from controllers.order_controller import order_bp
from controllers.production_controller import production_bp
from controllers.device_controller import device_bp
from controllers.ai_controller import ai_bp
from controllers.network_controller import network_bp

def register_routes(app: Flask):
    """注册所有路由"""
    # 注册用户相关路由
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # 注册产品相关路由
    app.register_blueprint(product_bp, url_prefix='/api/products')
    
    # 注册订单相关路由
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    
    # 注册生产线相关路由
    app.register_blueprint(production_bp, url_prefix='/api')
    
    # 注册设备相关路由
    app.register_blueprint(device_bp, url_prefix='/api')
    
    # 注册AI相关路由
    app.register_blueprint(ai_bp, url_prefix='/api')
    
    # 注册网络相关路由
    app.register_blueprint(network_bp, url_prefix='/api')