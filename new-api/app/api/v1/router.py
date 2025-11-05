from fastapi import APIRouter
from app.api.v1 import audio, input, summary, user

router = APIRouter(prefix="/api/v1", tags=["v1"])

router.include_router(audio.router)
router.include_router(input.router)
router.include_router(user.router)
router.include_router(summary.router)