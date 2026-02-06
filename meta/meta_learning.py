import json
import logging
import os
import time
from typing import Any

from fusionbrain.experts.base_expert import BaseExpert

logger = logging.getLogger(__name__)


class MetaLearning(BaseExpert):
    """
    Модуль мета-обучения (Reflexion + Reputation).
    """

    def __init__(self, storage_path="meta_weights.json"):
        super().__init__(
            name="MetaLearning",
            description="Analyzes feedback and adjusts system behavior.",
            version="3.0-Hybrid",
            model_name="llama3.1",
        )

        self.storage_path = storage_path
        self.learning_rate = 0.05
        self.min_weight = 0.1
        self.max_weight = 2.0
        self.weights = {
            "WebExpert": 1.0,
            "ReasoningExpert": 1.2,
            "CodeExpert": 1.0,
            "QuantumExpert": 1.0,
            "CriticExpert": 1.3,
        }

        self.stats = {"total_cycles": 0, "successful_cycles": 0, "lessons_learned": 0}

        self.load()

    def _perform_task(self, context: dict[str, Any]) -> str:
        """
        Мета-модуль обычно работает в фоне, но если его вызвать напрямую,
        он вернет текущую статистику обучения.
        """
        return (
            f"Meta Status: Active\n"
            f"Cycles: {self.stats['total_cycles']}\n"
            f"Lessons Learned: {self.stats['lessons_learned']}\n"
            f"Current Weights: {json.dumps(self.weights, indent=2)}"
        )

    def get_weights(self) -> dict[str, float]:
        return self.weights

    def evaluate(
        self, prompt: str, merged_response: str, expert_outputs: list[dict]
    ) -> dict[str, Any]:
        """Оценивает качество цикла."""
        merged_words = set(merged_response.lower().split())
        best_expert = None
        max_overlap = 0

        for item in expert_outputs:
            if item["expert"] == "MetaLearning":
                continue

            content = str(item["output"]).lower()
            content_words = set(content.split())
            if not content_words:
                continue

            intersection = merged_words.intersection(content_words)
            overlap = len(intersection) / len(content_words)

            if overlap > max_overlap:
                max_overlap = overlap
                best_expert = item["expert"]

        confidence = 0.5 + (max_overlap * 0.4)

        critic_output = ""
        for item in expert_outputs:
            if item["expert"] == "CriticExpert":
                critic_output = item["output"]
                break

        bad_signals = [
            "ошибка",
            "error",
            "risk",
            "риск",
            "неверно",
            "incorrect",
            "vulnerability",
            "security warning",
        ]
        is_bad = (
            any(signal in critic_output.lower() for signal in bad_signals)
            if critic_output
            else False
        )

        if is_bad:
            confidence = 0.3

        return {
            "confidence": min(0.99, confidence),
            "best_expert": best_expert,
            "score": confidence,
            "needs_improvement": is_bad,
            "critic_feedback": critic_output,
        }

    def learn(
        self, prompt: str, final_response: str, critique: dict[str, Any], knowledge_base=None
    ):
        """Главный метод обучения (Веса + Уроки)."""
        self.stats["total_cycles"] += 1

        quality_score = critique.get("score", 0.5)
        best_expert = critique.get("best_expert")

        if quality_score > 0.7:
            self.stats["successful_cycles"] += 1
            if best_expert and best_expert in self.weights:
                self._adjust_weight(best_expert, 1, quality_score)

        elif quality_score < 0.4:
            if best_expert and best_expert in self.weights:
                self._adjust_weight(best_expert, -1, quality_score)

        if critique.get("needs_improvement") and knowledge_base:
            self._reflexion_loop(
                prompt, final_response, critique.get("critic_feedback", ""), knowledge_base
            )

        if self.stats["total_cycles"] % 5 == 0:
            self.save()

    def _reflexion_loop(self, prompt: str, bad_response: str, feedback: str, knowledge_base):
        print("\n[Meta] 🧠 Reflexion triggered! Analyzing failure...")

        system_prompt = (
            "Ты — аналитик ошибок ИИ. "
            "Сформулируй ОДНО универсальное правило (Урок), которое поможет избежать этой ошибки в будущем. "
            "Правило должно начинаться со слов 'НЕЛЬЗЯ' или 'ВСЕГДА'."
        )

        user_content = (
            f"ЗАДАЧА: {prompt}\nОШИБКА: {bad_response}\nКРИТИКА: {feedback}\n\nСформулируй урок:"
        )

        lesson = self._ask_model(user_content, system_prompt=system_prompt)
        lesson = lesson.strip().replace('"', "")

        knowledge_base.add(
            content=f"[LESSON] {lesson}",
            category="mistake_pattern",
            tags=["self_improvement", "reflexion_rule"],
        )

        self.stats["lessons_learned"] += 1
        print(f"[Meta] 🎓 New Lesson Learned & Saved: '{lesson}'")

    def _adjust_weight(self, expert_name: str, direction: int, quality: float):
        current = self.weights.get(expert_name, 1.0)
        delta = direction * self.learning_rate * abs(quality - 0.5) * 2
        new_weight = max(self.min_weight, min(self.max_weight, current + delta))
        self.weights[expert_name] = round(new_weight, 4)

    def save(self):
        data = {"weights": self.weights, "stats": self.stats, "timestamp": time.time()}
        try:
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Meta save failed: {e}")

    def load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path) as f:
                data = json.load(f)
                self.weights = data.get("weights", self.weights)
                self.stats = data.get("stats", self.stats)
        except Exception as e:
            logger.error(f"Meta load failed: {e}")
