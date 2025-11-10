from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from app.utils.logger import get_logger
from app.config import config
import os

logger = get_logger(__name__)

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

    logger.debug("Initializing hugging model....")

    if not config.MODEL_ID:
        raise ValueError("MODEL_ID missing from the enviourment")

    if not config.HUGGINGFACE_API_TOKEN:
        raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")

    os.environ["HUGGINGFACE_API_TOKEN"] = config.HUGGINGFACE_API_TOKEN

    try:
        llm = HuggingFaceEndpoint(
            repo_id=config.MODEL_ID,
            task="text-generation",
            max_new_tokens=512,
            top_k=10,
            top_p=0.95,
            typical_p=0.95,
            do_sample=False,
            repetition_penalty=1.03,
            huggingfacehub_api_token=config.HUGGINGFACE_API_TOKEN,
        )
        logger.debug("HuggingFace endpoint created successfully")

    except Exception as e:
        logger.error(f"Failed to create HuggingFace endpoint: {str(e)}")
        raise Exception(f"Failed to create HuggingFace endpoint: {str(e)}")

    try:
        model = ChatHuggingFace(llm=llm)
        logger.debug("ChatHuggingFace model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to create ChatHuggingFace: {str(e)}")
        raise Exception(f"Failed to create ChatHuggingFace: {str(e)}")

    _model_instance = model
    logger.info("Model initialization complete")
    return model


def get_model():
    global _model_instance, _initialization_error

    if _model_instance is not None:
        return _model_instance

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
    return _model_instance is not None

