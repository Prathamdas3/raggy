from fastapi import APIRouter, status, HTTPException
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/v1")

logger = get_logger(__name__)

@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def on_signup():
    pass
