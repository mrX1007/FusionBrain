import logging
from typing import Any

from fusionbrain.experts.base_expert import BaseExpert
from fusionbrain.experts.quantum_expert import QuantumExpert

logger = logging.getLogger(__name__)


class WorldModelExpert(BaseExpert):
    """
    WORLD MODEL (SYSTEM 2+).

    Роль: Симулятор Будущего.
    Задача: Взять стратегию ReasoningExpert и проверить её на прочность
    в вероятностной квантовой среде (Qiskit Entanglement).
    """

    def __init__(self):
        super().__init__(
            name="WorldModelExpert",
            description="Simulates execution scenarios using Quantum Probabilities.",
            version="1.0-Simulation",
            model_name="llama3.1",
        )
        self.quantum_simulator = QuantumExpert()

    def _perform_task(self, context: dict[str, Any]) -> str:
        full_context = context.get("prompt", "")
        if len(full_context) < 50:
            return ""

        strategy_action = self._extract_strategy(full_context)

        agents = ["Environment (Market/System)", "Resistance (Competitor/Bugs)", "Agent Action"]
        sim_result = self.quantum_simulator.simulate_world_scenario(agents, strategy_action)
        advisory = ""
        if "NEGATIVE" in sim_result:
            advisory = "⛔️ CRITICAL WARNING: High failure probability detected. CodeExpert should add extra error handling or fallback mechanisms."
        elif "POSITIVE" in sim_result:
            advisory = "✅ GREEN LIGHT: Strategy appears robust. Proceed with implementation."
        else:
            advisory = "⚠️ CAUTION: Outcome is chaotic. Implement carefully."

        output = [
            "### 🔮 World Model Simulation (Pre-Mortem Analysis)",
            "",
            f"**Simulated Scenario:** '{strategy_action}'",
            "",
            f"{sim_result}",
            "",
            f"**System Advisory:** {advisory}",
        ]

        return "\n".join(output)

    def _extract_strategy(self, text: str) -> str:
        """
        Использует LLM, чтобы вычленить из длинного текста ReasoningExpert
        одно главное действие для симуляции.
        """
        recent_context = text[-2000:]

        system = (
            "Ты — аналитик систем. Твоя задача — прочитать мысли предыдущего эксперта "
            "и выделить ГЛАВНОЕ ПРЕДЛАГАЕМОЕ ДЕЙСТВИЕ в 2-5 словах на английском.\n"
            "Примеры: 'Aggressive Refactoring', 'High Risk Investment', 'Conservative Patch', 'System Reboot'.\n"
            "Если действие рискованное, обязательно добавь слово 'Risk'."
        )

        action = self._ask_model(
            f"Context:\n{recent_context}\n\nExtract Main Action:", system_prompt=system
        )
        return action.strip().replace('"', "").replace("'", "").split("\n")[0]
