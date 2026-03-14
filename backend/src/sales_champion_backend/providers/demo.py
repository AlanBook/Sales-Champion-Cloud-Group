from sales_champion_backend.providers.base import LLMProvider, ProviderContext


class DemoLLMProvider(LLMProvider):
    provider_name = "demo"

    def render_hint(self, context: ProviderContext) -> str:
        return (
            f"demo-provider::{context.prompt_name}::"
            f"围绕{context.business_goal}输出结构化结果，不做自由发挥。"
        )
