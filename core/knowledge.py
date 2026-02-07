import hashlib
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("KnowledgeBase")

try:
    import chromadb
    from sentence_transformers import SentenceTransformer

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("Install: uv add chromadb sentence-transformers")


class KnowledgeBase:
    """
    Production Vector Knowledge Store (RAG)

    Features:
    - Semantic embeddings
    - Persistent ChromaDB
    - Deduplication
    - Metadata
    - Batch ingest
    - Safe fallback
    """

    def __init__(self, db_path: str = "./fusion_knowledge"):
        self.db_path = db_path
        self.encoder = None
        self.collection = None
        self.client = None

        if RAG_AVAILABLE:
            self._boot()

    # -------------------------------------------------

    def _boot(self) -> None:
        try:
            logger.info("[KB] Loading encoder...")
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

            logger.info("[KB] Connecting Chroma...")
            self.client = chromadb.PersistentClient(path=self.db_path)

            self.collection = self.client.get_or_create_collection(
                name="memory",
                metadata={"hnsw:space": "cosine"},
            )

            logger.info("[KB] Ready | Stored: %s", self.collection.count())

        except Exception as e:
            logger.error("[KB] Boot failed: %s", e)
            self.collection = None

    # -------------------------------------------------

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()

    # -------------------------------------------------

    def add(
        self, content: str, category: str = "general", tags: list[str] | None = None
    ) -> str | None:
        if not self.collection or not self.encoder:
            return None

        tags = tags or []

        doc_hash = self._hash(content)
        doc_id = f"{category}:{doc_hash}"

        try:
            exists = self.collection.get(ids=[doc_id])
            if exists and exists["ids"]:
                return doc_id

            embedding = self.encoder.encode(content).tolist()

            meta = {
                "category": category,
                "tags": ",".join(tags),
                "created": time.time(),
            }

            self.collection.add(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[meta],
            )

            logger.info("[KB] + %s", content[:40])

            return doc_id

        except Exception as e:
            logger.error("[KB] add(): %s", e)
            return None

    # -------------------------------------------------

    def add_batch(self, texts: list[str], category: str = "general") -> None:
        if not self.collection or not self.encoder:
            return

        ids: list[str] = []
        embeddings: list[list[float]] = []
        metadatas: list[dict] = []
        documents: list[str] = []

        for text in texts:
            h = self._hash(text)
            doc_id = f"{category}:{h}"

            try:
                exists = self.collection.get(ids=[doc_id])
                if exists and exists["ids"]:
                    continue

                ids.append(doc_id)
                embeddings.append(self.encoder.encode(text).tolist())
                documents.append(text)
                metadatas.append(
                    {
                        "category": category,
                        "created": time.time(),
                    }
                )

            except Exception:
                continue

        if not ids:
            return

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    # -------------------------------------------------

    def retrieve(self, query: str, top_k: int = 3) -> str:
        if not self.collection or not self.encoder or self.collection.count() == 0:
            return ""

        try:
            q_embed = self.encoder.encode(query).tolist()

            res = self.collection.query(
                query_embeddings=[q_embed],
                n_results=top_k,
            )

            docs = res["documents"][0]
            metas = res["metadatas"][0]
            dists = res["distances"][0]

            out: list[str] = []

            for i, doc in enumerate(docs):
                if dists[i] > 0.75:
                    continue

                cat = metas[i].get("category", "general").upper()
                out.append(f"[{cat}] {doc}")

            return "\n".join(out)

        except Exception as e:
            logger.error("[KB] retrieve(): %s", e)
            return ""

    # -------------------------------------------------

    def stats(self) -> dict:
        if not self.collection:
            return {}

        return {
            "count": self.collection.count(),
            "path": self.db_path,
        }

    # -------------------------------------------------

    def clear(self) -> None:
        if self.client:
            self.client.delete_collection("memory")
            self._boot()
