from fastapi import APIRouter
from fastapi.sse import EventSourceResponse
from collections.abc import Iterable
from app.core import redis_client
from app.services import SummaryServiceDep
import json

summary_router = APIRouter(prefix="/summary",tags=["summary"])


@summary_router.get("/{chat_id}",response_class=EventSourceResponse)
def handle_summary(chat_id:str,summary:SummaryServiceDep)-> Iterable[str]:
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

