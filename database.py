# ============================================
# 数据库扩展模块
# 管理SQLAlchemy实例和数据库连接
# ============================================

import os
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# 全局SQLAlchemy实例
db = SQLAlchemy()


def get_database_uri():
    """获取数据库连接URI"""
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = os.getenv('DB_PORT', '3306')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'root')
    db_name = os.getenv('DB_NAME', '5g_a_industry')
    # 支持MySQL 8.0的caching_sha2_password认证
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"


def get_engine():
    """获取SQLAlchemy引擎"""
    return create_engine(
        get_database_uri(),
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False
    )


def init_database(app):
    """
    初始化数据库：创建数据库（如果不存在）和所有表
    注意：db.init_app(app) 已在 app.py 创建时调用，此处不再重复
    
    Args:
        app: Flask应用实例
    """
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = os.getenv('DB_PORT', '3306')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'root')
    db_name = os.getenv('DB_NAME', '5g_a_industry')

    # 先连接到MySQL服务器（不指定数据库），创建数据库
    try:
        engine_no_db = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/?charset=utf8mb4"
        )
        with engine_no_db.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        engine_no_db.dispose()
        logger.info(f"数据库 '{db_name}' 已就绪")
    except Exception as e:
        logger.error(f"无法连接到MySQL服务器: {e}")
        logger.error("请确保MySQL服务已启动，且用户名/密码正确")
        raise

    # 在应用上下文中创建所有表（db.init_app已在app.py中调用）
    with app.app_context():
        db.create_all()
        logger.info("所有数据库表已创建/验证完成")


def drop_all_tables(app):
    """删除所有表（仅用于开发环境重置）"""
    with app.app_context():
        db.drop_all()
        logger.warning("所有数据库表已删除")


def check_db_connection():
    """检查数据库连接状态"""
    try:
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        return True, "数据库连接正常"
    except Exception as e:
        return False, str(e)