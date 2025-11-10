from fastapi import APIRouter
from app.api.v1 import  auth, docs, chats,user,query

router = APIRouter(prefix="/api/v1", tags=["v1"])

router.include_router(docs.router)
router.include_router(auth.router)
router.include_router(chats.router)
router.include_router(user.router)
router.include_router(query.router)