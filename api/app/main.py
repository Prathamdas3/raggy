"""FastAPI application entry point.

Configures and creates the FastAPI application with all routes,
middleware, and lifespan handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import config
from app.api.router import router
from app.lifecycle import lifespan
from app.exception import register_exceptions

origins = ["http://localhost", "http://localhost:3000"]


app = FastAPI(
    lifespan=lifespan,
    title="Raggy",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    docs_url=None if config.env == "production" else "/docs",
    redoc_url=None if config.env == "production" else "/redoc",
    openapi_url=None if config.env == "production" else "/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exceptions(app)

app.include_router(router, prefix="/api")

def main():
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        log_level="debug" if config.debug else "info",
        reload=True,
        log_config=None,
    )

if __name__ == "__main__":
    main()
