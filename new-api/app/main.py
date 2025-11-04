from fastapi import FastAPI
from app.lifecycle import lifespan
from app.utils.logger import get_logger
from app.api.v1 import user, audio, summary, input
import app.models.all_schema

logger = get_logger()

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(audio.router)
app.include_router(summary.router)
app.include_router(input.router)

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting the server on http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
