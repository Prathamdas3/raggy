from pydantic import BaseModel
from collections.abc import Iterable
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent
from app.core import redis_client,get_logger
from app.services import SummaryServiceDep
import time
import json

logger=get_logger(__name__)
summary_router = APIRouter(prefix="/summary", tags=["summary"])

class Item(BaseModel):
    name: str
    description: str | None

items = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]

def _stream(chat_id: str, summary: SummaryServiceDep):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"chat:{chat_id}:done")

    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        data = json.loads(message["data"])

        if data["status"] == "done":
            result = summary.get_summaries(chat_id=chat_id)
            yield ServerSentEvent(
                event="result",
                data=json.dumps({"summary": result}),
            )
            yield ServerSentEvent(event="done", data="{}")
            break


# @summary_router.get("/{chat_id}")
# def handle_summary(chat_id: str, summary: SummaryServiceDep) -> EventSourceResponse:
#     return EventSourceResponse(_stream(chat_id, summary))


@summary_router.get("/", response_class=EventSourceResponse)
def sse_items_no_async() -> Iterable[Item]:
    logger.info("connected")
    for item in items:
        time.sleep(100)
        yield item
