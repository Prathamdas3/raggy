from fastapi import APIRouter, status, HTTPException
from app.utils.logger import get_logger

router = APIRouter()

logger = get_logger(__name__)


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_summary():
    pass
