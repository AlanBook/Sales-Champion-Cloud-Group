from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProviderContext:
    prompt_name: str
    business_goal: str


class LLMProvider:
    provider_name = "base"

    def render_hint(self, context: ProviderContext) -> str:
        return f"{self.provider_name}:{context.prompt_name}:{context.business_goal}"
