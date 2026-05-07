"""Vector store management using ChromaDB."""

from typing import Optional

from chromadb import Client
from chromadb.config import Settings as ChromaSettings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import TextNode
# from llama_index.embeddings.ollama import OllamaEmbedding

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    """Manages ChromaDB vector store operations."""

    def __init__(self):
        """Initialize ChromaDB client and vector store."""
        self.db_path = settings.chroma_db_path
        self.collection_name = settings.chroma_collection_name

        logger.info(f"Initializing ChromaDB at: {self.db_path}")

        # Initialize ChromaDB client
        chroma_settings = ChromaSettings(
            is_persistent=True,
            persist_directory=str(self.db_path),
            anonymized_telemetry=False,
        )
        self.chroma_client = Client(chroma_settings)

        # Initialize ChromaVectorStore
        self.vector_store = ChromaVectorStore(
            chroma_collection=self.chroma_client.get_or_create_collection(
                name=self.collection_name,
            )
        )

        logger.info(f"ChromaDB initialized with collection: {self.collection_name}")

    def add_documents(self, nodes: list[TextNode]) -> None:
        """
        Add documents/chunks to the vector store.

        Args:
            nodes: List of TextNode objects with embeddings
        """
        logger.info(f"Adding {len(nodes)} nodes to vector store...")

        try:
            # Create storage context with vector store
            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )

            # Create index and add nodes — explicitly use Ollama to avoid OpenAI fallback
            embed_model = OllamaEmbedding(
                model_name=settings.ollama_embedding_model,
                base_url=settings.ollama_base_url,
            )
            _ = VectorStoreIndex(nodes=nodes, storage_context=storage_context, embed_model=embed_model)

            logger.info(f"Successfully added {len(nodes)} nodes to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def get_collection_info(self) -> dict:
        """
        Get information about the current collection.

        Returns:
            Dictionary with collection information
        """
        collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )
        count = collection.count()

        logger.info(f"Collection '{self.collection_name}' has {count} documents")

        return {
            "name": self.collection_name,
            "count": count,
            "db_path": str(self.db_path),
        }

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self.vector_store = ChromaVectorStore(
                chroma_collection=self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                )
            )
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
