from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage
import os
from lib.logger import get_logger

load_dotenv(override=True)
logger = get_logger("lib/model")


MODEL_ID = os.getenv("MODEL_ID")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
MODEL_PROMPT = """Read the following text carefully. Then create a simple summary. The summary should be very clear and easy for a dyslexic child to understand. Please use:

- Short sentences (no more than 10 words).
- Simple, everyday words (avoid hard or complex terms).
- Repetition of important ideas so they are remembered.
- Line breaks or bullet points to separate ideas.
- Explain in a friendly, calm, and supportive tone.

Text to summarize:
{context}

Now, write the summary as if you are explaining to a dyslexic child. End with a quick “big idea” sentence that reminds them what everything means in the simplest way possible.
"""

_model_instance = None
_initialization_error = None


def _initialize_model():
    """
    Initialize the model. Called only once when first needed.

    Returns:
        ChatHuggingFace: Initialized model

    Raises:
        Exception: If model initialization fails
    """
    global _model_instance, _initialization_error

    try:
        logger.info("Initializing HuggingFace model...")

        # ===== Validate Environment Variables =====
        if not MODEL_ID:
            raise ValueError("MODEL_ID environment variable not set")

        if not HUGGINGFACE_API_TOKEN:
            raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")

        logger.info(f"Model ID: {MODEL_ID}")

        # ===== Set API Token =====
        os.environ["HUGGINGFACE_API_TOKEN"] = HUGGINGFACE_API_TOKEN

        # ===== Initialize HuggingFace Endpoint =====
        try:
            llm = HuggingFaceEndpoint(
                repo_id=MODEL_ID,
                task="text-generation",
                max_new_tokens=512,
                top_k=10,
                top_p=0.95,
                typical_p=0.95,
                do_sample=False,
                repetition_penalty=1.03,
               huggingfacehub_api_token=HUGGINGFACE_API_TOKEN
            )
            logger.info("HuggingFace endpoint created successfully")
        except Exception as e:
            logger.error(f"Failed to create HuggingFace endpoint: {str(e)}")
            raise Exception(f"Failed to create HuggingFace endpoint: {str(e)}")

        # ===== Initialize Chat Model =====
        try:
            model = ChatHuggingFace(llm=llm)
            logger.info("ChatHuggingFace model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to create ChatHuggingFace: {str(e)}")
            raise Exception(f"Failed to create ChatHuggingFace: {str(e)}")

        _model_instance = model
        logger.info("Model initialization complete")
        return model

    except Exception as e:
        _initialization_error = str(e)
        logger.exception(f"Model initialization failed: {str(e)}")
        raise


def get_model():
    """
    Get the model instance (lazy loading - initializes on first call).

    Returns:
        ChatHuggingFace: The model instance

    Raises:
        Exception: If model initialization failed
    """
    global _model_instance, _initialization_error

    # Return cached instance if available
    if _model_instance is not None:
        return _model_instance

    # If initialization previously failed, raise that error
    if _initialization_error is not None:
        raise Exception(
            f"Model initialization previously failed: {_initialization_error}"
        )

    # Initialize model (first call)
    try:
        return _initialize_model()
    except Exception as e:
        raise Exception(f"Failed to initialize model: {str(e)}")


def is_model_loaded():
    """
    Check if model is currently loaded.

    Returns:
        bool: True if model is loaded, False otherwise
    """
    return _model_instance is not None


def get_response(query: str) -> str:
    """
    Get response from the model for a given query.

    Args:
        query: The user's question or request (e.g., "Summarize this for me")

    Returns:
        str: Model response

    Raises:
        ValueError: If query is empty
        Exception: If model fails to generate response
    """
    logger.info(f"Getting response for query (length: {len(query) if query else 0})")

    try:
        # ===== Input Validation =====
        if not query:
            logger.error("Empty query provided")
            raise ValueError("Query cannot be empty")

        if not isinstance(query, str):
            logger.warning(f"Query is not string: {type(query)}, converting")
            query = str(query)

        query = query.strip()

        if not query:
            logger.error("Query is empty after stripping")
            raise ValueError("Query cannot be empty or only whitespace")

        # Warn if query is very long
        if len(query) > 10000:
            logger.warning(f"Query is very long: {len(query)} characters")

        # ===== Get Model Instance =====
        try:
            model = get_model()
        except Exception as e:
            logger.error(f"Failed to get model: {str(e)}")
            raise Exception(f"Model not available: {str(e)}")

        # ===== Prepare Messages =====
        try:
            formatted_system_prompt = MODEL_PROMPT
            messages = [
                SystemMessage(content=formatted_system_prompt),
                HumanMessage(content=query),
            ]

        except Exception as e:
            logger.error(f"Failed to prepare messages: {str(e)}")
            raise Exception(f"Failed to prepare messages: {str(e)}")

        # ===== Generate Response =====
        try:
            logger.info("Invoking model...")
            response = model.invoke(messages)

            if not response:
                logger.error("Model returned empty response")
                raise Exception("Model returned empty response")

            if not hasattr(response, "content"):
                logger.error(f"Response has no content attribute: {type(response)}")
                raise Exception("Invalid response format from model")

            content = response.content

            if not content:
                logger.warning("Model response content is empty")
                return ""

            if not isinstance(content, str):
                logger.warning(
                    f"Response content is not string: {type(content)}, converting"
                )
                content = str(content)

            logger.info(f"Response generated successfully (length: {len(content)})")
            return content.strip()

        except Exception as e:
            logger.exception(f"Model invocation failed: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")

    except ValueError:
        raise

    except Exception as e:
        logger.exception(f"Error in get_response: {str(e)}")
        raise Exception(f"Failed to get response: {str(e)}")
