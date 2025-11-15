from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from app.utils.logger import get_logger
from app.config import config
from typing import Optional
import threading

logger = get_logger(__name__)


class QdrantVectorStoreSingleton:
    """
    Singleton class for Qdrant vectorstore to ensure only one instance is created
    and reused across all workers and requests.
    """

    _qdrant_client: Optional[QdrantClient] = None
    _vector_store: Optional[QdrantVectorStore] = None
    _embeddings: Optional[HuggingFaceEmbeddings] = None
    _lock = threading.RLock()
    _initialized = False

    @classmethod
    def get_qdrant_client(cls) -> QdrantClient:
        """
        Get or create the Qdrant client instance.
        Thread-safe singleton implementation.

        Returns:
            QdrantClient: The Qdrant client instance

        Raises:
            RuntimeError: If client initialization fails
        """
        if cls._qdrant_client is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._qdrant_client is None:
                    try:
                        logger.info("Initializing Qdrant client singleton...")

                        # Initialize Qdrant client

                        cls._qdrant_client = QdrantClient(
                            url=f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}",
                            # host=QDRANT_HOST,
                            # port=QDRANT_PORT,
                            # api_key=QDRANT_API_KEY,
                            # https=QDRANT_USE_HTTPS
                        )

                        logger.info("✓ Qdrant client initialized successfully")

                    except Exception as e:
                        logger.error(f"✗ Failed to initialize Qdrant client: {str(e)}")
                        logger.error("Check your Qdrant configuration")
                        logger.error(f"QDRANT_HOST={config.QDRANT_HOST}")
                        logger.error(f"QDRANT_PORT={config.QDRANT_PORT}")
                        cls._qdrant_client = None
                        raise RuntimeError(
                            f"Failed to initialize Qdrant client: {str(e)}. "
                            f"Please check your Qdrant configuration and ensure the service is running."
                        )

        return cls._qdrant_client

    @classmethod
    def get_embeddings(cls) -> HuggingFaceEmbeddings:
        """
        Get or create the HuggingFace embeddings instance.

        Returns:
            HuggingFaceEmbeddings: The embeddings instance

        Raises:
            RuntimeError: If embeddings initialization fails
        """
        if cls._embeddings is None:
            with cls._lock:
                if cls._embeddings is None:
                    try:
                        logger.info("Initializing HuggingFace embeddings...")
                        logger.info(f"Embedding Model: {config.HUGGINGFACE_MODEL}")
                        logger.info(f"Device: {config.HUGGINGFACE_DEVICE}")

                        # Initialize HuggingFace embeddings
                        # This is equivalent to Xenova/all-MiniLM-L6-v2 in transformers.js
                        cls._embeddings = HuggingFaceEmbeddings(
                            model_name=config.HUGGINGFACE_MODEL,
                            model_kwargs={"device": config.HUGGINGFACE_DEVICE},
                            encode_kwargs={
                                "normalize_embeddings": True
                            },  # Important for cosine similarity
                        )

                        # Test the embeddings to ensure they work
                        logger.info("Testing embeddings with sample text...")
                        test_embedding = cls._embeddings.embed_query("test")
                        embedding_dim = len(test_embedding)
                        logger.info(f"✓ Embeddings working. Dimension: {embedding_dim}")

                        # Verify embedding dimension matches configuration
                        if embedding_dim != config.QDRANT_VECTOR_SIZE:
                            logger.warning(
                                f"⚠ Embedding dimension ({embedding_dim}) doesn't match "
                                f"configured vector size ({config.QDRANT_VECTOR_SIZE}). "
                                f"Updating QDRANT_VECTOR_SIZE to {embedding_dim}"
                            )
                            # Update the vector size to match actual embedding dimension
                            globals()["QDRANT_VECTOR_SIZE"] = embedding_dim

                        logger.info("✓ HuggingFace embeddings initialized successfully")

                    except Exception as e:
                        logger.error(f"✗ Failed to initialize embeddings: {str(e)}")
                        cls._embeddings = None
                        raise RuntimeError(
                            f"Failed to initialize HuggingFace embeddings: {str(e)}. "
                            f"Make sure sentence-transformers is installed: pip install sentence-transformers"
                        )

        return cls._embeddings

    @classmethod
    def get_vector_store(cls) -> QdrantVectorStore:
        """
        Get or create the Qdrant vector store instance.

        Returns:
            QdrantVectorStore: The vector store instance

        Raises:
            RuntimeError: If vector store initialization fails
        """
        if cls._vector_store is None:
            with cls._lock:
                if cls._vector_store is None:
                    try:
                        logger.info("Initializing Qdrant vector store...")

                        # Get client and embeddings
                        client = cls.get_qdrant_client()
                        embeddings = cls.get_embeddings()
                       

                        # Initialize vector store
                        cls._vector_store = QdrantVectorStore(
                            client=client,
                            collection_name=config.QDRANT_COLLECTION_NAME,
                            embedding=embeddings,
                        )

                        cls._initialized = True
                        logger.info("✓ Qdrant vector store initialized successfully")

                    except Exception as e:
                        logger.error(f"✗ Failed to initialize vector store: {str(e)}")
                        cls._vector_store = None
                        raise RuntimeError(
                            f"Failed to initialize Qdrant vector store: {str(e)}"
                        )

        return cls._vector_store

    @classmethod
    def initialize_collection(cls) -> None:
        """
        Ensure the collection exists with proper configuration.
        Should be called during application startup.

        Raises:
            RuntimeError: If collection initialization fails
        """
        try:
            client = cls.get_qdrant_client()
            embeddings = cls.get_embeddings()

            # Get actual embedding dimension
            test_embedding = embeddings.embed_query("test")
            actual_vector_size = len(test_embedding)

            logger.info(f"Actual embedding dimension: {actual_vector_size}")

            # Check if collection exists
            collections = client.get_collections().collections
            collection_names = [col.name for col in collections]

            if config.QDRANT_COLLECTION_NAME not in collection_names:
                logger.info(
                    f"Collection '{config.QDRANT_COLLECTION_NAME}' does not exist. Creating..."
                )

                # Create collection with vector configuration using actual embedding size
                client.create_collection(
                    collection_name=config.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=actual_vector_size, distance=Distance.COSINE
                    ),
                )

                logger.info(
                    f"✓ Collection '{config.QDRANT_COLLECTION_NAME}' created successfully"
                )
                logger.info(f"  - Vector size: {actual_vector_size}")
                logger.info("  - Distance metric: COSINE")
            else:
                logger.info(
                    f"✓ Collection '{config.QDRANT_COLLECTION_NAME}' already exists"
                )

                # Verify collection configuration
                collection_info = client.get_collection(config.QDRANT_COLLECTION_NAME)
                existing_vector_size = collection_info.config.params.vectors.size

                if existing_vector_size != actual_vector_size:
                    logger.error(
                        f"✗ Collection vector size mismatch! "
                        f"Collection: {existing_vector_size}, Embeddings: {actual_vector_size}"
                    )
                    raise RuntimeError(
                        f"Vector size mismatch. Please delete the collection and recreate it, "
                        f"or use embeddings with {existing_vector_size} dimensions."
                    )

            # Verify collection info
            collection_info = client.get_collection(config.QDRANT_COLLECTION_NAME)
            logger.info(
                f"Collection info - Vectors count: {collection_info.vectors_count}"
            )
            logger.info(
                f"Collection info - Points count: {collection_info.points_count}"
            )

        except Exception as e:
            logger.error(f"✗ Failed to initialize collection: {str(e)}")
            raise RuntimeError(f"Failed to initialize collection: {str(e)}")

    @classmethod
    def is_initialized(cls) -> bool:
        """
        Check if the vector store has been initialized.

        Returns:
            bool: True if initialized, False otherwise
        """
        return cls._initialized

    @classmethod
    def health_check(cls) -> dict:
        """
        Perform a health check on the Qdrant connection.

        Returns:
            dict: Health check status
        """
        try:
            client = cls.get_qdrant_client()

            # Check if client is responsive
            collections = client.get_collections()

            # Check if our collection exists
            collection_names = [col.name for col in collections.collections]
            collection_exists = config.QDRANT_COLLECTION_NAME in collection_names

            # Get collection info if exists
            collection_info = None
            if collection_exists:
                info = client.get_collection(config.QDRANT_COLLECTION_NAME)
                collection_info = {
                    "vectors_count": info.vectors_count,
                    "points_count": info.points_count,
                    "status": info.status.value
                    if hasattr(info.status, "value")
                    else str(info.status),
                    "vector_size": info.config.params.vectors.size,
                }

            # Test embeddings
            embeddings_working = False
            embedding_dimension = None
            try:
                embeddings = cls.get_embeddings()
                test_embedding = embeddings.embed_query("test")
                embeddings_working = True
                embedding_dimension = len(test_embedding)
            except Exception as emb_error:
                logger.error(f"Embeddings health check failed: {str(emb_error)}")

            return {
                "healthy": True,
                "client_initialized": cls._initialized,
                "collection_exists": collection_exists,
                "collection_name": config.QDRANT_COLLECTION_NAME,
                "collection_info": collection_info,
                "embeddings_working": embeddings_working,
                "embedding_dimension": embedding_dimension,
                "embedding_model": config.HUGGINGFACE_MODEL,
                "host": config.QDRANT_HOST,
                "port": config.QDRANT_PORT,
            }

        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return {
                "healthy": False,
                "client_initialized": cls._initialized,
                "error": str(e),
                "host": config.QDRANT_HOST,
                "port": config.QDRANT_PORT,
            }

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instances. Useful for testing or reconnection scenarios.
        """
        with cls._lock:
            logger.warning("Resetting Qdrant singleton instances")
            cls._qdrant_client = None
            cls._vector_store = None
            cls._embeddings = None
            cls._initialized = False


# Convenience functions
def get_qdrant_client() -> QdrantClient:
    """
    Get the Qdrant client singleton instance.

    Returns:
        QdrantClient: The Qdrant client instance
    """
    return QdrantVectorStoreSingleton.get_qdrant_client()


def get_vector_store() -> QdrantVectorStore:
    """
    Get the Qdrant vector store singleton instance.

    Returns:
        QdrantVectorStore: The vector store instance
    """
    return QdrantVectorStoreSingleton.get_vector_store()


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Get the HuggingFace embeddings singleton instance.

    Returns:
        HuggingFaceEmbeddings: The embeddings instance
    """
    return QdrantVectorStoreSingleton.get_embeddings()


def initialize_qdrant() -> None:
    """
    Initialize Qdrant client, embeddings, and ensure collection exists.
    Call this during application startup.
    """
    QdrantVectorStoreSingleton.initialize_collection()


def qdrant_health_check() -> dict:
    """
    Perform Qdrant health check.

    Returns:
        dict: Health check results
    """
    return QdrantVectorStoreSingleton.health_check()


def get_collection_name() -> str:
    """
    Get the configured Qdrant collection name.

    Returns:
        str: The collection name
    """
    return config.QDRANT_COLLECTION_NAME
