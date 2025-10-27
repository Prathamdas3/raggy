from lib.celery import celery
from lib.logger import get_logger
from lib.qdrant import get_vector_store

logger = get_logger("workers/vectors/get_data")


@celery.task(bind=True, max_retries=3)
def search_chunks_in_vectorstore(
    self, query: str, user_id: str = None, chat_id: str = None, k: int = 5
):
    """
    Search for similar chunks in Qdrant vector store using MMR retriever with metadata filters.
    MMR (Maximal Marginal Relevance) returns diverse results to avoid redundancy.

    Args:
        query: The search query
        user_id: Optional user ID filter (filters by user_id in metadata)
        chat_id: Optional chat ID filter (filters by chat_id in metadata)
        k: Number of results to return (default: 5, max: 100)

    Returns:
        dict: Contains success status and search results with MMR ranking
    """
    try:
        logger.info(f"Starting MMR search. Query length: {len(query)}, k={k}")
        if user_id:
            logger.info(f"Filtering by user_id: {user_id}")
        if chat_id:
            logger.info(f"Filtering by chat_id: {chat_id}")

        # ===== Input Validation =====
        if not query or not isinstance(query, str):
            logger.error("Invalid query provided")
            return {
                "success": False,
                "error": "query must be a non-empty string",
                "results": None,
            }

        query = query.strip()
        if not query:
            logger.error("Query is empty after stripping")
            return {
                "success": False,
                "error": "query cannot be empty or only whitespace",
                "results": None,
            }

        # Clamp k between 1 and 100
        if k < 1:
            logger.warning(f"k value too low: {k}, using k=1")
            k = 1
        elif k > 100:
            logger.warning(f"k value too high: {k}, using k=100")
            k = 100

        # ===== Get Vector Store =====
        try:
            vector_store = get_vector_store()
            logger.info("✓ Vector store instance obtained")
        except Exception as vs_error:
            logger.error(f"✗ Failed to get vector store: {str(vs_error)}")
            return {
                "success": False,
                "error": f"Vector store error: {str(vs_error)}",
                "results": None,
            }

        # ===== Build Qdrant Filter =====
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        qdrant_filter = None
        filter_conditions = []

        if user_id:
            filter_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        if chat_id:
            filter_conditions.append(
                FieldCondition(key="chat_id", match=MatchValue(value=chat_id))
            )

        if filter_conditions:
            qdrant_filter = Filter(must=filter_conditions)
            logger.info(f"✓ Created filter with {len(filter_conditions)} condition(s)")

        # ===== Build Search kwargs =====
        search_kwargs = {"k": k, "filter": {"user_id": user_id, "chat_id": chat_id}}

        if qdrant_filter:
            search_kwargs["filter"] = qdrant_filter

        logger.info(f"Search kwargs: k={k}, filters={'Yes' if qdrant_filter else 'No'}")

        # ===== Create MMR Retriever =====
        try:
            logger.info("Creating MMR retriever...")

            retriever = vector_store.as_retriever(
                search_type="mmr",  # Fixed to MMR for diverse results
                search_kwargs=search_kwargs,
            )

            logger.info("✓ MMR retriever created successfully")

        except Exception as retriever_error:
            logger.error(f"✗ Failed to create retriever: {str(retriever_error)}")
            logger.exception("Detailed error traceback:")
            return {
                "success": False,
                "error": f"Failed to create retriever: {str(retriever_error)}",
                "results": None,
            }

        # ===== Perform Retrieval =====
        try:
            logger.info(f"Invoking MMR retriever with query: '{query[:100]}...'")

            documents = retriever.invoke(query)

            logger.info(f"✓ Found {len(documents)} diverse documents using MMR")

            # Format results
            formatted_results = []
            for i, doc in enumerate(documents):
                formatted_results.append(
                    {
                        "rank": i + 1,
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                    }
                )

            # Log sample result
            if formatted_results:
                sample = formatted_results[0]
                logger.info(f"Sample result - Rank 1:")
                logger.info(f"  Content: {sample['content'][:100]}...")
                logger.info(f"  Metadata: {sample['metadata']}")

            return {
                "success": True,
                "error": None,
                "results": formatted_results,
                "count": len(formatted_results),
            }

        except Exception as search_error:
            logger.error(f"✗ MMR retrieval failed: {str(search_error)}")
            logger.exception("Detailed error traceback:")

            # Retry on failure
            if self.request.retries < self.max_retries:
                logger.info(
                    f"Retrying task. Attempt {self.request.retries + 1}/{self.max_retries}"
                )
                raise self.retry(exc=search_error, countdown=30)

            return {
                "success": False,
                "error": f"MMR retrieval failed: {str(search_error)}",
                "results": None,
            }

    except Exception as e:
        logger.exception(
            f"✗ Unexpected error in search_chunks_in_vectorstore: {str(e)}"
        )

        # Retry on unexpected errors
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying task. Attempt {self.request.retries + 1}/{self.max_retries}"
            )
            raise self.retry(exc=e, countdown=30)

        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "results": None,
        }
