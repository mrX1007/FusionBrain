import json
import math
import threading
import time
import uuid
from collections import defaultdict, deque


class MemoryItem(dict):
    __slots__ = ()

    @property
    def age(self):
        return time.time() - self["ts"]

    @property
    def importance(self):
        return self.get("importance", 1.0)


class Memory:
    """
    Advanced cognitive memory system:

    - STM / MTM hybrid buffer
    - decay + importance
    - episodic recall
    - topic graph
    - semantic search hook
    - reinforcement boosting
    - consolidation
    - snapshot persistence
    - attention weighting
    - future vector db ready
    """

    def __init__(
        self,
        max_items=512,
        decay_half_life=1800,
        importance_boost=1.6,
        consolidation_interval=120,
    ):
        self.max_items = max_items
        self.decay_half_life = decay_half_life
        self.importance_boost = importance_boost
        self.consolidation_interval = consolidation_interval

        self.buffer = deque(maxlen=max_items)
        self.index = {}
        self.topics = defaultdict(set)
        self.stats = defaultdict(int)

        self.lock = threading.Lock()
        self._last_consolidation = time.time()

    # ---------------- internal ----------------

    def _decay(self, item: MemoryItem):
        return item.importance * math.exp(-item.age / self.decay_half_life)

    def _make_item(self, role, text, meta=None):
        return MemoryItem(
            {
                "id": str(uuid.uuid4()),
                "role": role,
                "content": text,
                "ts": time.time(),
                "importance": 1.0,
                "attention": 1.0,
                "meta": meta or {},
            }
        )

    def _register(self, item):
        with self.lock:
            self.buffer.append(item)
            self.index[item["id"]] = item

            topic = item["meta"].get("topic")
            if topic:
                self.topics[topic].add(item["id"])

            self.stats[item["role"]] += 1

    # ---------------- store ----------------

    def store(self, role, text, topic=None, importance=1.0, attention=1.0):
        item = self._make_item(role, text, {"topic": topic})
        item["importance"] = importance
        item["attention"] = attention
        self._register(item)

    def store_user(self, text, **kw):
        self.store("user", text, **kw)

    def store_assistant(self, text, **kw):
        self.store("assistant", text, **kw)

    def inject(self, role, text, meta=None, importance=1.0):
        item = self._make_item(role, text, meta)
        item["importance"] = importance
        self._register(item)

    # ---------------- retrieval ----------------

    def recent(self, n=10):
        return list(self.buffer)[-n:]

    def strongest(self, n=10):
        return sorted(
            self.buffer,
            key=lambda x: self._decay(x) * x.get("attention", 1),
            reverse=True,
        )[:n]

    def by_topic(self, topic):
        return [self.index[x] for x in self.topics.get(topic, [])]

    def search(self, keyword):
        k = keyword.lower()
        return [m for m in self.buffer if k in m["content"].lower()]

    # ---------------- reinforcement ----------------

    def reinforce(self, item_id, factor=None):
        if item_id in self.index:
            self.index[item_id]["importance"] *= factor or self.importance_boost

    def punish(self, item_id, factor=0.7):
        if item_id in self.index:
            self.index[item_id]["importance"] *= factor

    # ---------------- consolidation ----------------

    def consolidate(self):
        now = time.time()
        if now - self._last_consolidation < self.consolidation_interval:
            return

        survivors = deque(maxlen=self.max_items)

        for m in self.buffer:
            if self._decay(m) > 0.02:
                survivors.append(m)

        self.buffer = survivors
        self.index = {m["id"]: m for m in survivors}
        self._last_consolidation = now

    # ---------------- episodic ----------------

    def episode(self, seconds=300):
        t = time.time()
        return [m for m in self.buffer if t - m["ts"] < seconds]

    # ---------------- persistence ----------------

    def dump(self):
        return list(self.buffer)

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.dump(), f, indent=2)

    def load(self, path):
        with open(path) as f:
            data = json.load(f)

        self.buffer.clear()
        self.index.clear()
        self.topics.clear()

        for d in data[-self.max_items :]:
            item = MemoryItem(d)
            self.buffer.append(item)
            self.index[item["id"]] = item
            topic = item.get("meta", {}).get("topic")
            if topic:
                self.topics[topic].add(item["id"])

    # ---------------- summaries ----------------

    def summary(self, n=20):
        return "\n".join(f"{m['role']}: {m['content']}" for m in self.strongest(n))

    # ---------------- embeddings ----------------

    def embed_hook(self, fn):
        for m in self.buffer:
            m["embedding"] = fn(m["content"])

    def similarity(self, vec, top_k=5):
        scored = []
        for m in self.buffer:
            emb = m.get("embedding")
            if not emb:
                continue
            dot = sum(a * b for a, b in zip(vec, emb, strict=False))
            scored.append((dot, m))
        return [x[1] for x in sorted(scored, reverse=True)[:top_k]]

    # ---------------- introspection ----------------

    def diagnostics(self):
        return {
            "total": len(self.buffer),
            "topics": len(self.topics),
            "roles": dict(self.stats),
        }

    # ---------------- wipe ----------------

    def clear(self):
        self.buffer.clear()
        self.index.clear()
        self.topics.clear()
        self.stats.clear()
