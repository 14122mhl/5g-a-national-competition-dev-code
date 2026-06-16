# 5G-A 确定性网络智能调度仿真平台

## 项目概述

5G-A 确定性网络智能调度仿真平台是一个面向工业互联网场景的智能调度系统，通过5G-A通感融合技术、网络切片管理、边缘算力调度和AI智能分析，实现生产网络的确定性保障和智能优化。

## 系统架构

```
5G-A/
├── app.py                     # 主应用入口，Flask Web服务器
├── dev.html                   # 前端单页应用界面
├── config/                    # 配置管理
│   ├── __init__.py
│   └── config.py              # 多环境配置（开发/测试/生产）
├── algorithms/                # 核心算法模块
│   ├── __init__.py
│   ├── scheduler.py           # 生产调度优化算法
│   ├── predictor.py           # 性能预测算法（指数平滑/移动平均）
│   ├── sensing.py             # 通感一体感知数据处理
│   └── optimizer.py           # 网络切片优化算法
├── services/                  # 业务服务层
│   ├── __init__.py
│   └── ai_agent.py            # AI智能分析代理（含DeepSeek API预留接口）
├── middleware/                 # 中间件层
│   ├── __init__.py
│   └── auth.py                # 认证与权限控制
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── logger.py              # 日志系统
│   ├── response.py            # 统一响应格式
│   ├── validator.py           # 请求验证
│   ├── jwt.py                 # JWT令牌管理
│   ├── password.py            # 密码处理
│   └── network.py             # 网络模拟工具
├── models/                    # 数据模型层
├── routes/                    # 路由层
├── controllers/               # 控制器层
├── tests/                     # 测试模块
└── logs/                      # 日志目录
```

## 核心功能

### 1. 核心仪表盘
- 实时监控空口峰值速率、上行峰值速率、URLLC时延、车联网时延
- 展示SLA履约率、通感融合精度、网络可靠性指标
- 系统资源概览（网络切片、边缘节点、告警事件）
- 性能趋势图表（时延/吞吐量实时监控）

### 2. 网络切片管理
- 创建、编辑、删除、批量删除网络切片
- 支持工业控制切片、车联网切片、民生服务切片
- 按类型、状态、关键词搜索和筛选
- 实时展示切片时延、带宽、状态等参数

### 3. 通感一体监控
- 温度、人员、设备、环境、振动五大感知类型
- 实时感知精度、距离、刷新率、覆盖率监控
- 环境监测数据（温度、湿度、气压、振动、噪音、空气质量）
- 目标追踪（人员、车辆、机器人、设备位置与速度）

### 4. 边缘算力监控
- 边缘节点CPU/内存使用率实时监控
- 推理任务查看与管理
- 节点负载均衡态势展示

### 5. 仿真调度
- 多负载场景仿真（低/中/高负载）
- 多切片类型调度（工业/车联网/民生）
- AI优化与传统方案对比（时延、带宽、丢包率、可靠性）
- 生产调度结果展示（任务分配、产线负载、优化指标）
- 仿真历史记录管理

### 6. 性能预测
- 基于指数平滑和移动平均的预测算法
- AI优化预测 vs 传统方式对比
- 支持时延、丢包率、可靠性多指标预测
- 需求预测（历史趋势分析+季节性调整）

### 7. AI智能分析
- 生产调度优化分析（效率、资源、风险、改进）
- 网络风险评估（丢包率、时延、节点异常检测）
- 综合优化报告（时延、吞吐量、节能、成本、质量）
- DeepSeek API集成接口（预留，配置后启用）

## API接口文档

### 基础接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 前端主页面 |
| GET | `/health` | 健康检查 |

### 仪表盘 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/metrics` | 获取仪表盘实时指标 |
| POST | `/api/dashboard/refresh` | 刷新仪表盘数据 |

### 网络切片 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/slices` | 获取切片列表（支持`?type=`、`?status=`、`?search=`筛选） |
| POST | `/api/slices` | 创建切片 |
| PUT | `/api/slices/{id}` | 更新切片 |
| DELETE | `/api/slices/{id}` | 删除切片 |
| POST | `/api/slices/batch-delete` | 批量删除切片 |

### 通感一体 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sensing/data` | 获取通感感知数据 |
| POST | `/api/sensing/filter` | 筛选感知类型 |
| GET | `/api/sensing/tracking` | 获取目标追踪数据 |

### 边缘算力 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/edge/nodes` | 获取边缘节点列表 |
| GET | `/api/edge/nodes/{id}/tasks` | 获取节点推理任务 |

### 仿真调度 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/simulation/run` | 运行仿真调度 |
| GET | `/api/simulation/history` | 获取仿真历史 |
| DELETE | `/api/simulation/history` | 清空仿真历史 |

### 性能预测 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/prediction/performance` | 性能预测 |
| POST | `/api/prediction/demand` | 需求预测 |

### AI分析 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/analyze` | AI智能分析（支持production/risk/report） |
| GET | `/api/ai/status` | AI服务状态检查 |

### 算法参数 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/algorithm/params` | 获取算法参数 |
| PUT | `/api/algorithm/params` | 更新算法参数 |

## 技术方案

### 算法实现

- **生产调度算法**：基于优先级评分、负载均衡和资源分配的多目标优化算法
- **性能预测算法**：指数平滑（Holt-Winters）结合移动平均，支持趋势和季节性分析
- **网络优化算法**：场景自适应切片参数优化，AI优化与传统方案对比评估
- **通感一体处理**：多模态感知数据融合处理，支持实时筛选和追踪

### AI集成

- 内置基于规则的AI分析引擎，提供即时优化建议
- 预留DeepSeek API接口，替换`DEEPSEEK_API_KEY_PLACEHOLDER`即可启用云端AI分析
- 混合架构：本地规则引擎 + 云端大模型（可选）

### 数据存储

- 内存数据存储，重启后数据重置
- 仿真历史上限100条，自动滚动
- 适合演示和测试场景

## 部署说明

### 环境要求

- Python 3.8+
- Flask 2.0+

### 安装依赖

```bash
pip install flask python-dotenv
```

### 启动服务

```bash
cd d:\python_chuangxin\5G-A
python app.py
```

访问 http://127.0.0.1:5000

### 配置DeepSeek API（可选）

编辑 `services/ai_agent.py`，修改以下配置：

```python
DEEPSEEK_CONFIG = {
    "api_key": "your-api-key-here",
    "enabled": True,
    ...
}
```

## 系统质量

- 全面的错误处理与日志记录
- CORS跨域支持
- 统一JSON响应格式 `{"success": bool, "data": ..., "message": "..."}`
- 请求追踪（X-Request-ID、X-Response-Time）
- 所有POST接口支持空请求体容错
- 前端告警消息3秒自动消失
- 响应式设计，支持多种屏幕尺寸

## 维护说明

- 日志文件：`logs/app_YYYYMMDD.log`
- 启动时自动创建日志目录
- 算法参数可通过`/api/algorithm/params`接口动态调整
- 仿真历史可通过API清空

## 版本历史

- v2.0.0 - 生产级系统重构，前后端打通，算法实现
- v1.0.0 - 初始版本