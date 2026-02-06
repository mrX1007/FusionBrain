import logging
from typing import Any

from fusionbrain.experts.base_expert import BaseExpert

logger = logging.getLogger(__name__)

try:
    from duckduckgo_search import DDGS

    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False


class WebExpert(BaseExpert):
    """
    Эксперт по поиску в интернете.
    Использует DuckDuckGo для получения текстовых сниппетов и LLM для ответа.
    """

    def __init__(self):
        super().__init__(
            name="WebExpert",
            description="Searches the internet for real-time info (No API key required).",
            version="2.0-TextConfig",
            model_name="llama3.1",
        )

    def _perform_task(self, context: dict[str, Any]) -> str:
        prompt = context.get("prompt", "")

        if not DDG_AVAILABLE:
            return "⚠️ Ошибка: Библиотека duckduckgo_search не установлена. Выполните: pip install -U duckduckgo_search"

        search_data = self._search(prompt)

        if not search_data:
            return "WebSearch: По вашему запросу ничего актуального не найдено."
        system = (
            "Ты — умный поисковый аналитик. "
            "Я дам тебе сырые данные из поисковой выдачи (заголовки и содержание). "
            "Твоя задача — ответить на вопрос пользователя, опираясь ИСКЛЮЧИТЕЛЬНО на эти данные. "
            "Если в данных есть точные цифры (цены, даты) — назови их. "
            "В конце укажи использованные источники (URL)."
        )

        user_content = (
            f"ВОПРОС ПОЛЬЗОВАТЕЛЯ: {prompt}\n\n"
            f"=== РЕЗУЛЬТАТЫ ПОИСКА (RAW DATA) ===\n"
            f"{search_data}\n"
            f"====================================\n"
            f"Сформируй четкий и краткий ответ."
        )

        summary = self._ask_model(user_content, system_prompt=system)

        return f"### 🌍 Web Knowledge\n{summary}"

    def _search(self, query: str, max_results=4) -> str:
        """
        Запрос к DuckDuckGo. Возвращает отформатированный текст с содержанием сайтов.
        """
        results_text = ""
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results, backend="api")

                if not results:
                    return ""

                for i, r in enumerate(results):
                    title = r.get("title", "Без заголовка")
                    body = r.get("body", "Нет описания")
                    href = r.get("href", "#")

                    results_text += f"SOURCE #{i + 1}\n"
                    results_text += f"Title: {title}\n"
                    results_text += f"Content: {body}\n"
                    results_text += f"URL: {href}\n\n"

        except Exception as e:
            logger.error(f"DuckDuckGo error: {e}")
            return f"Error during search: {str(e)}"

        return results_text
