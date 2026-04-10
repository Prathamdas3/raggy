from fastapi import APIRouter, status
from app.models import Response
from fastapi.sse import EventSourceResponse
from collections.abc import Iterable

query_router = APIRouter(prefix="/query",tags=["query"])


@query_router.get("/query", status_code=status.HTTP_200_OK, response_model=Response)
def handle_query(query: str) -> dict[str, dict[str, str]]:
    """Handle a chat query.

    Args:
        query: The user's query.

    Returns:
        Response with the chatbot's reply.
    """
    # Placeholder implementation - replace with actual chat logic
    return {"data": {"message": "successfully updated the chats"}}




@query_router.get("/query",response_class=EventSourceResponse)
def handle_answer()->Iterable[str]:
    for i in [""]:
        yield i