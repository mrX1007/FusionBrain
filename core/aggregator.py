import logging
import subprocess
from typing import Any

# Настраиваем логгер
logger = logging.getLogger(__name__)


class Aggregator:
    """
    Модуль принятия решений и синтеза ответа.
    Использует локальную LLM (Ollama) для объединения ответов экспертов.
    """

    def __init__(self):
        self.model_name = "llama3.1"

    def merge(self, prompt: str, expert_outputs: list[dict], state: Any) -> str:
        """
        Собирает ответы экспертов и формирует итоговый ответ через LLM.
        """
        inputs_text = ""
        for item in expert_outputs:
            if item.get("output"):
                inputs_text += f"\n--- Expert: {item['expert']} ---\n{item['output']}\n"

        if not inputs_text.strip():
            return "Я подумал, но эксперты не дали мне информации. Попробуйте переформулировать запрос."

        system_prompt = (
            "Ты — FusionBrain, единый AI-ассистент. "
            "Твоя задача — проанализировать ответы разных экспертов и сформировать "
            "ОДИН связный, полезный ответ для пользователя на русском языке. "
            "Не перечисляй экспертов (не говори 'как сказал CodeExpert'), просто дай решение. "
            "Если есть код, обязательно сохрани его форматирование."
        )

        user_prompt = (
            f"Запрос пользователя: {prompt}\n\n"
            f"ДАННЫЕ ОТ ЭКСПЕРТОВ:{inputs_text}\n\n"
            "Сформируй итоговый ответ:"
        )

        final_response = self._call_ollama(user_prompt, system_prompt)

        return final_response

    def refine(self, current_answer: str, critique: dict[str, Any]) -> str:
        """
        Позволяет улучшить ответ, если Критик недоволен.
        """
        score = critique.get("score", 1.0)
        feedback = critique.get("feedback", "")

        if score < 0.5 and feedback:
            logger.info(f"[Aggregator] Refining answer due to low score: {score}")
            prompt = (
                f"Вот ответ: \n{current_answer}\n\n"
                f"Критика: {feedback}\n\n"
                "Перепиши ответ, исправив недочеты."
            )
            return self._call_ollama(prompt, "Ты редактор. Улучши текст.")

        return current_answer

    def _call_ollama(self, prompt: str, system: str) -> str:
        """
        Внутренний метод для обращения к Ollama через консоль.
        Заменяет необходимость файла llm_engine.py.
        """
        full_prompt = f"System: {system}\nUser: {prompt}"

        cmd = ["ollama", "run", self.model_name]

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
            )

            stdout, stderr = proc.communicate(input=full_prompt)

            if proc.returncode != 0:
                logger.error(f"Ollama Error: {stderr}")
                return f"Произошла ошибка генерации: {stderr}"

            return stdout.strip()

        except FileNotFoundError:
            return "Ошибка: Ollama не установлена или недоступна в PATH."
        except Exception as e:
            logger.error(f"LLM Call Error: {e}")
            return f"Ошибка вызова нейросети: {e}"
