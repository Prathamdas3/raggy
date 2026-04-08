"""Chat API endpoints.

Provides endpoints for managing chat conversations, including
creating, updating, sharing, and branching conversations.
"""
from aiohttp.web import Request

from fastapi import APIRouter, status, Depends
from app.models import Response
from fastapi.sse import EventSourceResponse
from collections.abc import AsyncIterable
from app.core import async_redis_client
from app.services import get_summary_service,SummaryService
import json

chat_router = APIRouter(prefix="/chat")


@chat_router.get("/query", status_code=status.HTTP_200_OK, response_model=Response)
async def handle_query(query: str) -> dict[str, dict[str, str]]:
    """Handle a chat query.

    Args:
        query: The user's query.

    Returns:
        Response with the chatbot's reply.
    """
    # Placeholder implementation - replace with actual chat logic
    return {"data": {"message": "successfully updated the chats"}}


@chat_router.get("/summary/{chat_id}",response_class=EventSourceResponse)
async def handle_summary(request:Request,chat_id:str,summary:SummaryService=Depends(get_summary_service))->AsyncIterable[str]:
    pubsub=await async_redis_client.pubsub()
    await pubsub.subscribe(f"chat:{chat_id}:done")
    async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            if data["status"] == "done":
                # fetch the actual content from 
                result =await summary.get_summaries(chat_id=chat_id)

                yield f"event: result\ndata: {json.dumps({'summary': result})}\n\n"
                yield "event: done\ndata: {}\n\n"
                break


@chat_router.get("/query?",response_class=EventSourceResponse)
async def handle_answer()->AsyncIterable[str]:
    for i in [""]:
        yield i