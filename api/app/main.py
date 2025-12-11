from fastapi import FastAPI
from app.lifecycle import lifespan
from app.utils.logger import get_logger
from app.api.v1.router import router
from app.api.task import router as task_router
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
import app.models.all_schema

logger = get_logger()

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    docs_url=None if config.ENV == "production" else "/docs",
    redoc_url=None if config.ENV == "production" else "/redoc",
    openapi_url=None if config.ENV == "production" else "/openapi.json",
)
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(task_router)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting the server on http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
