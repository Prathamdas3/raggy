from fastapi import APIRouter, status, HTTPException
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/v1")

logger = get_logger(__name__)

@router.get('/audio',status_code=status.HTTP_200_OK)
async def get_audio():
    pass