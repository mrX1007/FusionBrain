from typing import Any

from fusionbrain.experts.base_expert import BaseExpert


class CriticExpert(BaseExpert):
    def __init__(self):
        super().__init__(
            name="CriticExpert",
            description="Reviews logic and safety using LLM.",
            version="2.0-Real",
            model_name="llama3.1",  # qwen2.5, или mistral
        )

    def _perform_task(self, context: dict[str, Any]) -> str:
        prompt = context.get("prompt", "")

        system = (
            "Ты — строгий критик. Твоя задача — найти логические ошибки, "
            "двусмысленности или проблемы безопасности в запросе пользователя. "
            "Будь краток и конструктивен."
        )

        critique = self._ask_model(f"Проанализируй этот запрос: '{prompt}'", system_prompt=system)

        return f"### ⚖️ Critic Review\n{critique}"

    def evaluate_answer(self, prompt: str, answer: str) -> dict[str, Any]:
        return {"score": 0.8, "feedback": "LLM check passed (simulated)."}
