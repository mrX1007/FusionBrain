import ast
import importlib
import re
from typing import Any

from fusionbrain.experts.base_expert import BaseExpert


class CodeExpert(BaseExpert):
    def __init__(self):
        super().__init__(
            name="CodeExpert",
            description="Generates code and checks for non-existent functions (Hallucination check).",
            version="4.0-AntiHallucination",
            model_name="qwen2.5-coder:7b",
        )

    def _perform_task(self, context: dict[str, Any]) -> str:
        prompt = context.get("prompt", "")

        system = (
            "Ты — Python-разработчик. Пиши код. "
            "Используй ТОЛЬКО существующие библиотеки и функции. "
            "Не выдумывай методы. Оберни код в ```python```."
        )

        raw_response = self._ask_model(prompt, system_prompt=system)
        code_fragment = self._extract_code(raw_response)

        analysis = self._deep_analyze_code(code_fragment)

        result = [
            f"### 🤖 Code Expert (Model: {self.model_name})",
            raw_response,
            "",
            "--- 🔍 Deep Inspection ---",
            f"• Syntax: {'✅ Valid' if analysis['syntax_valid'] else '❌ Error'}",
            f"• Hallucinations: {'✅ None' if analysis['attributes_valid'] else '⚠️ DETECTED'}",
        ]

        if not analysis["syntax_valid"]:
            result.append(f"• Syntax Error: {analysis['error']}")

        if not analysis["attributes_valid"]:
            for err in analysis["attribute_errors"]:
                result.append(f"• 🤥 Hallucination: {err}")
                result.append("  (Model invented a function that does not exist!)")

        return "\n".join(result)

    def _extract_code(self, text: str) -> str:
        match = re.search(r"```python(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    def _deep_analyze_code(self, code: str) -> dict[str, Any]:
        """
        Проверяет и синтаксис, и существование модулей/функций.
        """
        result = {
            "syntax_valid": False,
            "attributes_valid": True,
            "error": None,
            "attribute_errors": [],
        }

        try:
            tree = ast.parse(code)
            result["syntax_valid"] = True
        except Exception as e:
            result["error"] = str(e)
            return result

        hallucinations = self._check_imports_and_calls(tree)
        if hallucinations:
            result["attributes_valid"] = False
            result["attribute_errors"] = hallucinations

        return result

    def _check_imports_and_calls(self, tree: ast.AST) -> list[str]:
        """
        Проходит по AST, находит импорты и проверяет, существуют ли вызовы.
        Пример: если код вызывает shutil.disk_format, мы проверяем hasattr(shutil, 'disk_format').
        """
        errors = []
        imported_modules = {}  # map: alias -> real_module_name

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    asname = alias.asname or alias.name
                    imported_modules[asname] = name
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                if module:
                    for alias in node.names:
                        asname = alias.asname or alias.name
                        imported_modules[asname] = f"{module}.{alias.name}"

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    var_name = node.value.id  #'shutil'
                    attr_name = node.attr  #'disk_format'

                    if var_name in imported_modules:
                        real_module_name = imported_modules[var_name]

                        try:
                            mod = importlib.import_module(real_module_name)
                            if not hasattr(mod, attr_name):
                                errors.append(
                                    f"Module '{real_module_name}' has no attribute '{attr_name}'"
                                )
                        except ImportError:
                            pass
                        except Exception:
                            pass

        return errors
