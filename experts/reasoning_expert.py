import logging
from typing import Any

from .base_expert import BaseExpert

logger = logging.getLogger(__name__)


class ReasoningExpert(BaseExpert):
    def __init__(self, brain_ref: Any):
        super().__init__(
            name="ReasoningExpert",
            description="Generates multiple reasoning paths (Tree of Thought).",
            version="2.1-DeepSeek",
            model_name="deepseek-r1:14b",
        )
        self.brain = brain_ref

    def run(self, context: dict[str, Any]) -> str:
        prompt = context.get("prompt", "")
        policy = context.get("policy", {"method": "cot"})

        if policy.get("method") == "tot":
            return self._tree_of_thought(prompt, policy)

        return self._chain_of_thought(prompt)

    # -----------------------------------------------------

    def _chain_of_thought(self, prompt: str) -> str:
        logger.info("Executing Chain-of-Thought...")
        response = self._ask_model(prompt, system_prompt="Think step-by-step.")
        return f"### Linear Reasoning (CoT)\n{response}"

    # -----------------------------------------------------

    def _tree_of_thought(self, prompt: str, policy: dict[str, Any]) -> str:
        branches = int(policy.get("branches", 3))
        logger.info("Executing Tree-of-Thought with %s branches...", branches)

        candidates: list[str] = []

        for i in range(branches):
            thought = self._ask_model(
                prompt,
                system_prompt=f"Generate distinct approach #{i+1}. Be concise.",
            )
            candidates.append(thought)

        best_thought = ""
        best_score = -1.0
        report: list[str] = []

        for i, thought in enumerate(candidates):
            score_str = self._ask_model(
                f"Evaluate from 0 to 10. Return ONLY number.\nSolution:\n{thought}",
                system_prompt="Strict verifier.",
            )

            try:
                score = float(score_str.strip())
            except ValueError:
                score = 5.0

            report.append(f"Branch {i+1} (Score {score}): {thought[:60]}")

            if score > best_score:
                best_score = score
                best_thought = thought

        return (
            f"### Tree of Thought (Winner: {best_score})\n"
            f"{best_thought}\n\n"
            f"Discarded:\n" + "\n".join(report)
        )
