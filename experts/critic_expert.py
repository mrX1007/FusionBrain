import ast
import logging
import re
import subprocess
import sys
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any

from .base_expert import BaseExpert

logger = logging.getLogger(__name__)


class CriticExpert(BaseExpert):
    def __init__(self):
        super().__init__(
            name="CriticExpert",
            description="Executes Unit Tests to verify code logic (TDD).",
            version="3.2-SecureTDD",
            model_name="qwen2.5-coder:32b",
        )

        # запрещаем только опасное для генерируемого кода
        self.forbidden_imports = {
            "subprocess",
            "socket",
            "requests",
            "shutil",
        }

    # -----------------------------------------------------

    def run(self, context: dict[str, Any]) -> str:
        candidate_solution = context.get("prev_output", "")
        prompt = context.get("prompt", "")

        code_match = re.search(r"```python(.*?)```", candidate_solution, re.DOTALL)

        if not code_match:
            return self._text_critique(candidate_solution)

        original_code = code_match.group(1).strip()

        if not self._is_safe(original_code):
            return "❌ Security Block: forbidden imports detected."

        logger.info("Generating Unit Tests...")
        test_code = self._generate_test(prompt, original_code)

        full_suite = f"""
import unittest

{original_code}

# ---- GENERATED TESTS ----
{test_code}

if __name__ == "__main__":
    unittest.main(argv=["x"], exit=False)
"""

        output, exit_code = self._execute_sandbox(full_suite)

        if exit_code == 0 and "OK" in output:
            return "✅ Verification Passed\nAll tests succeeded."

        return f"❌ Verification Failed\n```\n{output}\n```"

    # -----------------------------------------------------

    def _generate_test(self, task_prompt: str, code: str) -> str:
        system = (
            "You are QA automation. Generate ONLY python unittest code. "
            "No markdown. No comments."
        )

        user = f"TASK:\n{task_prompt}\n\nCODE:\n{code}"

        resp = self._ask_model(user, system_prompt=system)
        return resp.replace("```python", "").replace("```", "").strip()

    # -----------------------------------------------------

    def _execute_sandbox(self, code: str) -> tuple[str, int]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = Path(tmp.name)

        try:
            result = subprocess.run(
                [sys.executable, str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return (result.stdout + result.stderr).strip(), result.returncode

        except subprocess.TimeoutExpired:
            return "Timeout exceeded", 1

        except Exception as e:
            return str(e), 1

        finally:
            with suppress(Exception):
                tmp_path.unlink(missing_ok=True)

    # -----------------------------------------------------

    def _text_critique(self, text: str) -> str:
        return self._ask_model(
            f"Critique this text:\n{text}",
            system_prompt="Be strict.",
        )

    # -----------------------------------------------------

    def _is_safe(self, code: str) -> bool:
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        if a.name.split(".")[0] in self.forbidden_imports:
                            return False

                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module.split(".")[0] in self.forbidden_imports:
                        return False

            return True

        except Exception as e:
            logger.warning(f"AST failure: {e}")
            return False
