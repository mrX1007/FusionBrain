import time
import uuid
from enum import Enum


class GoalStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class Goal:
    def __init__(self, description: str, priority: int = 1, parent_id: str = None):
        self.id = str(uuid.uuid4())
        self.description = description
        self.priority = priority  # 1 (low) to 5 (high)
        self.status = GoalStatus.ACTIVE.value
        self.created_at = time.time()
        self.completed_at = None
        self.parent_id = parent_id
        self.subgoals = []

    def complete(self):
        self.status = GoalStatus.COMPLETED.value
        self.completed_at = time.time()

    def fail(self):
        self.status = GoalStatus.FAILED.value

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "parent_id": self.parent_id,
            "subgoals": self.subgoals,
        }


class GoalManager:
    """
    Управление целями агента.
    Позволяет создавать дерево задач, отслеживать прогресс и приоритизировать действия.
    """

    def __init__(self):
        self.goals: dict[str, Goal] = {}

    def add_goal(self, description: str, priority: int = 1, parent_id: str = None) -> str:
        goal = Goal(description, priority, parent_id)
        self.goals[goal.id] = goal
        if parent_id and parent_id in self.goals:
            self.goals[parent_id].subgoals.append(goal.id)

        return goal.id

    def complete_goal(self, goal_id: str):
        if goal_id in self.goals:
            self.goals[goal_id].complete()

    def get_goal(self, goal_id: str) -> Goal | None:
        return self.goals.get(goal_id)

    def current(self) -> list[dict]:
        """Возвращает список только активных целей, отсортированных по приоритету."""
        active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE.value]
        active_goals.sort(key=lambda x: (x.priority, x.created_at), reverse=True)

        return [g.to_dict() for g in active_goals]

    def clear_completed(self):
        """Очистка памяти от завершенных задач"""
        self.goals = {k: v for k, v in self.goals.items() if v.status != GoalStatus.COMPLETED.value}

    def dump(self):
        return [g.to_dict() for g in self.goals.values()]
