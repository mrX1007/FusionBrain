import hashlib
import uuid


class HashUtils:
    """
    Утилиты для хэширования и генерации ID.
    """

    @staticmethod
    def generate_uuid() -> str:
        """Генерирует стандартный UUID4."""
        return str(uuid.uuid4())

    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """
        Генерирует короткий уникальный ID (удобно для логов).
        Пример: 'a1b2c3d4'
        """
        return uuid.uuid4().hex[:length]

    @staticmethod
    def compute_hash(text: str) -> str:
        """
        Возвращает SHA-256 хэш строки.
        Используется для создания уникальных ключей кэша для промптов.
        """
        if not text:
            return ""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def checksum(file_path: str) -> str | None:
        """Считает хэш файла (проверка целостности)."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(65536)
                    if not data:
                        break
                    sha256.update(data)
            return sha256.hexdigest()
        except FileNotFoundError:
            return None
