# 网络模拟工具
# 模拟5G-A网络的响应

import random
import time
from config import current_config

def simulate_network_response(data=None, success_rate=0.95, delay_range=(0.1, 0.5)):
    """
    模拟网络响应
    :param data: 响应数据
    :param success_rate: 成功概率
    :param delay_range: 延迟范围（秒）
    :return: 模拟的网络响应
    """
    # 模拟网络延迟
    delay = random.uniform(*delay_range)
    time.sleep(delay)
    
    # 模拟网络错误
    if random.random() > success_rate:
        raise Exception(f"网络错误: 模拟5G-A网络响应失败")
    
    # 模拟网络抖动
    if random.random() > 0.7:
        jitter = random.uniform(0.05, 0.1)
        time.sleep(jitter)
    
    return data

def simulate_5g_a_network_latency():
    """
    模拟5G-A网络时延
    :return: 时延值（毫秒）
    """
    # 5G-A网络时延范围：1-10毫秒
    return round(random.uniform(1, 10), 2)

def simulate_5g_a_network_reliability():
    """
    模拟5G-A网络可靠性
    :return: 可靠性值（百分比）
    """
    # 5G-A网络可靠性：99.99% - 99.999%
    return round(random.uniform(99.99, 99.999), 4)
