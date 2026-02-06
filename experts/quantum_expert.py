import logging
import math
import random
from typing import Any

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

from fusionbrain.experts.base_expert import BaseExpert

logger = logging.getLogger(__name__)


class QuantumExpert(BaseExpert):
    """
    Advanced Quantum Expert powered by IBM Qiskit.

    Функционал:
    1. Decision Making: Алгоритм Гровера для выбора лучшей гипотезы.
    2. World Modeling: Симуляция сценариев через квантовую запутанность (Entanglement).
    """

    def __init__(self):
        super().__init__(
            name="QuantumExpert",
            description="Uses IBM Qiskit (Grover & Entanglement) for decision making and simulation.",
            version="4.0-Hybrid",
        )
        self.shots = 1024

        if QISKIT_AVAILABLE:
            self.backend = AerSimulator()
            logger.info("[QuantumExpert] Qiskit Aer backend initialized.")
        else:
            logger.warning("[QuantumExpert] Qiskit not found. Using mock simulation.")

    def _perform_task(self, context: dict[str, Any]) -> str:
        """
        Стандартный метод запуска (используется ReasoningExpert для выбора гипотез).
        """
        prompt = context.get("prompt", "")

        scenarios = self._generate_scenarios(prompt)

        if QISKIT_AVAILABLE:
            simulation_result = self._run_quantum_circuit(scenarios)
            method_name = "IBM Qiskit (Grover's Search)"
        else:
            simulation_result = self._run_mock_simulation(scenarios)
            method_name = "Pseudo-Random (Mock)"

        best_outcome = max(simulation_result, key=simulation_result.get)

        response = [
            f"### ⚛️ Quantum Expert (Engine: {method_name})",
            f"Shots: {self.shots} | States: {len(scenarios)}",
            "",
            "--- 🌌 Quantum Interference Results ---",
        ]

        sorted_res = sorted(simulation_result.items(), key=lambda x: x[1], reverse=True)

        for outcome, probability in sorted_res:
            bar_len = int(probability * 25)
            bar = "█" * bar_len + "░" * (25 - bar_len)
            response.append(f"{outcome:<30} |{bar}| {probability * 100:.1f}%")

        response.append("")
        response.append(f"**Коллапс волновой функции:**\n_{best_outcome}_")

        return "\n".join(response)

    def simulate_world_scenario(self, agents: list[str], actions: str) -> str:
        """
        Создает квантовую симуляцию взаимодействия агентов для WorldModelExpert.
        Использует запутанность кубитов для моделирования хаоса и причинно-следственных связей.
        """
        if not QISKIT_AVAILABLE:
            return "Simulation skipped (No Qiskit backend found)."

        num_qubits = 4
        qc = QuantumCircuit(num_qubits, num_qubits)

        qc.h(0)

        qc.rx(math.pi / 3, 1)
        is_risky = any(word in actions.lower() for word in ["risk", "риск", "all-in", "агрессив"])

        if is_risky:
            qc.x(2)  # Жесткое решение
        else:
            qc.h(2)  # Гибкое решение

        qc.cx(0, 1)
        qc.ccx(1, 2, 3)
        qc.ry(math.pi / 4, 3)

        qc.measure(range(num_qubits), range(num_qubits))

        try:
            circ = transpile(qc, self.backend)
            result = self.backend.run(circ, shots=self.shots).result()
            counts = result.get_counts(circ)
        except Exception as e:
            return f"Quantum Simulation Failed: {e}"

        success_count = 0
        total_runs = 0

        for state, count in counts.items():
            total_runs += count
            if state.startswith("0"):
                success_count += count

        probability = (success_count / total_runs) * 100

        # Интерпретация
        if probability > 70:
            outcome = "POSITIVE (Stable Outcome)"
        elif probability < 40:
            outcome = "NEGATIVE (High Failure Risk)"
        else:
            outcome = "UNCERTAIN (Chaotic System)"

        return (
            f"Simulation Results ({self.shots} Parallel Universes):\n"
            f"- Scenario Input: {actions}\n"
            f"- Success Probability: {probability:.1f}%\n"
            f"- Quantum Logic: Entanglement (Market -> Opponent -> Outcome)\n"
            f"- Verdict: {outcome}"
        )

    def _run_quantum_circuit(self, scenarios: list[str]) -> dict[str, float]:
        """
        Реализация Алгоритма Гровера для 2 кубитов (4 сценария).
        Цель: Усилить амплитуду 'Целевого' (позитивного) состояния.
        """
        n_scenarios = len(scenarios)

        if n_scenarios != 4:
            return self._run_superposition_only(scenarios)

        n_qubits = 2
        qc = QuantumCircuit(n_qubits)
        qc.h([0, 1])
        qc.x([0, 1])
        qc.cz(0, 1)
        qc.x([0, 1])
        qc.h([0, 1])
        qc.x([0, 1])
        qc.cz(0, 1)
        qc.x([0, 1])
        qc.h([0, 1])

        qc.measure_all()

        circ = transpile(qc, self.backend)
        result = self.backend.run(circ, shots=self.shots).result()
        counts = result.get_counts(circ)

        final_probs = {s: 0.0 for s in scenarios}
        bit_map = {"00": 0, "01": 1, "10": 2, "11": 3}

        for bitstring, count in counts.items():
            clean_bits = bitstring.replace(" ", "")
            idx = bit_map.get(clean_bits)

            if idx is not None and idx < len(scenarios):
                final_probs[scenarios[idx]] = count / self.shots

        return final_probs

    def _run_superposition_only(self, scenarios: list[str]) -> dict[str, float]:
        """Фолбэк: Просто случайная суперпозиция (если сценариев != 4)."""
        n_qubits = math.ceil(math.log2(len(scenarios)))
        qc = QuantumCircuit(n_qubits)
        for q in range(n_qubits):
            qc.h(q)
        qc.measure_all()

        circ = transpile(qc, self.backend)
        result = self.backend.run(circ, shots=self.shots).result()
        counts = result.get_counts(circ)

        final_probs = {s: 0.0 for s in scenarios}
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for i, (bs, count) in enumerate(sorted_counts):
            if i < len(scenarios):
                final_probs[scenarios[i]] = count / self.shots
        return final_probs

    def _run_mock_simulation(self, scenarios: list[str]) -> dict[str, float]:
        """Заглушка без Qiskit."""
        results = random.choices(scenarios, k=self.shots)
        counts = {s: results.count(s) for s in scenarios}
        return {k: v / self.shots for k, v in counts.items()}

    def _generate_scenarios(self, prompt: str) -> list[str]:
        """
        Генерация 4-х сценариев для алгоритма.
        Важно: 1-й сценарий (index 0) будет "целевым" для Оракула.
        """
        p = prompt.lower()
        if "код" in p or "code" in p or "запуск" in p or "run" in p:
            return [
                "✅ Успешный запуск (Success)",  # Target |00>
                "⚠️ Незначительные баги (Warn)",
                "❌ Ошибка компиляции (Error)",
                "💀 Критический сбой (Crash)",
            ]
        elif "риск" in p or "risk" in p:
            return [
                "🟢 Минимальный риск",  # Target |00>
                "🟡 Умеренный риск",
                "🟠 Высокий риск",
                "🔴 Неприемлемый риск",
            ]
        else:
            return [
                "✨ Оптимистичный исход",  # Target |00>
                "⚖️ Нейтральный исход",
                "🌧 Пессимистичный исход",
                "🌀 Хаотичный исход",
            ]
