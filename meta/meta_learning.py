import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class MetaLearning:
    """
    Advanced Meta-Learning System (RL-based).
    Tracks trajectories, calculates rewards, and learns from mistakes.
    """

    def __init__(self, memory_ref: Any):
        self.memory = memory_ref
        self.reward_buffer: list[float] = []
        self.trajectory: list[dict[str, Any]] = []
        self.stats: dict[str, float] = {"lessons_learned": 0.0, "total_reward": 0.0}

    # -----------------------------------------------------

    def track(self, expert_name: str, output: str) -> None:
        self.trajectory.append(
            {
                "expert": expert_name,
                "output": str(output)[:1000],
                "ts": time.time(),
            }
        )

    # -----------------------------------------------------

    def evaluate_episode(self, user_prompt: str, final_response: str) -> dict[str, Any]:
        reward = 0.0

        if final_response and len(final_response) > 20:
            reward += 0.2

        if "Sandbox Output" in final_response:
            if "Error" not in final_response and "Traceback" not in final_response:
                reward += 0.8
            else:
                reward -= 0.5

        if "Verifier Report" in final_response:
            if "No critical errors" in final_response or "Looks good" in final_response:
                reward += 0.3
            elif "Hallucination" in final_response or "Logic error" in final_response:
                reward -= 0.5

        self.reward_buffer.append(reward)
        self.stats["total_reward"] += reward

        lesson: str | None = None

        if reward < 0.0:
            lesson = self._formulate_lesson(user_prompt, final_response)
            self._store_lesson(lesson)
            self.stats["lessons_learned"] += 1.0
            logger.warning("Low reward %.2f → lesson learned", reward)
        else:
            logger.info("High reward %.2f", reward)

        self.trajectory.clear()

        return {
            "reward": reward,
            "lesson": lesson,
            "stats": self.stats,
        }

    # -----------------------------------------------------

    def _formulate_lesson(self, prompt: str, response: str) -> str:
        if "Sandbox Error" in response or "SyntaxError" in response:
            return f"Always validate Python syntax and imports. Context: {prompt[:40]}"

        if "No information found" in response or "Nothing relevant" in response:
            return f"Use broader search queries. Context: {prompt[:40]}"

        if "Hallucination" in response:
            return f"Do not invent APIs. Verify libraries. Context: {prompt[:40]}"

        if "Forbidden" in response or "Security Alert" in response:
            return "Never use dangerous system commands."

        return "Double-check reasoning logic before final answer."

    # -----------------------------------------------------

    def _store_lesson(self, lesson: str) -> None:
        if hasattr(self.memory, "store"):
            self.memory.store(
                role="system",
                text=f"[SELF-IMPROVE] {lesson}",
                topic="lesson",
                importance=3.0,
            )
