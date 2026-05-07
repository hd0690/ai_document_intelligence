"""Document retrieval from vector store."""

from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
# from llama_index.embeddings.ollama import OllamaEmbedding

from config import settings
from ingestion.embedder import get_embedding_model
from retrieval.vector_store import VectorStoreManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentRetriever:
    """Retrieves relevant documents from the vector store."""

    def __init__(self):
        """Initialize the document retriever."""
        self.vector_store_manager = VectorStoreManager()
        self.vector_store = self.vector_store_manager.vector_store
        self.embedding_model = get_embedding_model()

        logger.info("DocumentRetriever initialized")

    def retrieve(self, query: str, k: int | None = None) -> list[str]:
        """
        Retrieve top-k most relevant documents for a query.

        Args:
            query: User's query string
            k: Number of documents to retrieve (uses settings.top_k_retrieval if None)

        Returns:
            List of retrieved document chunks
        """
        if k is None:
            k = settings.top_k_retrieval

        logger.info(f"Retrieving top {k} documents for query: {query}")

        try:
            # Load existing index from vector store — from_vector_store() does not require nodes
            index = VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model=self.embedding_model
            )
            retriever = VectorIndexRetriever(index, similarity_top_k=k)

            # Retrieve nodes
            nodes = retriever.retrieve(query)

            # Extract text from nodes
            retrieved_texts = [node.get_content() for node in nodes]

            logger.info(f"Retrieved {len(retrieved_texts)} documents")
            for i, text in enumerate(retrieved_texts, 1):
                preview = text[:100].replace("\n", " ") + "..."
                logger.debug(f"[{i}] {preview}")

            return retrieved_texts

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise

    def retrieve_with_scores(
        self, query: str, k: int | None = None
    ) -> list[tuple[str, float]]:
        """
        Retrieve top-k documents with similarity scores.

        Args:
            query: User's query string
            k: Number of documents to retrieve

        Returns:
            List of tuples (document_text, similarity_score)
        """
        if k is None:
            k = settings.top_k_retrieval

        logger.info(f"Retrieving top {k} documents with scores for query: {query}")

        try:
            index = VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model=self.embedding_model
            )
            retriever = VectorIndexRetriever(index, similarity_top_k=k)

            nodes = retriever.retrieve(query)

            # Extract text and scores
            results = [
                (node.get_content(), node.score if hasattr(node, "score") else 0.0)
                for node in nodes
            ]

            logger.info(f"Retrieved {len(results)} documents with scores")

            return results

        except Exception as e:
            logger.error(f"Error retrieving documents with scores: {e}")
            raise
