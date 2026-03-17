# 配置管理模块
# 模拟企业级应用的配置系统

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # 应用配置
    APP_NAME = "工业大模型柔性生产智能调度系统"
    APP_VERSION = "1.0.0"
    DEBUG = False
    TESTING = False
    
    # 数据库配置 (模拟)
    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://admin:password@localhost:5432/5g_a_industry')
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
    
    # API配置
    API_PREFIX = '/api/v1'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # 5G-A网络配置
    NETWORK_TIMEOUT = 30  # 网络超时时间（秒）
    NETWORK_RETRY_COUNT = 3  # 网络重试次数
    
    # 工业大模型配置
    MODEL_ENDPOINT = os.getenv('MODEL_ENDPOINT', 'http://localhost:8000/model')
    MODEL_TIMEOUT = 60  # 模型调用超时时间（秒）


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'postgresql://admin:password@localhost:5432/5g_a_industry_test')


class ProductionConfig(Config):
    """生产环境配置"""
    pass


# 根据环境变量选择配置
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# 获取当前环境配置
current_config = config_map.get(os.getenv('FLASK_ENV', 'development'))
