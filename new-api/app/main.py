from fastapi import FastAPI
from app.lifecycle import lifespan
from app.utils.logger import get_logger
from app.api.v1 import router
import app.models.all_schema

logger = get_logger()

app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"defaultModelsExpandDepth": -1})

app.include_router(router.router)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting the server on http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
