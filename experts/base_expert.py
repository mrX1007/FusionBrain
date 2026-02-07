import logging
import subprocess
import time
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class BaseExpert:
    def __init__(self, name: str, description: str, version: str = "1.0", model_name: str = ""):
        self.name = name
        self.description = description
        self.version = version
        self.model_name = model_name

    def run(self, context: dict[str, Any]) -> str:
        """
        Главная точка входа.
        Обертка с логированием и обработкой ошибок.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Started processing request.")

        if not self._validate_context(context):
            return f"[{self.name}] Context invalid: 'prompt' missing."

        try:
            result = self._perform_task(context)

            elapsed = time.time() - start_time
            logger.info(f"[{self.name}] Finished in {elapsed:.4f}s.")
            return result

        except NotImplementedError:
            error_msg = f"[{self.name}] Critical: Expert logic not implemented."
            logger.error(error_msg)
            return error_msg

        except Exception as e:
            logger.error(f"[{self.name}] CRITICAL ERROR: {e}", exc_info=True)
            return f"[{self.name}] Error: {str(e)}"

    def _perform_task(self, context: dict[str, Any]) -> str:
        """
        Метод, который должны реализовать наследники, если они используют базовый run().
        Если наследник переопределяет run() (как ResearchExpert), этот метод можно не писать.
        """
        raise NotImplementedError(
            f"Expert {self.name} must implement _perform_task or override run()"
        )

    def _validate_context(self, context: dict[str, Any]) -> bool:
        """Проверка наличия промпта в контексте."""
        return isinstance(context, dict) and "prompt" in context

    def _ask_model(self, prompt: str, system_prompt: str = "") -> str:
        """
        Отправляет запрос в локальную LLM через Ollama (Subprocess).
        """
        if not self.model_name:
            return "[System] No model configured for this expert."

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\nUser: {prompt}"

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
                errors="replace",
            )

            stdout, stderr = proc.communicate(input=full_prompt)

            if proc.returncode != 0:
                logger.error(f"[{self.name}] Ollama Error: {stderr}")
                return f"Error from model: {stderr}"

            return stdout.strip()

        except FileNotFoundError:
            return "Error: Ollama not found. Please install Ollama CLI."
        except Exception as e:
            logger.error(f"[{self.name}] LLM Connection Error: {e}")
            return f"Error calling model: {e}"

    def get_info(self) -> dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "model": self.model_name,
        }
