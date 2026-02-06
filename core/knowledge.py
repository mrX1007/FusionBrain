import logging
import time
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("⚠️ RAG libraries (chromadb, sentence-transformers) not found.")
    logger.warning("   Please run: pip install chromadb sentence-transformers")
    logger.warning("   Falling back to dummy memory mode.")


class KnowledgeBase:
    """
    Продвинутая Векторная Память (RAG).

    Использует:
    1. SentenceTransformer: Превращает текст в векторы (числа).
    2. ChromaDB: Хранит эти векторы и позволяет искать по смыслу.
    """

    def __init__(self, db_path="fusion_knowledge_db"):
        self.db_path = db_path
        self.collection = None
        self.encoder = None

        if RAG_AVAILABLE:
            self._init_vector_db()

    def _init_vector_db(self):
        """Инициализация базы данных и нейросети для эмбеддингов."""
        try:
            logger.info("[Knowledge] Loading Embedding Model (all-MiniLM-L6-v2)...")

            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

            logger.info("[Knowledge] Connecting to ChromaDB...")

            self.client = chromadb.PersistentClient(path=self.db_path)

            self.collection = self.client.get_or_create_collection(name="brain_memory")

            count = self.collection.count()
            logger.info(f"[Knowledge] System Ready. Memories stored: {count}")

        except Exception as e:
            logger.error(f"[Knowledge] Critical Init Error: {e}")

    def add(
        self, content: str, category: str = "general", tags: list[str] = None, source: str = "user"
    ) -> str | None:
        """
        Сохраняет факт в векторную базу.
        """
        if not RAG_AVAILABLE or not self.collection:
            return None

        try:
            if tags is None:
                tags = []
            tags_str = ",".join(tags)

            metadata = {
                "category": category,
                "tags": tags_str,
                "source": source,
                "timestamp": str(time.time()),
            }

            doc_id = str(uuid.uuid4())

            embedding = self.encoder.encode(content).tolist()

            self.collection.add(
                documents=[content], embeddings=[embedding], metadatas=[metadata], ids=[doc_id]
            )

            logger.info(f"[Knowledge] + Memorized: '{content[:40]}...'")
            return doc_id

        except Exception as e:
            logger.error(f"[Knowledge] Add Error: {e}")
            return None

    def retrieve(self, query: str, n_results: int = 3) -> str:
        """
        Семантический поиск: находит информацию, подходящую по СМЫСЛУ к запросу.
        Возвращает отформатированную строку для вставки в промпт LLM.
        """
        if not RAG_AVAILABLE or not self.collection:
            return ""

        if self.collection.count() == 0:
            return ""

        try:
            query_embedding = self.encoder.encode(query).tolist()

            results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

            found_docs = results["documents"][0]
            found_meta = results["metadatas"][0]

            if not found_docs:
                return ""

            context_parts = []
            for i, doc in enumerate(found_docs):
                meta = found_meta[i]
                timestamp = meta.get("timestamp", "unknown")

                context_parts.append(f"- [Fact]: {doc}")

            return "Relevant Long-Term Memory:\n" + "\n".join(context_parts)

        except Exception as e:
            logger.error(f"[Knowledge] Retrieve Error: {e}")
            return ""

    def save(self):
        pass
