"""Chat API endpoints.

Provides endpoints for managing chat conversations, including
creating, updating, sharing, and branching conversations.
"""

from fastapi import APIRouter, status,Request
from app.models import Response
from fastapi.sse import EventSourceResponse
from collections.abc import Iterable
from app.core import redis_client


from app.services import SummaryServiceDep
import json

chat_router = APIRouter(prefix="/chat")

@chat_router.get("/",response_model=Response)
def get_list_of_chats():...


@chat_router.get("/{chat_id}",response_class=EventSourceResponse)
def handle_summary(request:Request,chat_id:str,summary:SummaryServiceDep)-> Iterable[str]:
    pubsub=redis_client.pubsub()
    pubsub.subscribe(f"chat:{chat_id}:done")
    for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            if data["status"] == "done":
                # fetch the actual content from 
                # result =await summary.get_summaries(chat_id=chat_id)

                # yield f"event: result\ndata: {json.dumps({'summary': result})}\n\n"
                yield "event: done\ndata: {}\n\n"
                break








@chat_router.get("/query", status_code=status.HTTP_200_OK, response_model=Response)
def handle_query(query: str) -> dict[str, dict[str, str]]:
    """Handle a chat query.

    Args:
        query: The user's query.

    Returns:
        Response with the chatbot's reply.
    """
    # Placeholder implementation - replace with actual chat logic
    return {"data": {"message": "successfully updated the chats"}}




@chat_router.get("/query",response_class=EventSourceResponse)
def handle_answer()->Iterable[str]:
    for i in [""]:
        yield i