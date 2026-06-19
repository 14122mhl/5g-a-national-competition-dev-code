# ============================================
# AI智能分析Agent - 集成DeepSeek API
# 真实调用大模型进行智能分析与决策支持
# ============================================

import json
import os
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

from database import db
from models.db_models import AIAnalysisLog

load_dotenv()
logger = logging.getLogger(__name__)


class AIAgent:
    """AI智能分析代理 - 集成DeepSeek大模型"""

    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.api_endpoint = os.getenv('DEEPSEEK_API_ENDPOINT', 'https://api.deepseek.com/v1/chat/completions')
        self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.max_tokens = 2048
        self.temperature = 0.7

    def _is_api_available(self):
        """检查DeepSeek API是否可用"""
        # 测试模式下跳过API调用
        try:
            from flask import current_app
            if current_app and current_app.config.get('TESTING'):
                return False
        except Exception:
            pass
        return bool(self.api_key) and self.api_key != 'DEEPSEEK_API_KEY_PLACEHOLDER'

    def _call_deepseek_api(self, system_prompt, user_prompt):
        """
        调用DeepSeek API进行分析
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
        
        Returns:
            API返回的文本内容，失败返回None
        """
        if not self._is_api_available():
            logger.info("DeepSeek API未配置，使用本地算法分析")
            return None

        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }

            start_time = time.time()
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            elapsed = round(time.time() - start_time, 2)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                tokens = result.get("usage", {}).get("total_tokens", 0)
                logger.info(f"DeepSeek API调用成功, 耗时={elapsed}s, tokens={tokens}")
                return content, elapsed, tokens
            else:
                logger.error(f"DeepSeek API返回错误: {response.status_code} - {response.text}")
                return None, elapsed, 0

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return None, 0, 0

    def _log_analysis(self, analysis_type, input_data, output_data, api_called,
                      api_response_time=None, tokens_used=0, status='success', error_message=None):
        """记录AI分析日志到数据库"""
        try:
            log = AIAnalysisLog(
                analysis_type=analysis_type,
                input_data=json.dumps(input_data, ensure_ascii=False) if isinstance(input_data, dict) else str(input_data),
                output_data=json.dumps(output_data, ensure_ascii=False) if isinstance(output_data, (dict, list)) else str(output_data),
                api_called=api_called,
                api_response_time=api_response_time,
                tokens_used=tokens_used,
                status=status,
                error_message=error_message
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logger.warning(f"记录AI分析日志失败: {e}")
            db.session.rollback()

    def analyze_production(self, production_data):
        """
        分析生产数据并提供优化建议（真实调用DeepSeek）
        
        Args:
            production_data: 生产数据字典
        
        Returns:
            包含分析结果和AI建议的字典
        """
        system_prompt = """你是一个5G-A工业智能调度专家。请分析以下工业生产数据，给出专业的生产优化建议。
请从以下方面进行分析：
1. 生产效率优化建议
2. 资源分配优化方案
3. 潜在风险识别
4. 改进措施

请用中文输出，格式清晰，每条建议用序号标注。"""

        user_prompt = f"""当前工业生产数据分析：

生产数据摘要：
- 活跃产线数: {production_data.get('active_lines', 0)}
- 总任务数: {production_data.get('total_tasks', 0)}
- 已调度任务数: {production_data.get('scheduled_count', 0)}
- 调度率: {production_data.get('scheduled_rate', 0)}%

请基于以上数据给出专业分析。"""

        api_result, elapsed, tokens = self._call_deepseek_api(system_prompt, user_prompt)

        # 本地算法补充建议（当API不可用或作为补充）
        local_recommendations = [
            "基于负载均衡算法优化产线任务分配，优先使用高能效产线",
            "根据订单优先级实施动态调度，减少换型等待时间",
            "利用预测性维护减少非计划停机，提升设备综合效率(OEE)",
            "优化物料配送路线，降低在制品(WIP)库存积压",
            "通过实时质量监控实现缺陷早期预警，降低返工率"
        ]

        result = {
            "analysis_id": f"ANALYSIS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "data_summary": {
                "active_lines": production_data.get('active_lines', 0),
                "total_tasks": production_data.get('total_tasks', 0),
                "scheduled_rate": production_data.get('scheduled_rate', 0)
            },
            "ai_recommendations": local_recommendations,
            "deepseek_analysis": api_result,
            "api_called": api_result is not None,
            "confidence": 0.89 if api_result else 0.75,
            "timestamp": datetime.now().isoformat()
        }

        self._log_analysis(
            'production', production_data, result,
            api_called=api_result is not None,
            api_response_time=elapsed,
            tokens_used=tokens,
            status='success' if api_result else 'fallback'
        )

        return result

    def analyze_risk(self, network_data):
        """
        风险评估分析（调用DeepSeek + 本地规则引擎）
        
        Args:
            network_data: 网络状态数据
        
        Returns:
            风险评估结果
        """
        # 本地规则引擎：快速风险检测
        risks = []
        if network_data.get("packet_loss_rate", 0) > 0.1:
            risks.append({"level": "warning", "type": "高丢包率",
                          "detail": f"丢包率{network_data['packet_loss_rate']}超过阈值0.1%",
                          "suggestion": "检查网络拥塞控制策略"})
        if network_data.get("average_latency", 0) > 3:
            risks.append({"level": "warning", "type": "时延偏高",
                          "detail": f"平均时延{network_data['average_latency']}ms超过3ms阈值",
                          "suggestion": "优化URLLC资源配置"})
        if network_data.get("online_nodes", 0) < network_data.get("network_nodes", 1):
            risks.append({"level": "info", "type": "节点异常",
                          "detail": f"{network_data['network_nodes'] - network_data['online_nodes']}个节点离线",
                          "suggestion": "排查离线节点原因"})

        if not risks:
            risks.append({"level": "info", "type": "系统正常",
                          "detail": "当前网络运行状态良好，无显著风险",
                          "suggestion": "继续保持当前配置"})

        # 如果API可用，调用DeepSeek做深度分析
        if self._is_api_available():
            system_prompt = "你是一个5G-A网络运维专家，请分析网络状态数据并给出风险评估。"
            user_prompt = f"网络状态数据: {json.dumps(network_data, ensure_ascii=False)}\n已有风险: {json.dumps(risks, ensure_ascii=False)}\n请给出补充分析。"
            api_result, elapsed, tokens = self._call_deepseek_api(system_prompt, user_prompt)
        else:
            api_result = None
            elapsed = tokens = 0

        result = {
            "risk_count": len(risks),
            "overall_level": max((r["level"] for r in risks),
                                 key=lambda x: {"info": 0, "warning": 1, "critical": 2}.get(x, 0)),
            "risks": risks,
            "deepseek_analysis": api_result,
            "api_called": api_result is not None,
            "timestamp": datetime.now().isoformat()
        }

        self._log_analysis('risk', network_data, result,
                           api_called=api_result is not None,
                           api_response_time=elapsed, tokens_used=tokens)

        return result

    def get_optimization_report(self, scenario="medium"):
        """
        获取综合优化报告（调用DeepSeek生成专业报告）
        
        Args:
            scenario: 场景类型 (low/medium/high)
        
        Returns:
            优化报告
        """
        scenarios = {
            "low": {"latency_improvement": 44, "throughput_improvement": 18, "energy_saving": 12},
            "medium": {"latency_improvement": 38, "throughput_improvement": 22, "energy_saving": 15},
            "high": {"latency_improvement": 42, "throughput_improvement": 25, "energy_saving": 18}
        }
        data = scenarios.get(scenario, scenarios["medium"])

        if self._is_api_available():
            system_prompt = "你是一个5G-A工业网络优化专家，请生成一份专业的网络优化报告。"
            user_prompt = f"""场景: {scenario}负载
当前指标: 时延改善{data['latency_improvement']}%, 吞吐量提升{data['throughput_improvement']}%, 节能{data['energy_saving']}%
请生成一份简明扼要的优化报告，包含4条关键建议。"""
            api_result, elapsed, tokens = self._call_deepseek_api(system_prompt, user_prompt)
        else:
            api_result = None
            elapsed = tokens = 0

        recommendations = api_result.split('\n') if api_result else [
            "启用AI驱动的自适应调度，实时响应生产变化",
            "部署预测性维护模型，减少突发故障",
            "实施能源消耗智能监控，优化峰谷用电",
            "引入数字孪生技术，提升生产过程透明度"
        ]

        # 过滤掉空行
        if isinstance(recommendations, list):
            recommendations = [r.strip() for r in recommendations if r.strip() and len(r.strip()) > 5]

        result = {
            "scenario": scenario,
            "metrics": {
                "latency_improvement": f"{data['latency_improvement']}%",
                "throughput_improvement": f"{data['throughput_improvement']}%",
                "energy_saving": f"{data['energy_saving']}%",
                "cost_reduction": f"{round(data['energy_saving'] * 0.8, 1)}%",
                "quality_improvement": f"{round(data['throughput_improvement'] * 0.15, 1)}%"
            },
            "recommendations": recommendations,
            "deepseek_analysis": api_result,
            "api_called": api_result is not None,
            "timestamp": datetime.now().isoformat()
        }

        self._log_analysis('report', {"scenario": scenario}, result,
                           api_called=api_result is not None,
                           api_response_time=elapsed, tokens_used=tokens)

        return result

    def get_ai_status(self):
        """获取AI服务状态"""
        return {
            "deepseek_enabled": self._is_api_available(),
            "api_endpoint": self.api_endpoint if self._is_api_available() else None,
            "model": self.model if self._is_api_available() else None,
            "algorithm_modules": ["scheduler", "predictor", "sensing", "optimizer"],
            "status": "ready" if self._is_api_available() else "local_only"
        }

    def generate_analysis_report(self, context):
        """基于上下文数据生成AI分析报告（DeepSeek驱动）"""
        analysis_type = context.get('type', 'scheduling')
        company = context.get('company', '佳帮手集团')

        # 构建提示词
        prompts = {
            'scheduling': f"""你是一个制造业智能调度专家。请分析以下佳帮手兴平智造基地的调度数据，给出专业的调度优化建议：

当前状态：
- 待处理任务: {context.get('pending_tasks', 0)} 个
- 进行中任务: {context.get('in_progress_tasks', 0)} 个
- 已完成任务: {context.get('completed_tasks', 0)} 个
- 在线AGV: {context.get('online_agvs', 0)} 台
- 紧急任务(优先级1-2): {context.get('urgent_tasks', 0)} 个

请输出：
1. 调度效率评估（一句话）
2. 存在的瓶颈问题（1-2条）
3. 优化建议（2-3条，每条不超过30字）
4. 风险预警（如有）
请用JSON格式返回，键名为: efficiency, bottlenecks(array), suggestions(array), risks(array)。""",

            'network': f"""你是一个5G网络优化专家。请分析佳帮手兴平智造基地的网络状态：

当前状态：
- 24小时内严重事件: {context.get('critical_events_24h', 0)} 次
- 活跃生产区域: {context.get('zones', 0)} 个
- 网络切片: {len(context.get('slices', []))} 个

请输出：
1. 网络健康度评估
2. 需要关注的问题
3. 优化建议
请用JSON格式返回，键名为: health, issues(array), suggestions(array)。""",

            'production': f"""你是一个制造业生产管理专家。请分析佳帮手兴平智造基地的生产状态：

当前状态：
- 待处理订单: {context.get('pending_orders', 0)} 个
- 活跃生产区域: {context.get('active_zones', 0)} 个
- 设备总数: {context.get('total_devices', 0)} 台
- 在线设备: {context.get('device_online', 0)} 台

请输出：
1. 产能利用率评估
2. 生产瓶颈分析
3. 优化建议
请用JSON格式返回，键名为: utilization, bottlenecks(array), suggestions(array)。""",

            'prediction': f"""你是一个工业数据分析专家。请分析佳帮手兴平智造基地的近期趋势数据：

网络负载趋势: {context.get('recent_load', [])}
AGV活跃趋势: {context.get('recent_agv', [])}

请预测未来趋势并给出建议。请用JSON格式返回，键名为: trend, prediction, suggestions(array)。""",

            'quick_insight': f"""你是一个制造业智能调度助手。请根据以下佳帮手兴平智造基地的实时状态，用一句话总结当前情况：

- 待处理任务: {context.get('pending_tasks', 0)} 个
- 1小时内严重网络事件: {context.get('critical_events_1h', 0)} 次
- 在线AGV: {context.get('online_agvs', 0)} 台

请直接返回一句话总结（不超过50字），不要JSON格式。"""
        }

        prompt = prompts.get(analysis_type, prompts['scheduling'])

        # 尝试调用DeepSeek API
        api_result = self._call_llm(prompt)

        if api_result:
            return {
                "type": analysis_type,
                "analysis": api_result,
                "source": "deepseek",
                "timestamp": datetime.now().isoformat()
            }

        # 本地回退分析
        local_result = self._local_analysis(context)
        return {
            "type": analysis_type,
            "analysis": local_result,
            "source": "local",
            "timestamp": datetime.now().isoformat()
        }

    def generate_quick_insight(self, context):
        """生成快速洞察"""
        result = self.generate_analysis_report(context)
        return result.get('analysis', '系统运行正常')

    def _call_llm(self, prompt):
        """调用LLM API（DeepSeek）"""
        if not self._is_api_available():
            return None
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的制造业智能调度助手，服务于佳帮手集团的确定性网络智能调度平台。请用中文回答，保持专业和简洁。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            return None
        except Exception as e:
            logger.warning(f"LLM API调用失败: {e}")
            return None

    def _local_analysis(self, context):
        """本地分析回退"""
        analysis_type = context.get('type', 'scheduling')
        if analysis_type == 'scheduling':
            pending = context.get('pending_tasks', 0)
            urgent = context.get('urgent_tasks', 0)
            agv = context.get('online_agvs', 0)
            if pending > 20:
                eff = "调度负载较高，存在任务积压风险"
                suggestions = ["建议增加AGV调度数量", "提高紧急任务优先级", "优化任务分配算法"]
            elif urgent > 5:
                eff = "紧急任务较多，需要优先处理"
                suggestions = ["优先处理紧急任务", "减少非紧急任务调度"]
            else:
                eff = "调度系统运行正常，效率良好"
                suggestions = ["可适当增加调度任务量", "保持当前调度策略"]
            return f"效率评估: {eff}。建议: {'; '.join(suggestions[:2])}"

        elif analysis_type == 'network':
            critical = context.get('critical_events_24h', 0)
            if critical > 0:
                return f"网络存在{critical}次严重事件，建议检查URLLC切片稳定性并优化带宽分配"
            return "网络运行稳定，所有切片SLA达标，无需干预"

        elif analysis_type == 'production':
            pending = context.get('pending_orders', 0)
            online = context.get('device_online', 0)
            total = context.get('total_devices', 0)
            rate = round(online / total * 100, 1) if total else 0
            return f"设备在线率{rate}%，待处理订单{pending}个。{'建议启动备用产线' if pending > 50 else '产能充足，运行正常'}"

        elif analysis_type == 'prediction':
            return "基于近期趋势，预计未来2小时网络负载将保持稳定，AGV调度效率可维持当前水平"

        return "系统运行正常，暂无异常"

    def get_analysis_logs(self, limit=20):
        """获取AI分析历史日志"""
        logs = AIAnalysisLog.query.order_by(
            AIAnalysisLog.created_at.desc()
        ).limit(limit).all()
        return [l.to_dict() for l in logs]


ai_agent = AIAgent()