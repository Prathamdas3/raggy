"""Chat API endpoints.

Provides endpoints for managing chat conversations, including
creating, updating, sharing, and branching conversations.
"""

from fastapi import APIRouter

chat_router = APIRouter(prefix="/chat")
