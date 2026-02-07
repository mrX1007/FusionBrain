import uuid

from fusionbrain.core.aggregator import Aggregator
from fusionbrain.core.goals import GoalManager
from fusionbrain.core.knowledge import KnowledgeBase
from fusionbrain.core.memory import Memory
from fusionbrain.core.self_state import SelfState
from fusionbrain.experts import (
    CodeExpert,
    CriticExpert,
    QuantumExpert,
    ReasoningExpert,
    ResearchExpert,
    WebExpert,
    WorldModelExpert,
)
from fusionbrain.meta.meta_learning import MetaLearning


class FusionBrain:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.memory = Memory()
        self.state = SelfState()
        self.knowledge = KnowledgeBase()
        self.goals = GoalManager()

        self.research_expert = ResearchExpert(self)

        self.experts = [
            WebExpert(),
            QuantumExpert(),
            ReasoningExpert(),
            WorldModelExpert(),
            CodeExpert(),
            CriticExpert(),
        ]

        self.aggregator = Aggregator()
        self.meta = MetaLearning()

        print(f"[FusionBrain] Session started: {self.session_id}")
        print("[FusionBrain] Pipeline Mode: ACTIVE (Quantum Intuition + Deep Reasoning)")

    def think(self, prompt: str) -> str:
        if prompt.strip().lower().startswith("/research"):
            topic = prompt.replace("/research", "").strip()
            if not topic:
                topic = "Latest Artificial Intelligence Architectures Github"
            return self.research_expert.run(topic)

        cycle_id = str(uuid.uuid4())
        self.memory.store_user(prompt)

        trigger_phrases = [
            "меня зовут",
            "я люблю",
            "мне нравится",
            "мой",
            "моя",
            "мое",
            "я работаю",
        ]
        if any(phrase in prompt.lower() for phrase in trigger_phrases):
            self.knowledge.add(prompt, category="user_fact", tags=["auto_learned"])

        base_context = {
            "prompt": prompt,
            "memory": self.memory.recent(),
            "state": self.state.snapshot(),
            "goals": self.goals.current(),
            "knowledge": self.knowledge.retrieve(prompt),
        }

        chain_of_thought = []
        expert_outputs_log = []

        print(f"\n[Brain] Starting Pipeline for: '{prompt[:50]}...'")

        for expert in self.experts:
            try:
                pipeline_context = base_context.copy()
                if chain_of_thought:
                    history_str = "\n\n".join(
                        [f"--- ОТЧЕТ {name} ---\n{out}" for name, out in chain_of_thought]
                    )

                    enhanced_prompt = (
                        f"ЗАДАЧА ПОЛЬЗОВАТЕЛЯ: {prompt}\n\n"
                        f"КОНТЕКСТ ПРЕДЫДУЩИХ ЭКСПЕРТОВ (Chain of Thought):\n{history_str}\n\n"
                        f"ТВОЯ ЗАДАЧА ({expert.name}): Используй контекст выше. Выполни свою часть работы."
                    )

                    if expert.name == "QuantumExpert":
                        enhanced_prompt += "\n\nРЕЖИМ: ГЕНЕРАЦИЯ ИДЕЙ. Используй суперпозицию для поиска нестандартных решений. Не ограничивай себя безопасностью на этом этапе."

                    pipeline_context["prompt"] = enhanced_prompt
                else:
                    pipeline_context["prompt"] = prompt

                print(f"  -> ⏳ {expert.name} is working...")
                result = expert.run(pipeline_context)

                if not result:
                    print(f"  -> ⏭️ {expert.name} skipped.")
                    continue

                chain_of_thought.append((expert.name, result))
                expert_outputs_log.append({"expert": expert.name, "output": result})
                print(f"  -> ✅ {expert.name} completed.")

            except Exception as e:
                print(f"[Brain] ❌ Pipeline Break at {expert.name}: {e}")
                expert_outputs_log.append({"expert": expert.name, "output": f"Error: {e}"})

        merged = self.aggregator.merge(
            prompt=prompt, expert_outputs=expert_outputs_log, state=self.state
        )

        critique = self.meta.evaluate(prompt, merged, expert_outputs_log)
        self.meta.learn(prompt, merged, critique, self.knowledge)
        final = self.aggregator.refine(merged, critique)

        self.memory.store_assistant(final)
        self.state.update({"last_cycle": cycle_id})

        return final

    def repl(self):
        print("\n=== FusionBrain AGI (Sequential Pipeline Core) ===")
        print("Modes available:")
        print("1. Standard Chat (Type anything)")
        print("2. Autonomous Research (Type '/research <topic>')")
        print("Type 'exit' to quit\n")

        while True:
            try:
                user = input(">> ")
                if user.lower() in ["exit", "quit"]:
                    break
                if not user.strip():
                    continue
                answer = self.think(user)
                print("\n" + "=" * 60 + "\n" + answer + "\n" + "=" * 60 + "\n")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nError: {e}")


if __name__ == "__main__":
    brain = FusionBrain()
    brain.repl()
