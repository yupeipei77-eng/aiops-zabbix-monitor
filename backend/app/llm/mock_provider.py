from app.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    async def analyze_alert(self, prompt: str) -> dict:
        return {
            "summary": "检测到系统资源异常，可能存在性能瓶颈或配置问题，建议进一步排查系统负载和资源使用情况。",
            "possible_causes": [
                "业务流量突增导致资源消耗加大",
                "存在异常进程占用大量系统资源",
                "系统配置不合理，未充分利用资源",
            ],
            "suggested_actions": [
                "检查系统资源使用情况（CPU/内存/磁盘/网络）",
                "查看近期流量和负载变化趋势",
                "评估是否需要扩容或优化配置",
            ],
            "risk_level": "medium",
            "confidence": 0.75,
            "need_human_confirm": False,
        }

    async def chat(self, messages: list[dict]) -> str:
        return "这是 Mock AI 助手的回复。当前为测试模式，不会调用真实模型。"

    async def health_check(self) -> bool:
        return True
