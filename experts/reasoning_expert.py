import logging
import re
from typing import Any

from fusionbrain.experts.base_expert import BaseExpert
from fusionbrain.experts.quantum_expert import QuantumExpert

logger = logging.getLogger(__name__)


class ReasoningExpert(BaseExpert):
    """
    QUANTUM-ENHANCED REASONING (SCIENTIFIC GRADE + MEMORY AWARE).

    Отличия v4.1:
    1. Mental Models: Использование научных фреймворков.
    2. Full Memory Context: Видит и RAG (уроки), и Краткосрочную память (историю диалога).
    """

    def __init__(self):
        super().__init__(
            name="ReasoningExpert",
            description="Uses Mental Models & Quantum Selection for deep analysis.",
            version="4.1-Scientific-Memory",
            model_name="llama3.1",
        )
        self.quantum_core = QuantumExpert()

    def _perform_task(self, context: dict[str, Any]) -> str:
        prompt = context.get("prompt", "")
        rag_memory = context.get("knowledge", "")  # Долговременная (RAG + Lessons)
        chat_history = context.get("memory", [])  # Краткосрочная (Диалог)

        history_str = ""
        if isinstance(chat_history, list):
            for msg in chat_history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                history_str += f"[{role.upper()}]: {content}\n"

        if len(prompt.split()) < 3:
            return ""

        hypotheses_text = self._generate_hypotheses(prompt)
        hypotheses_list = self._parse_hypotheses(hypotheses_text)

        if len(hypotheses_list) != 4:
            hypotheses_list = [
                "Through the lens of Quantum Physics (State vs Matter)",
                "Through the lens of Information Theory (Bit continuity)",
                "Through the lens of Systems Engineering (Functional Identity)",
                "Through the lens of Philosophy (Ontology)",
            ]

        try:
            q_results = self.quantum_core._run_quantum_circuit(hypotheses_list)
            winner_hypothesis = max(q_results, key=q_results.get)
            winner_score = q_results[winner_hypothesis]
        except Exception:
            winner_hypothesis = hypotheses_list[0]
            winner_score = 0.25

        full_memory_context = (
            f"=== SHORT-TERM CHAT HISTORY (DIALOG) ===\n{history_str}\n\n"
            f"=== LONG-TERM KNOWLEDGE & LESSONS ===\n{rag_memory}"
        )

        thought_process = self._execute_reasoning(prompt, winner_hypothesis, full_memory_context)
        final_answer = self._synthesize(prompt, winner_hypothesis, thought_process)

        output = [
            "### ⚛️🧠 Quantum-Neuro Reasoning (Scientific Grade)",
            "",
            "#### 1. 🔭 Mental Models (The Multiverse):",
            *[f"- {h}" for h in hypotheses_list],
            "",
            "#### 2. ⚡ Selected Paradigm (Grover's Choice):",
            f"**Winner:** {winner_hypothesis} (Confidence: {winner_score * 100:.1f}%)",
            "",
            "#### 3. 🧬 Deep Analysis (Context-Aware):",
            f"{thought_process}",
            "",
            "#### 4. 🏛️ Conclusion:",
            f"{final_answer}",
        ]

        return "\n".join(output)

    def _generate_hypotheses(self, prompt: str) -> str:
        system = (
            "Ты — научный стратег. Твоя задача — декомпозировать проблему, используя 4 различных МЕНТАЛЬНЫХ МОДЕЛИ.\n"
            "Не предлагай банальные решения. Используй фреймворки:\n"
            "- First Principles (Первые принципы)\n"
            "- Information Theory (Теория информации)\n"
            "- Systems Thinking (Системное мышление)\n"
            "- Quantum Mechanics (Wave function, Entanglement).\n"
            "Формат: 1. [Название модели]: Суть... 2. ... 3. ... 4. ..."
        )
        return self._ask_model(f"Проблема для анализа: {prompt}", system_prompt=system)

    def _parse_hypotheses(self, text: str) -> list[str]:
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            cleaned = re.sub(r"^\d+[\.\)]\s*", "", line.strip())
            if cleaned and len(cleaned) > 5:
                clean_lines.append(cleaned)
        return clean_lines[:4]

    def _execute_reasoning(self, prompt: str, winner: str, memory: str) -> str:
        system = (
            "Ты — профессор с мировым именем. Тебе дали задачу, историю диалога и научный метод решения.\n"
            "ВАЖНО:\n"
            "1. Посмотри 'CHAT HISTORY' — там контекст беседы.\n"
            "2. Посмотри 'LONG-TERM KNOWLEDGE' — там прошлые уроки ([LESSON]).\n"
            "Твоя цель: Доказать истину через логику, физику и факты.\n"
            "Используй термины: 'Энтропия', 'Состояние системы', 'Эмерджентность', 'Непрерывность'.\n"
            "Рассуждай шаг за шагом."
        )
        user_input = (
            f"Вопрос: {prompt}\n"
            f"ПОЛНЫЙ КОНТЕКСТ ПАМЯТИ:\n{memory}\n"
            f"Выбранная Парадигма: {winner}\n\n"
            f"Начинай глубокий анализ:"
        )
        return self._ask_model(user_input, system_prompt=system)

    def _synthesize(self, prompt: str, winner: str, thoughts: str) -> str:
        system = (
            "Сформулируй финальный, научно обоснованный ответ. "
            "Он должен быть кратким, но глубоким. "
            "Структура: Тезис -> Доказательство -> Вывод."
        )
        return self._ask_model(f"Вопрос: {prompt}\nМысли: {thoughts}", system_prompt=system)
