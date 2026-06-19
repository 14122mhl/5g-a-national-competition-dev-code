# ============================================
# 数据库种子数据脚本
# 仓库模式：使用 data_generator 生成真实业务数据
# ============================================

import logging

logger = logging.getLogger(__name__)


def seed_all():
    """执行所有种子数据插入（仓库模式 - 约5500条数据）"""
    from data_generator import generate_all
    generate_all()


if __name__ == '__main__':
    from app import app
    with app.app_context():
        seed_all()