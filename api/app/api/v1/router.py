from fastapi import APIRouter
from app.api.v1.auth import auth_router
from app.api.v1.user import user_router
from app.api.v1.upload import file_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(file_router)