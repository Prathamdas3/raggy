"""Qdrant vector database configuration.

Provides thread-safe singleton access to Qdrant client and vector store
for embedding and similarity search operations.
"""

import threading
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import config
from app.core.logger import get_logger

logger = get_logger(__name__)


class QdrantStore:
    """Thread-safe singleton for Qdrant vector store operations.

    Provides lazy initialization of Qdrant client, embeddings model,
    and vector store with automatic collection management.
    """

    _client: Optional[QdrantClient] = None
    _store: Optional[QdrantVectorStore] = None
    _embeddings: Optional[HuggingFaceEmbeddings] = None
    _lock = threading.RLock()

    @classmethod
    def _get_embeddings(cls) -> HuggingFaceEmbeddings:
        """Get or create HuggingFace embeddings model.

        Returns:
            Configured HuggingFaceEmbeddings instance.

        Raises:
            Exception: If embeddings initialization fails.
        """
        if cls._embeddings is None:
            with cls._lock:
                if cls._embeddings is None:
                    try:
                        cls._embeddings = HuggingFaceEmbeddings(
                            model_name=config.huggingface_model,
                            model_kwargs={"device": config.huggingface_device},
                            encode_kwargs={"normalize_embeddings": True},
                        )
                        logger.info(
                            f"Embeddings initialized: {config.huggingface_model}"
                        )
                    except Exception as e:
                        cls._embeddings = None
                        logger.error(f"Failed to initialize embeddings: {e}")
                        raise
        return cls._embeddings

    @classmethod
    def _get_client(cls) -> QdrantClient:
        """Get or create Qdrant client.

        Returns:
            Configured QdrantClient instance.

        Raises:
            RuntimeError: If client initialization fails.
        """
        if cls._client is None:
            with cls._lock:
                if cls._client is None:
                    try:
                        cls._client = QdrantClient(
                            url=config.qdrant_url, https=config.qdrant_use_https
                        )
                        cls._ensure_collection()
                        logger.info("Qdrant client initialized.")
                    except Exception as e:
                        cls._client = None
                        logger.error(f"Failed to initialize Qdrant client: {e}")
                        raise
        if cls._client is None:
            raise RuntimeError("Qdrant client could not be initialized.")
        return cls._client

    @classmethod
    def _ensure_collection(cls) -> None:
        """Ensure the configured collection exists, create if not.

        Creates the collection with cosine distance if it doesn't exist.

        Raises:
            RuntimeError: If client is not initialized.
        """
        if cls._client is None:
            raise RuntimeError("Client not initialized.")
        existing = [c.name for c in cls._client.get_collections().collections]
        if config.qdrant_collection_name not in existing:
            # get vector size from embeddings
            dim = len(cls._get_embeddings().embed_query("test"))
            cls._client.create_collection(
                collection_name=config.qdrant_collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
            logger.info(f"Collection '{config.qdrant_collection_name}' created.")
        else:
            logger.info(f"Collection '{config.qdrant_collection_name}' already exists.")

    @classmethod
    def get_store(cls) -> QdrantVectorStore:
        """Get or create QdrantVectorStore instance.

        Returns:
            Configured QdrantVectorStore instance.

        Raises:
            Exception: If store initialization fails.
        """
        if cls._store is None:
            with cls._lock:
                if cls._store is None:
                    try:
                        cls._store = QdrantVectorStore(
                            client=cls._get_client(),
                            collection_name=config.qdrant_collection_name,
                            embedding=cls._get_embeddings(),
                        )
                        logger.info("Qdrant vector store initialized.")
                    except Exception as e:
                        cls._store = None
                        logger.error(f"Failed to initialize Qdrant store: {e}")
                        raise
        return cls._store

    @classmethod
    def save(
        cls,
        texts: list[str],
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ):
        """Save texts to the vector store.

        Args:
            texts: List of text strings to embed and save.
            metadatas: Optional list of metadata dicts.
            ids: Optional list of custom IDs.

        Returns:
            List of saved point IDs.

        Raises:
            Exception: If save operation fails.
        """
        try:
            return cls.get_store().add_texts(texts=texts, metadatas=metadatas, ids=ids)
        except Exception as e:
            logger.error(f"Failed to save texts: {e}")
            raise

    @classmethod
    def reset(cls) -> None:
        """Reset all cached instances.

        Useful for testing or when configuration changes.
        """
        with cls._lock:
            cls._client = None
            cls._store = None
            cls._embeddings = None
            logger.warning("Qdrant store reset.")


qdrant_store = QdrantStore()
