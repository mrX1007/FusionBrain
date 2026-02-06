import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IOUtils")


class IOUtils:
    """
    Утилиты для ввода-вывода (Input/Output).
    Обеспечивает безопасное сохранение и загрузку данных.
    """

    @staticmethod
    def ensure_dir(file_path: str):
        """Создает директорию для файла, если её нет."""
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
            except OSError as e:
                logger.error(f"Error creating directory {directory}: {e}")

    @staticmethod
    def save_json(path: str, data: dict | list, indent: int = 2):
        """Сохраняет данные в обычный JSON файл."""
        IOUtils.ensure_dir(path)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            logger.debug(f"Saved JSON to {path}")
        except Exception as e:
            logger.error(f"Failed to save JSON to {path}: {e}")

    @staticmethod
    def load_json(path: str, default: Any = None) -> Any:
        """Загружает JSON. Возвращает default, если файл не найден или битый."""
        if not os.path.exists(path):
            return default if default is not None else {}

        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Corrupted JSON file: {path}")
            return default if default is not None else {}
        except Exception as e:
            logger.error(f"Error loading JSON {path}: {e}")
            return default

    @staticmethod
    def append_jsonl(path: str, data: dict):
        """
        Добавляет одну запись в JSONL (JSON Lines) файл.
        Идеально для логов событий и истории чата.
        """
        IOUtils.ensure_dir(path)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to JSONL {path}: {e}")

    @staticmethod
    def load_jsonl(path: str) -> list[dict]:
        """Читает весь JSONL файл в список словарей."""
        if not os.path.exists(path):
            return []

        result = []
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        result.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading JSONL {path}: {e}")

        return result
