from langchain_core.messages.ai import AIMessage
from app.core.logger import get_logger
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.runnables import RunnableConfig
from app.core.config import config
from enum import Enum
import threading

logger = get_logger(__name__)


class InvokeConfig(Enum):
    DEFAULT= {
        "max_new_tokens": 2048,
        "temperature": 0.7,
        "top_k": 50,
        "top_p": 0.95,
        "do_sample": True,
    }
    CONCISE = {
        "max_new_tokens": 512,
        "temperature": 0.3,
        "top_k": 20,
        "top_p": 0.9,
        "do_sample": True,
    }
    DETAILED = {
        "max_new_tokens": 4096,
        "temperature": 0.7,
        "top_k": 50,
        "top_p": 0.95,
        "do_sample": True,
    }


class AiModel:
    _model: ChatHuggingFace | None = None
    _lock = threading.RLock()

    @classmethod
    def _get_model(cls) -> ChatHuggingFace:
        if cls._model is None:
            with cls._lock:
                if cls._model is None:
                    try:
                        llm = HuggingFaceEndpoint(
                            repo_id=config.model_id,
                            task="text-generation",
                            repetition_penalty=1.03,
                            stop_sequences=["</s>", "<|endoftext|>"],
                            huggingfacehub_api_token=config.huggingface_api_token,
                           **InvokeConfig.DEFAULT.value,  # ty:ignore[invalid-argument-type]
                        )
                        cls._model = ChatHuggingFace(
                            llm=llm,
                            model_id=config.model_id,
                        )
                        logger.info(f"Model loaded: {config.model_id}")
                    except Exception as e:
                        cls._model = None
                        logger.error(f"Failed to load model: {e}")
                        raise
        if cls._model is None:
            raise RuntimeError("Model could not be initialized.")
        return cls._model

    @classmethod
    def invoke(
        cls,
        messages: list[HumanMessage|SystemMessage],
        invoke_config:InvokeConfig= InvokeConfig.DEFAULT,  
    ) -> AIMessage:  
        try:
            model = cls._get_model()
            response: AIMessage = model.invoke(messages, RunnableConfig(configurable=invoke_config.value)) 
            return response
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Model invocation failed: {e}")
            raise

    @classmethod
    def initialize(cls) -> None:
        """Call at startup — ensures client and all buckets are ready."""
        cls._get_model()
        
    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._model = None
            logger.warning("AI model reset.")


ai_model:AiModel = AiModel()