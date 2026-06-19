# 日志工具
# 配置和使用日志系统

import logging
import os
from datetime import datetime
from config import current_config

# 创建日志目录
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 创建日志文件名
log_file = os.path.join(log_dir, f"{current_config.LOG_FILE.split('.')[0]}_{datetime.now().strftime('%Y%m%d')}.{current_config.LOG_FILE.split('.')[1]}")

# 配置日志
logging.basicConfig(
    level=getattr(logging, current_config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# 创建logger实例
logger = logging.getLogger('5G-A-Industry')

# 测试日志
logger.info("日志系统初始化完成")
logger.debug(f"当前配置: {current_config.__class__.__name__}")
