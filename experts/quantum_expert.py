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

from .base_expert import BaseExpert

logger = logging.getLogger(__name__)


class QuantumExpert(BaseExpert):
    """
    Advanced Quantum Expert (Hybrid Engine).

    Capabilities:
    1. Right Brain: Quantum Intuition & Creativity (Entropy Measurement).
    2. Left Brain: Grover's Search Algorithm (Decision Making).
    3. Simulation: Quantum Entanglement (World Modeling).
    """

    def __init__(self):
        super().__init__(
            name="QuantumExpert",
            description="Hybrid Quantum Engine: Generates Intuition (Entropy) and Solves Decisions (Grover).",
            version="4.0-Ultimate",
            model_name="qwen2.5-coder:7b",
        )
        self.shots = 1024

        if QISKIT_AVAILABLE:
            self.backend = AerSimulator()
            logger.info("[QuantumExpert] Qiskit Aer backend initialized.")
        else:
            self.backend = None
            logger.warning("[QuantumExpert] Qiskit not found. Using mock simulation.")

    def run(self, context: dict[str, Any]) -> str:
        """
        Главная точка входа.
        Этап 1: Оценка креативности (Интуиция).
        Этап 2: Если нужна логика — запуск Гровера (Решение задач).
        """
        prompt = context.get("prompt", "")

        intuition = self._generate_intuition()

        output = [
            "### ⚛️ QUANTUM CORE REPORT",
            f"State: |00>={intuition['zeros']} | |11>={intuition['ones']}",
            f"Entropy (Creativity): {intuition['score']}/1.0",
            f"MODE: **{intuition['mode']}**",
            f"Advice: {intuition['advice']}",
            "-" * 40,
        ]

        should_run_solver = intuition["mode"] != "CHAOS_MODE" or any(
            w in prompt.lower() for w in ["выбери", "choose", "solve", "реши", "анализ"]
        )

        if should_run_solver:
            scenarios = self._generate_scenarios(prompt)
            solver_result = self._run_grover_solver(scenarios)
            output.append(solver_result)

        return "\n".join(output)

    def _generate_intuition(self) -> dict[str, Any]:
        """Генерирует энтропию через запутанные кубиты (Bell State)."""
        zeros, ones = 50, 50  # Default

        if QISKIT_AVAILABLE and self.backend:
            try:
                qc = QuantumCircuit(2)
                qc.h(0)
                qc.cx(0, 1)
                qc.measure_all()
                circ = transpile(qc, self.backend)

                counts = self.backend.run(circ, shots=100).result().get_counts()
                zeros = counts.get("00", 0)
                ones = counts.get("11", 0)
            except Exception as e:
                logger.error(f"Intuition gen failed: {e}")

        balance = min(zeros, ones) / (max(zeros, ones) + 1)

        score = round(balance + 0.2 + (random.random() * 0.1), 2)
        if score > 1.0:
            score = 1.0

        if score < 0.4:
            mode = "LOGIC_MODE"
            advice = "Strict adherence to facts."
        elif score < 0.7:
            mode = "BALANCED_MODE"
            advice = "Mix logic with new ideas."
        else:
            mode = "CHAOS_MODE"
            advice = "Think outside the box. Ignore rules."

        return {"score": score, "mode": mode, "advice": advice, "zeros": zeros, "ones": ones}

    def _run_grover_solver(self, scenarios: list[str]) -> str:
        """Запускает алгоритм Гровера и рисует ASCII-график (как в старой версии)."""
        if QISKIT_AVAILABLE and self.backend:
            probs = self._run_quantum_circuit_grover(scenarios)
            method = "IBM Qiskit (Grover)"
        else:
            probs = self._run_mock_simulation(scenarios)
            method = "Pseudo-Random (Mock)"

        best_outcome = max(probs, key=probs.get)

        report = [
            f"\n🔎 DECISION MATRIX ({method})",
            f"Candidates: {len(scenarios)}",
        ]

        sorted_res = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        for outcome, probability in sorted_res:
            bar_len = int(probability * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            report.append(f"{outcome:<25} |{bar}| {probability * 100:.1f}%")

        report.append(f"\n✅ COLLAPSED STATE: {best_outcome}")
        return "\n".join(report)

    def simulate_world_scenario(self, agents: list[str], actions: str) -> str:
        """
        Симуляция мира через запутанность (для WorldModelExpert).
        """
        if not QISKIT_AVAILABLE or not self.backend:
            return "Simulation skipped (No Qiskit)."

        num_qubits = 4
        qc = QuantumCircuit(num_qubits, num_qubits)
        qc.h(0)
        qc.rx(math.pi / 3, 1)

        is_risky = any(w in actions.lower() for w in ["risk", "риск", "all-in"])
        if is_risky:
            qc.x(2)
        else:
            qc.h(2)

        qc.cx(0, 1)  # Entanglement
        qc.ccx(1, 2, 3)  # Toffoli
        qc.ry(math.pi / 4, 3)
        qc.measure(range(num_qubits), range(num_qubits))

        try:
            circ = transpile(qc, self.backend)
            result = self.backend.run(circ, shots=self.shots).result()
            counts = result.get_counts()
        except Exception as e:
            return f"Sim Failed: {e}"

        success_count = sum(c for s, c in counts.items() if s.startswith("0"))
        total = sum(counts.values())
        prob = (success_count / total) * 100

        outcome = "STABLE" if prob > 70 else "CHAOS" if prob < 40 else "UNCERTAIN"

        return (
            f"Quantum Sim ({self.shots} universes):\n"
            f"- Action: {actions}\n"
            f"- Probability of Success: {prob:.1f}%\n"
            f"- Verdict: {outcome}"
        )

    def _run_quantum_circuit_grover(self, scenarios: list[str]) -> dict[str, float]:
        """Реализация алгоритма Гровера (2 кубита)."""
        n_scenarios = len(scenarios)

        if n_scenarios != 4:
            return self._run_superposition_only(scenarios)

        qc = QuantumCircuit(2)
        qc.h([0, 1])

        qc.cz(0, 1)

        # Diffuser (Amplification)
        qc.h([0, 1])
        qc.x([0, 1])
        qc.cz(0, 1)
        qc.x([0, 1])
        qc.h([0, 1])

        qc.measure_all()

        circ = transpile(qc, self.backend)
        counts = self.backend.run(circ, shots=self.shots).result().get_counts()

        probs = {s: 0.0 for s in scenarios}

        mapping = {"00": 0, "01": 1, "10": 2, "11": 3}

        for k, v in counts.items():
            clean = k.replace(" ", "")
            idx = mapping.get(clean)
            if idx is not None and idx < len(scenarios):
                probs[scenarios[idx]] = v / self.shots

        return probs

    def _run_superposition_only(self, scenarios: list[str]) -> dict[str, float]:
        """Фолбэк: Простая суперпозиция, если сценариев не 4."""
        n = math.ceil(math.log2(len(scenarios)))
        qc = QuantumCircuit(n)
        for i in range(n):
            qc.h(i)
        qc.measure_all()

        circ = transpile(qc, self.backend)
        counts = self.backend.run(circ, shots=self.shots).result().get_counts()

        probs = {s: 0.0 for s in scenarios}
        sorted_c = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for i, (k, v) in enumerate(sorted_c):
            if i < len(scenarios):
                probs[scenarios[i]] = v / self.shots
        return probs

    def _run_mock_simulation(self, scenarios: list[str]) -> dict[str, float]:
        """Для тех, у кого нет Qiskit."""
        res = random.choices(scenarios, k=self.shots)
        counts = {s: res.count(s) for s in scenarios}
        return {k: v / self.shots for k, v in counts.items()}

    def _generate_scenarios(self, prompt: str) -> list[str]:
        p = prompt.lower()
        if "risk" in p or "риск" in p:
            return ["Low Risk", "Medium Risk", "High Risk", "Critical Fail"]
        if "code" in p or "код" in p:
            return ["Clean Code", "Minor Bugs", "Spaghetti Code", "Not Working"]
        return [
            "Option A (Optimal)",
            "Option B (Standard)",
            "Option C (Creative)",
            "Option D (Bad)",
        ]
