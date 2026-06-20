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
        """基于上下文数据生成AI分析报告（DeepSeek驱动）—— 返回JSON数据块 + 简短建议"""
        import time as time_module
        analysis_type = context.get('type', 'scheduling')
        company = context.get('company', '佳帮手集团')

        # 构建提示词：要求DeepSeek严格返回JSON格式
        prompts = {
            'scheduling': f"""你是一个制造业智能调度专家。请分析以下佳帮手兴平智造基地的调度数据，给出专业分析。

当前状态：
- 待处理任务: {context.get('pending_tasks', 0)} 个
- 进行中任务: {context.get('in_progress_tasks', 0)} 个
- 已完成任务: {context.get('completed_tasks', 0)} 个
- 在线AGV: {context.get('online_agvs', 0)} 台
- 紧急任务(优先级1-2): {context.get('urgent_tasks', 0)} 个

请严格按以下JSON格式返回（不要包含任何其他文字）：
{{
  "efficiency": "调度效率评估（一句话，不超过30字）",
  "load_status": "正常/偏高/严重",
  "bottlenecks": ["瓶颈1", "瓶颈2"],
  "suggestions": ["建议1（不超过30字）", "建议2（不超过30字）", "建议3（不超过30字）"],
  "risks": ["风险预警1", "风险预警2"],
  "score": 85
}}""",

            'network': f"""你是一个5G网络优化专家。请分析佳帮手兴平智造基地的网络状态。

当前状态：
- 24小时内严重事件: {context.get('critical_events_24h', 0)} 次
- 活跃生产区域: {context.get('zones', 0)} 个
- 网络切片数: {len(context.get('slices', []))} 个
- 切片详情: {json.dumps(context.get('slices', []), ensure_ascii=False)}

请严格按以下JSON格式返回：
{{
  "health": "网络健康度评估（一句话）",
  "health_status": "优秀/良好/一般/需关注",
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1（不超过30字）", "建议2（不超过30字）"],
  "score": 85
}}""",

            'production': f"""你是一个制造业生产管理专家。请分析佳帮手兴平智造基地的生产状态。

当前状态：
- 待处理订单: {context.get('pending_orders', 0)} 个
- 活跃生产区域: {context.get('active_zones', 0)} 个
- 设备总数: {context.get('total_devices', 0)} 台
- 在线设备: {context.get('device_online', 0)} 台
- 设备在线率: {round(context.get('device_online', 0) / max(context.get('total_devices', 1), 1) * 100, 1)}%

请严格按以下JSON格式返回：
{{
  "utilization": "产能利用率评估（一句话）",
  "utilization_status": "充足/适中/紧张/严重不足",
  "bottlenecks": ["瓶颈1", "瓶颈2"],
  "suggestions": ["建议1（不超过30字）", "建议2（不超过30字）"],
  "score": 80
}}""",

            'prediction': f"""你是一个工业数据分析专家。请分析佳帮手兴平智造基地的数据趋势。

网络负载趋势（最近24个采样点）: {context.get('recent_load', [])[-6:]}
AGV活跃趋势: {context.get('recent_agv', [])[-6:]}
带宽趋势: {context.get('recent_bandwidth', [])[-6:]}

请严格按以下JSON格式返回：
{{
  "trend": "趋势判断（上升/稳定/下降，一句话）",
  "prediction": "未来2小时预测（一句话）",
  "suggestions": ["建议1（不超过30字）", "建议2（不超过30字）"],
  "score": 75
}}""",

            'quick_insight': f"""你是一个制造业智能调度助手。请根据以下佳帮手兴平智造基地的实时状态，用一句话总结当前情况：

- 待处理任务: {context.get('pending_tasks', 0)} 个
- 1小时内严重网络事件: {context.get('critical_events_1h', 0)} 次
- 在线AGV: {context.get('online_agvs', 0)} 台

请直接返回一句话总结（不超过50字），不要JSON格式。"""
        }

        prompt = prompts.get(analysis_type, prompts['scheduling'])

        # 模拟1秒分析时间（让用户感知到AI正在分析）
        time_module.sleep(1.0)

        # 尝试调用DeepSeek API
        api_result = self._call_llm_structured(prompt)

        if api_result:
            return {
                "type": analysis_type,
                "data": api_result,
                "suggestions": api_result.get("suggestions", []),
                "source": "deepseek",
                "score": api_result.get("score", 85),
                "timestamp": datetime.now().isoformat()
            }

        # 本地回退分析（JSON格式）
        local = self._local_analysis_structured(context)
        return {
            "type": analysis_type,
            "data": local,
            "suggestions": local.get("suggestions", []),
            "source": "local",
            "score": local.get("score", 70),
            "timestamp": datetime.now().isoformat()
        }

    def _call_llm_structured(self, prompt):
        """调用LLM API并尝试解析JSON结果"""
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
                    {"role": "system", "content": "你是一个专业的制造业智能调度助手，服务于佳帮手集团的确定性网络智能调度平台。请严格按JSON格式输出，不要包含任何其他文字或markdown标记。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 800
            }
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content'].strip()
                # 尝试解析JSON
                # 去掉可能的markdown代码块标记
                if content.startswith('```'):
                    lines = content.split('\n')
                    content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
                    content = content.strip()
                result = json.loads(content)
                return result
            return None
        except json.JSONDecodeError:
            logger.warning(f"DeepSeek返回非JSON格式: {content[:200]}")
            return None
        except Exception as e:
            logger.warning(f"LLM API调用失败: {e}")
            return None

    def _local_analysis_structured(self, context):
        """本地分析回退（结构化JSON格式）"""
        analysis_type = context.get('type', 'scheduling')
        if analysis_type == 'scheduling':
            pending = context.get('pending_tasks', 0)
            urgent = context.get('urgent_tasks', 0)
            in_progress = context.get('in_progress_tasks', 0)
            agv = context.get('online_agvs', 0)
            completed = context.get('completed_tasks', 0)

            if pending > 100:
                eff = "调度负载严重偏高，存在大量任务积压"
                load = "严重"
                bottlenecks = [f"待处理任务{pending}个严重积压", f"在线AGV仅{agv}台，运力不足"]
                suggestions = ["立即增加AGV调度数量", "启动备用运输通道", "提高紧急任务优先级至最高", "暂停非关键任务调度"]
                risks = [f"任务积压可能导致产线停线", "紧急任务延迟交付风险"]
                score = 45
            elif pending > 50:
                eff = "调度负载偏高，存在任务积压风险"
                load = "偏高"
                bottlenecks = [f"待处理任务{pending}个超过安全线", f"紧急任务{urgent}个需优先处理"]
                suggestions = ["增加AGV调度批次", "优化任务分配算法", "提高紧急任务优先级"]
                risks = ["持续积压可能影响交付周期"]
                score = 65
            elif urgent > 5:
                eff = "紧急任务较多，调度系统正在优先处理"
                load = "正常"
                bottlenecks = [f"紧急任务{urgent}个需关注"]
                suggestions = ["优先处理紧急任务", "合理安排非紧急任务"]
                risks = []
                score = 78
            else:
                eff = "调度系统运行正常，任务流转顺畅"
                load = "正常"
                bottlenecks = []
                suggestions = ["保持当前调度策略", "可适当增加任务投放量"]
                risks = []
                score = 92

            return {
                "efficiency": eff,
                "load_status": load,
                "bottlenecks": bottlenecks,
                "suggestions": suggestions,
                "risks": risks,
                "score": score
            }

        elif analysis_type == 'network':
            critical = context.get('critical_events_24h', 0)
            if critical > 5:
                health = f"网络存在{critical}次严重事件，稳定性堪忧"
                status = "需关注"
                issues = [f"24小时内{critical}次严重事件", "URLLC切片SLA可能不达标"]
                suggestions = ["检查URLLC切片配置", "优化带宽分配策略", "排查网络设备故障"]
                score = 50
            elif critical > 0:
                health = f"网络出现{critical}次严重事件，需持续监控"
                status = "一般"
                issues = [f"24小时内{critical}次严重事件"]
                suggestions = ["加强网络监控", "检查高危节点"]
                score = 70
            else:
                health = "网络运行稳定，所有切片SLA达标"
                status = "优秀"
                issues = []
                suggestions = ["保持当前网络配置", "定期巡检关键设备"]
                score = 95
            return {
                "health": health,
                "health_status": status,
                "issues": issues,
                "suggestions": suggestions,
                "score": score
            }

        elif analysis_type == 'production':
            pending = context.get('pending_orders', 0)
            online = context.get('device_online', 0)
            total = context.get('total_devices', 1)
            rate = round(online / max(total, 1) * 100, 1)
            if rate < 80:
                utilization = f"设备在线率仅{rate}%，产能利用率不足"
                status = "严重不足"
                bottlenecks = [f"设备在线率{rate}%偏低", f"待处理订单{pending}个"]
                suggestions = ["排查离线设备原因", "启动备用设备", "优先处理积压订单"]
                score = 50
            elif pending > 100:
                utilization = f"设备在线率{rate}%，但订单积压{pending}个"
                status = "紧张"
                bottlenecks = [f"待处理订单{pending}个积压"]
                suggestions = ["增加产线班次", "提高设备利用率", "优化排产计划"]
                score = 65
            else:
                utilization = f"设备在线率{rate}%，产能充足"
                status = "充足"
                bottlenecks = []
                suggestions = ["保持当前产能", "关注设备维护计划"]
                score = 88
            return {
                "utilization": utilization,
                "utilization_status": status,
                "bottlenecks": bottlenecks,
                "suggestions": suggestions,
                "score": score
            }

        elif analysis_type == 'prediction':
            loads = context.get('recent_load', [])
            if loads:
                avg = sum(loads) / len(loads)
                if avg > 80:
                    trend = "网络负载持续偏高，呈上升趋势"
                    prediction = "预计未来2小时网络负载将继续上升，建议提前扩容"
                    suggestions = ["提前申请带宽扩容", "优化非关键业务流量", "准备应急降级方案"]
                    score = 55
                else:
                    trend = "网络负载处于正常范围，趋势稳定"
                    prediction = "预计未来2小时网络负载将保持稳定"
                    suggestions = ["保持当前网络配置", "按计划执行常规维护"]
                    score = 82
            else:
                trend = "数据不足，趋势待观察"
                prediction = "需更多数据点进行趋势预测"
                suggestions = ["增加数据采集密度", "建立基线数据模型"]
                score = 60
            return {
                "trend": trend,
                "prediction": prediction,
                "suggestions": suggestions,
                "score": score
            }

        return {"message": "系统运行正常，暂无异常", "suggestions": ["保持当前策略"], "score": 75}

    def generate_quick_insight(self, context):
        """生成快速洞察"""
        result = self.generate_analysis_report(context)
        data = result.get('data', {})
        if isinstance(data, dict):
            return data.get('efficiency', data.get('health', data.get('utilization', data.get('message', '系统运行正常'))))
        return str(data) if data else '系统运行正常'

    def get_analysis_logs(self, limit=20):
        """获取AI分析历史日志"""
        logs = AIAnalysisLog.query.order_by(
            AIAnalysisLog.created_at.desc()
        ).limit(limit).all()
        return [l.to_dict() for l in logs]


ai_agent = AIAgent()