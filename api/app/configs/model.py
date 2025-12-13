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
        raise ValueError("MODEL_ID missing from the environment")
    
    if not config.HUGGINGFACE_API_TOKEN:
        raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")
    
    os.environ["HUGGINGFACE_API_TOKEN"] = config.HUGGINGFACE_API_TOKEN
    
    try:
        llm = HuggingFaceEndpoint(
            repo_id=config.MODEL_ID,
            task="text-generation",
            # FIXED: Increased token limit
            max_new_tokens=2048,  # Increased from 512 to 2048
            
            # FIXED: Better sampling parameters
            temperature=0.7,  # Added for more natural responses
            top_k=50,  # Increased from 10
            top_p=0.95,
            
            # FIXED: Enable sampling for better responses
            do_sample=True,  # Changed from False to True
            
            repetition_penalty=1.03,
            
            # FIXED: Add stop sequences to prevent cutoff
            stop_sequences=["</s>", "<|endoftext|>"],
            
            huggingfacehub_api_token=config.HUGGINGFACE_API_TOKEN,
        )
        logger.debug("HuggingFace endpoint created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create HuggingFace endpoint: {str(e)}")
        _initialization_error = str(e)
        raise Exception(f"Failed to create HuggingFace endpoint: {str(e)}")
    
    try:
        model = ChatHuggingFace(
            llm=llm,
            # FIXED: Add model kwargs for better chat handling
            model_id=config.MODEL_ID,
        )
        logger.debug("ChatHuggingFace model initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to create ChatHuggingFace: {str(e)}")
        _initialization_error = str(e)
        raise Exception(f"Failed to create ChatHuggingFace: {str(e)}")
    
    _model_instance = model
    logger.info("✓ Model initialization complete")
    logger.info(f"Model: {config.MODEL_ID}")
    logger.info("Max tokens: 2048")
    
    return model


def get_model():
    """
    Get the model instance. Initializes on first call.
    
    Returns:
        ChatHuggingFace: The model instance
        
    Raises:
        Exception: If initialization fails
    """
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
        _initialization_error = str(e)
        raise Exception(f"Failed to initialize model: {str(e)}")


def is_model_loaded():
    """
    Check if the model is loaded.
    
    Returns:
        bool: True if model is loaded, False otherwise
    """
    return _model_instance is not None


def reset_model():
    """
    Reset the model instance. Useful for reinitializing with new config.
    """
    global _model_instance, _initialization_error
    logger.warning("Resetting model instance")
    _model_instance = None
    _initialization_error = None


# ALTERNATIVE: Configuration based on use case
def get_model_with_config(use_case: str = "default"):
    """
    Get model with specific configuration based on use case.
    
    Args:
        use_case: One of "default", "concise", "detailed", "creative"
    
    Returns:
        ChatHuggingFace: Configured model instance
    """
    configs = {
        "default": {
            "max_new_tokens": 2048,
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 0.95,
            "do_sample": True,
        },
        "concise": {
            "max_new_tokens": 512,
            "temperature": 0.3,
            "top_k": 20,
            "top_p": 0.9,
            "do_sample": True,
        },
        "detailed": {
            "max_new_tokens": 4096,
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 0.95,
            "do_sample": True,
        },
        "creative": {
            "max_new_tokens": 2048,
            "temperature": 0.9,
            "top_k": 100,
            "top_p": 0.95,
            "do_sample": True,
        },
    }
    
    config_params = configs.get(use_case, configs["default"])
    
    try:
        llm = HuggingFaceEndpoint(
            repo_id=config.MODEL_ID,
            task="text-generation",
            **config_params,
            repetition_penalty=1.03,
            stop_sequences=["</s>", "<|endoftext|>"],
            huggingfacehub_api_token=config.HUGGINGFACE_API_TOKEN,
        )
        
        model = ChatHuggingFace(llm=llm, model_id=config.MODEL_ID)
        logger.info(f"Model configured for '{use_case}' use case")
        
        return model
        
    except Exception as e:
        logger.error(f"Failed to create model with config '{use_case}': {str(e)}")
        raise


# DEBUGGING: Add logging wrapper
def invoke_with_logging(model, messages, **kwargs):
    """
    Invoke model with detailed logging.
    
    Args:
        model: The ChatHuggingFace model
        messages: List of messages
        **kwargs: Additional invoke parameters
    
    Returns:
        Response from the model
    """
    logger.info("=" * 50)
    logger.info("MODEL INVOCATION")
    logger.info(f"Messages: {len(messages)} message(s)")
    logger.info(f"First message preview: {str(messages[0])[:100]}...")
    
    try:
        response = model.invoke(messages, **kwargs)
        
        logger.info("RESPONSE RECEIVED")
        logger.info(f"Content length: {len(response.content)} chars")
        logger.info(f"Content preview: {response.content[:100]}...")
        logger.info(f"Token usage: {response.usage_metadata}")
        logger.info(f"Finish reason: {response.response_metadata.get('finish_reason')}")
        logger.info("=" * 50)
        
        # Check if response was cut off
        if response.response_metadata.get('finish_reason') == 'length':
            logger.warning("⚠ Response was cut off due to token limit!")
            logger.warning("Consider increasing max_new_tokens")
        
        # Check if content is empty
        if not response.content or len(response.content.strip()) == 0:
            logger.error("✗ Response content is empty!")
            logger.error("This might be a prompt formatting issue")
        
        return response
        
    except Exception as e:
        logger.error(f"✗ Model invocation failed: {str(e)}")
        logger.info("=" * 50)
        raise