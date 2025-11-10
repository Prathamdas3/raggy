from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage
from app.utils.logger import get_logger

logger=get_logger(__name__)

_model_instance=None
_initialization_error=None