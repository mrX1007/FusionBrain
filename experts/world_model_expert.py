import json
import logging

from .base_expert import BaseExpert

logger = logging.getLogger(__name__)


class WorldModelExpert(BaseExpert):
    def __init__(self):
        super().__init__(
            name="WorldModel",
            description="Maintains the global state.",
            version="2.0-Stateful",
            model_name="qwen2.5-coder:32b",  # <--- CHANGED
        )
        self.state = {
            "user_intent": None,
            "constraints": [],
            "risk_level": "unknown",
            "current_step": 0,
        }

    def run(self, context: dict) -> str:
        prompt = context.get("prompt", "")
        self._update_state(prompt)

        simulated_outcome = self._simulate_outcome(prompt)

        return (
            f"### 🌍 World State Snapshot\n"
            f"- Intent: {self.state['user_intent']}\n"
            f"- Risk: {self.state['risk_level']}\n"
            f"- Simulation: {simulated_outcome}"
        )

    def _update_state(self, prompt: str):
        """Парсит промпт и обновляет переменные состояния."""
        if "код" in prompt or "python" in prompt:
            self.state["user_intent"] = "coding"
        elif "research" in prompt or "найди" in prompt:
            self.state["user_intent"] = "research"
        else:
            self.state["user_intent"] = "general_chat"

        if "удалить" in prompt or "hack" in prompt:
            self.state["risk_level"] = "HIGH"
        else:
            self.state["risk_level"] = "LOW"

    def _simulate_outcome(self, action: str) -> str:
        """
        Предсказывает результат действий (Look-ahead).
        """
        if self.state["risk_level"] == "HIGH":
            return "⛔ BLOCK: Action leads to system instability or violation."

        if self.state["user_intent"] == "coding":
            return "✅ SUCCESS: Code execution probable. Syntax check required."

        return "ℹ️ NEUTRAL: Standard interaction."
