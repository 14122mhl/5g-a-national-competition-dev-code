# ============================================
# 配置管理模块
# 支持多环境配置和数据库连接
# ============================================

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置类"""
    APP_NAME = "5G-A确定性网络智能调度平台"
    APP_VERSION = "3.0.0"
    DEBUG = False
    TESTING = False

    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', '5g_a_industry')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')

    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_ENDPOINT = os.getenv('DEEPSEEK_API_ENDPOINT', 'https://api.deepseek.com/v1/chat/completions')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

    # 5G-A网络配置
    NETWORK_TIMEOUT = 30
    NETWORK_RETRY_COUNT = 3


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DB_NAME = os.getenv('TEST_DB_NAME', '5g_a_industry_test')


class ProductionConfig(Config):
    """生产环境配置"""
    pass


config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

current_config = config_map.get(os.getenv('FLASK_ENV', 'development'), DevelopmentConfig)()