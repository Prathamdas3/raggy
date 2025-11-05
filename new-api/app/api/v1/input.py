from fastapi import APIRouter,status,HTTPException
from app.utils.logger import get_logger

router=APIRouter()
logger=get_logger(__name__)


@router.post("/file",status_code=status.HTTP_202_ACCEPTED)
async def upload_file():
    pass
