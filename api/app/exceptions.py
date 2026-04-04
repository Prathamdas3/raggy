from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status


def register_exceptions(app: FastAPI)->None:
    from app.models import Response
    from app.core import NotFoundException, UnauthorizedException,AppException

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(_request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=exc.status_code,
            content=Response(error=exc.message).model_dump(),
        )
        
    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(_request: Request, exc: UnauthorizedException):
        return JSONResponse(
            status_code=exc.status_code,
            content=Response(error=exc.message).model_dump(),
        )
        
    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, exc: Exception):
        if isinstance(exc, AppException):
            return JSONResponse(
                status_code=exc.status_code,
                content=Response(error=exc.message).model_dump(),
            )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=Response(error="Internal Server Error").model_dump(),
        )