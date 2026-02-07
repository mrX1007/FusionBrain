import logging
import time
import uuid
from typing import Any, Union

from fusionbrain.core.knowledge import KnowledgeBase
from fusionbrain.core.memory import Memory
from fusionbrain.experts.code_expert import CodeExpert
from fusionbrain.experts.critic_expert import CriticExpert
from fusionbrain.experts.policy_sampler import PolicySampler
from fusionbrain.experts.reasoning_expert import ReasoningExpert
from fusionbrain.experts.research_expert import ResearchExpert
from fusionbrain.experts.web_expert import WebExpert
from fusionbrain.experts.world_model_expert import WorldModelExpert
from fusionbrain.meta.meta_learning import MetaLearning

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("FusionBrain")


class FusionBrain:
    CONTEXT_LIMIT = 4000
    CRITIQUE_LIMIT = 2000

    def __init__(self):
        self.session_id = str(uuid.uuid4())

        logger.info(f"🤖 Booting FusionBrain v7.1 - Session: {self.session_id}")

        self.memory = Memory()
        self.knowledge = KnowledgeBase()
        self.meta_learner = MetaLearning(self.memory)

        self.router = PolicySampler()
        self.world = WorldModelExpert()
        self.critic = CriticExpert()

        self.web_expert = WebExpert()
        self.code_expert = CodeExpert()
        self.research_expert = ResearchExpert(brain_ref=self)
        self.reasoning_expert = ReasoningExpert(brain_ref=self)

        self.experts_map: dict[str, Any] = {
            "CodeExpert": self.code_expert,
            "ResearchExpert": self.research_expert,
            "ReasoningExpert": self.reasoning_expert,
        }

        self.default_expert = self.reasoning_expert

        print(f"[FusionBrain] Session started: {self.session_id}")
        print("[FusionBrain] Pipeline Mode: Robust Agent")

    def think(self, user_prompt: str) -> str:
        start_time = time.time()

        self.memory.store_user(user_prompt)

        plan = self.router.classify_intent(user_prompt)

        intent = plan.get("intent", "CHAT")
        target_expert_name = plan.get("expert", "ReasoningExpert")
        difficulty = plan.get("difficulty", 1)

        print(f"🧭 Route: [{intent}] -> {target_expert_name} ({difficulty}/10)")

        retrieved = self.knowledge.retrieve(user_prompt, n_results=2)
        retrieved_str = str(retrieved)

        lessons_context = ""
        if "[LESSON]" in retrieved_str:
            lessons_context = (
                "\nCRITICAL MEMORY:\n"
                f"{retrieved_str[:self.CONTEXT_LIMIT]}\n"
                "Avoid repeating this."
            )

        prompt_for_expert = (user_prompt + lessons_context)[-self.CONTEXT_LIMIT :]

        context: dict[str, Any] = {
            "prompt": prompt_for_expert,
            "memory": self.memory.recent(3),
            "knowledge": retrieved_str[: self.CONTEXT_LIMIT],
            "prev_output": "",
        }

        final_response = ""

        max_retries = 2 if difficulty > 4 else 1
        expert = self.experts_map.get(target_expert_name, self.default_expert)

        for attempt in range(max_retries):
            if attempt > 0:
                critique = context.get("critique", "")
                critique = critique[: self.CRITIQUE_LIMIT]

                context["prompt"] = (
                    f"ORIGINAL TASK:\n{user_prompt}\n\n"
                    f"CRITIC FEEDBACK:\n{critique}\n\n"
                    "Fix errors."
                )

            result = expert.run(context)

            if intent in {"CODING", "REASONING"} and difficulty >= 4:
                context["prev_output"] = result
                critique = self.critic.run(context)

                passed = "[VERDICT]: PASS" in critique or "✅" in critique

                if passed:
                    final_response = result
                    break

                context["critique"] = critique
                final_response = result if attempt == max_retries - 1 else ""

            else:
                final_response = result
                break

        self.meta_learner.track(target_expert_name, final_response)
        stats = self.meta_learner.evaluate_episode(user_prompt, final_response)

        if stats.get("lesson"):
            self.knowledge.add(
                f"[LESSON] {stats['lesson']}",
                category="meta",
                tags=["auto"],
            )

        self.memory.store_assistant(final_response)
        self.memory.save_episode(user_prompt, final_response, success=stats["reward"] > 0)

        elapsed = time.time() - start_time
        print(f"✅ Done in {elapsed:.2f}s | Reward {stats['reward']:.2f}")

        return final_response

    def repl(self):
        print("\n=== FusionBrain ===\n")

        while True:
            try:
                user = input("👤 ")

                if user.lower() in {"exit", "quit"}:
                    break

                if not user.strip():
                    continue

                print("\n🤖")
                response = self.think(user)
                print(response)

            except KeyboardInterrupt:
                break

            except Exception as e:
                logger.error("Crash", exc_info=True)
                print(e)


if __name__ == "__main__":
    brain = FusionBrain()
    brain.repl()
