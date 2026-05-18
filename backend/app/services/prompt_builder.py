from app.core.logging import get_logger

logger = get_logger(__name__)


class PromptBuilder:
    @staticmethod
    def build_alert_analysis_prompt(alert_data: dict) -> str:
        return (
            f"你是一个专业的运维 AI 助手。请分析以下告警信息并给出专业建议：\n\n"
            f"告警名称：{alert_data.get('trigger_name', '未知')}\n"
            f"主机：{alert_data.get('host_name', '未知')} ({alert_data.get('host_ip', '未知')})\n"
            f"严重级别：{alert_data.get('severity_label', '未知')} ({alert_data.get('severity', 0)})\n"
            f"监控项：{alert_data.get('item_key', '未知')}\n"
            f"当前值：{alert_data.get('item_value', '未知')}\n\n"
            f"请按以下 JSON 格式返回分析结果：\n"
            f'{{\n'
            f'  "summary": "告警摘要",\n'
            f'  "possible_causes": ["原因1", "原因2"],\n'
            f'  "suggested_actions": ["建议1", "建议2"],\n'
            f'  "risk_level": "low|medium|high|critical",\n'
            f'  "confidence": 0.0-1.0,\n'
            f'  "need_human_confirm": true/false\n'
            f'}}'
        )

    @staticmethod
    def build_storm_summary_prompt(alerts_data: list[dict]) -> str:
        alert_summaries = "\n".join(
            f"- [{a.get('severity_label', '?')}] {a.get('trigger_name', '?')} on {a.get('host_name', '?')}"
            for a in alerts_data[:20]
        )
        return (
            f"检测到告警风暴，共 {len(alerts_data)} 条告警。请生成聚合摘要：\n\n"
            f"{alert_summaries}\n\n"
            f"请按以下 JSON 格式返回：\n"
            f'{{\n'
            f'  "summary": "风暴聚合摘要",\n'
            f'  "possible_causes": ["主要原因"],\n'
            f'  "suggested_actions": ["紧急建议"],\n'
            f'  "risk_level": "critical",\n'
            f'  "confidence": 0.0-1.0,\n'
            f'  "need_human_confirm": true\n'
            f'}}'
        )
