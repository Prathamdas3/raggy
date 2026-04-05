from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request


def register_exceptions(app: FastAPI)->None:
    from app.models import Response
    from app.core import AppException

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=Response(error=exc.message).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=Response(error="Internal Server Error").model_dump(),
        )