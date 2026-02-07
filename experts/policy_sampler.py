import json
import logging
from typing import Any

from .base_expert import BaseExpert

logger = logging.getLogger(__name__)


class PolicySampler(BaseExpert):
    def __init__(self):
        super().__init__(
            name="PolicySampler",
            description="Semantic Intent Classifier & Strategy Planner.",
            version="2.0-Semantic",
            model_name="llama3.1:latest",  # Используем быструю модель
        )

    def classify_intent(self, prompt: str) -> dict:
        """
        Определяет намерение пользователя и сложность задачи.
        Возвращает JSON: { "intent":Str, "difficulty":Int, "expert":Str }
        """
        system_prompt = (
            "You are the brain's router. Analyze the user prompt. "
            "Classify into one of: [CODING, RESEARCH, REASONING, CHAT]. "
            "Select the best expert: [CodeExpert, ResearchExpert, ReasoningExpert]. "
            "Estimate difficulty (1-10). "
            'Return JSON ONLY: {"intent": "...", "expert": "...", "difficulty": int}'
        )

        try:
            # Быстрый запрос к LLM
            response = self._ask_model(prompt, system_prompt)

            # Чистим JSON
            clean_json = response.replace("```json", "").replace("```", "").strip()
            if "{" not in clean_json:
                raise ValueError("No JSON")

            data = json.loads(clean_json)
            return data
        except Exception as e:
            logger.warning(f"Routing failed, fallback to rules. Error: {e}")
            return self._fallback_routing(prompt)

    def _fallback_routing(self, prompt: str) -> dict:
        """Запасной вариант на if/else, если LLM выдала мусор."""
        p = prompt.lower()
        if any(w in p for w in ["код", "code", "python", "script"]):
            return {"intent": "CODING", "expert": "CodeExpert", "difficulty": 5}
        if any(w in p for w in ["поиск", "найди", "research", "кто", "когда"]):
            return {"intent": "RESEARCH", "expert": "ResearchExpert", "difficulty": 3}
        return {"intent": "REASONING", "expert": "ReasoningExpert", "difficulty": 5}

    def run(self, context: dict) -> str:
        # Этот метод для совместимости, основная логика теперь в classify_intent
        return "PolicySampler active."
