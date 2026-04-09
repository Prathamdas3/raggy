from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse

def register_exceptions(app: FastAPI) -> None:
    from fastapi.exceptions import HTTPException, RequestValidationError
    from app.models import Response
    from app.core import AppException, get_logger

    logger = get_logger(__name__)

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=Response(error=exc.message).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=Response(error=exc.detail).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError):
        first_error = exc.errors()[0].get("msg", "Validation error")
        return JSONResponse(
            status_code=422,
            content=Response(error=first_error).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, exc: Exception):
        if isinstance(exc, AppException):
            return await app_exception_handler(_request, exc)
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=Response(error="Internal Server Error").model_dump(),
        )