"""API v1 router aggregation.

Aggregates all v1 API routers into a single router for inclusion
in the main application.
"""

from fastapi import APIRouter
from app.api.v1.auth import auth_router
from app.api.v1.user import user_router
from app.api.v1.chat import chat_router
from app.api.v1.summary import summary_router
from app.api.v1.query import query_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
v1_router.include_router(user_router)
v1_router.include_router(chat_router)
v1_router.include_router(summary_router)
v1_router.include_router(query_router)