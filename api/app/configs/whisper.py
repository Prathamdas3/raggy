import whisper
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Global instance
_whisper_model_instance = None


def get_whisper_model(model_name: str = "base"):
    """
    Get or create the Whisper model instance.
    Uses singleton pattern to ensure only one model is loaded.

    Args:
        model_name: Whisper model size to use
            - "tiny" (~39MB, fastest)
            - "base" (~140MB, default)
            - "small" (~461MB)
            - "medium" (~1.4GB)
            - "large" (~2.9GB, best quality)

    Returns:
        whisper.Whisper: Loaded Whisper model instance

    Raises:
        Exception: If model loading fails
    """

    global _whisper_model_instance

    if _whisper_model_instance is not None:
        logger.debug("Returning cached whisper model instance")
        return _whisper_model_instance

    try:
        logger.info(f"Loading whisper model: {model_name}")
        _whisper_model_instance = whisper.load_model(model_name)
        logger.info(f"Whisper model '{model_name}' loaded successfully")
        return _whisper_model_instance

    except Exception as e:
        logger.error(f"Failed to load whisper model '{model_name}': {str(e)}")
        raise


def reload_whisper_model(model_name: str = "base"):
    """
    Force reload the Whisper model.
    Useful if you need to switch to a different model size.

    Args:
        model_name: Whisper model size to use

    Returns:
        whisper.Whisper: Newly loaded Whisper model instance

    Raises:
        Exception: If model loading fails
    """
    global _whisper_model_instance

    try:
        logger.info(f"Reloading Whisper model: {model_name}")
        _whisper_model_instance = None  # Clear old instance
        _whisper_model_instance = whisper.load_model(model_name)
        logger.info(f"Whisper model '{model_name}' reloaded successfully")
        return _whisper_model_instance

    except Exception as e:
        logger.error(f"Failed to reload Whisper model '{model_name}': {str(e)}")
        _whisper_model_instance = None  # Clear on failure
        raise


def get_model_instance():
    """
    Get the current Whisper model instance without loading.
    Returns None if not yet loaded.

    Returns:
        whisper.Whisper or None: Current model instance
    """
    global _whisper_model_instance
    return _whisper_model_instance


def is_model_loaded() -> bool:
    """
    Check if Whisper model is currently loaded.

    Returns:
        bool: True if model is loaded, False otherwise
    """
    global _whisper_model_instance
    return _whisper_model_instance is not None
