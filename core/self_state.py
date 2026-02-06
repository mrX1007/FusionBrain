import time
from typing import Any


class SelfState:
    """
    Модуль внутреннего состояния агента (SelfState).
    Эмулирует динамические когнитивные показатели:
    - Fatigue (Усталость): накапливается при работе, снижает фокус.
    - Stress (Стресс): растет при ошибках, влияет на рискованность решений.
    - Mood (Настроение): влияет на стиль ответа (творческий/сухой).
    - Confidence (Уверенность): базируется на успешности прошлых ответов.
    - Focus (Фокус/Внимание): определяет глубину анализа.
    """

    def __init__(self):
        self.fatigue: float = 0.0
        self.stress: float = 0.0
        self.mood: float = 0.5
        self.confidence: float = 0.5
        self.focus: float = 1.0

        self.last_update = time.time()

        self.decay_rate = 0.05

    def snapshot(self) -> dict[str, float]:
        """Возвращает текущий снимок состояния для передачи экспертам."""
        self._natural_decay()
        return {
            "fatigue": round(self.fatigue, 3),
            "stress": round(self.stress, 3),
            "mood": round(self.mood, 3),
            "confidence": round(self.confidence, 3),
            "focus": round(self.focus, 3),
            "timestamp": time.time(),
        }

    def update(self, metrics: dict[str, Any]):
        """
        Обновляет состояние на основе результатов цикла мышления.
        metrics: словарь, например {"success": True, "complexity": 0.8}
        """
        complexity = metrics.get("complexity", 0.1)
        success = metrics.get("success", True)
        confidence_score = metrics.get("confidence", 0.5)

        fatigue_increase = complexity * 0.1
        self.fatigue = min(1.0, self.fatigue + fatigue_increase)

        if success:
            self.confidence = min(1.0, self.confidence + 0.05)
            self.mood = min(1.0, self.mood + 0.05)
            self.stress = max(0.0, self.stress - 0.05)
        else:
            self.confidence = max(0.0, self.confidence - 0.1)
            self.mood = max(0.0, self.mood - 0.1)
            self.stress = min(1.0, self.stress + 0.1)

        if "confidence" in metrics:
            self.confidence = (self.confidence * 0.7) + (confidence_score * 0.3)

        self.focus = max(0.0, 1.0 - (self.fatigue * 0.8) - (self.stress * 0.2))

    def _natural_decay(self):
        """Эмуляция восстановления со временем (если агент простаивает)."""
        now = time.time()
        delta = now - self.last_update

        if delta > 10:
            recovery_steps = int(delta / 10)
            recovery_amount = recovery_steps * 0.02

            self.fatigue = max(0.0, self.fatigue - recovery_amount)
            self.stress = max(0.0, self.stress - recovery_amount)
            if self.mood > 0.5:
                self.mood = max(0.5, self.mood - recovery_amount)
            else:
                self.mood = min(0.5, self.mood + recovery_amount)

            self.last_update = now

    def get_cognitive_weights(self) -> dict[str, float]:
        """
        Возвращает модификаторы для экспертов.
        Например, при усталости CodeExpert получает меньше веса, а CriticExpert больше.
        """
        return {
            "creativity_penalty": self.fatigue * 0.5,
            "criticism_boost": self.stress * 0.3,
            "risk_tolerance": self.confidence * 0.8,
        }

    def __str__(self):
        return (
            f"State(Ftg:{self.fatigue:.2f}, Str:{self.stress:.2f}, "
            f"Moo:{self.mood:.2f}, Cnf:{self.confidence:.2f}, Foc:{self.focus:.2f})"
        )
