import ast
import logging
import os
import re
import subprocess
import sys
import tempfile
from typing import Any

from .base_expert import BaseExpert

logger = logging.getLogger(__name__)


class CodeExpert(BaseExpert):
    def __init__(self):
        super().__init__(
            name="CodeExpert",
            description="Generates AND Executes Python code in a sandbox.",
            version="3.0-Sandbox",
            model_name="qwen2.5-coder:32b",
        )

    def run(self, context: dict[str, Any]) -> str:
        """
        Основной метод запуска.
        1. Генерирует код.
        2. Если пользователь просит — выполняет его.
        """
        # Если промпт лежит внутри словаря (как в новом пайплайне)
        prompt = context.get("prompt", "") if isinstance(context, dict) else str(context)

        # 1. Генерация кода
        code = self._generate_code(prompt)

        # 2. Если пользователь просит выполнить — запускаем Sandbox
        if self._should_execute(prompt):
            execution_result = self._execute_sandbox(code)
            return (
                f"### 🐍 Code Generated & Executed\n"
                f"```python\n{code}\n```\n"
                f"**Sandbox Output:**\n"
                f"```text\n{execution_result}\n```"
            )

        return f"### 🐍 Code Generated (Dry Run)\n```python\n{code}\n```"

    def _perform_task(self, context: dict[str, Any]) -> str:
        # Для совместимости с BaseExpert.run
        return self.run(context)

    def _generate_code(self, prompt: str) -> str:
        system = (
            "Write pure Python code. No markdown, no explanations. Just code. "
            "Use standard libraries where possible."
        )
        response = self._ask_model(prompt, system_prompt=system)

        # Очистка от ```python ... ```
        clean_code = response.replace("```python", "").replace("```", "").strip()
        return clean_code

    def _should_execute(self, prompt: str) -> bool:
        """Определяет, нужно ли выполнять код."""
        triggers = ["выполни", "execute", "run", "запусти", "посчитай", "calculate", "test"]
        return any(w in prompt.lower() for w in triggers)

    def _execute_sandbox(self, code: str) -> str:
        """
        Безопасное выполнение кода через временный файл и subprocess.
        """
        logger.info("Spinning up Sandbox Container...")

        # Проверка на опасные команды перед запуском
        if self._is_dangerous(code):
            return "❌ Security Alert: Code contains forbidden commands (rm, system, etc)."

        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            # Запускаем в отдельном процессе с тайм-аутом 5 сек
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "❌ TimeoutError: Code execution took too long (>5s)."
        except Exception as e:
            output = f"❌ Sandbox Error: {e}"
        finally:
            # Удаляем улики
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return output.strip() or "[No Output]"

    def _is_dangerous(self, code: str) -> bool:
        """Простейшая стат. проверка на rm -rf и прочее."""
        forbidden = ["shutil.rmtree", "os.remove", "os.rmdir", "subprocess.call", "rm -rf"]
        return any(cmd in code for cmd in forbidden)
