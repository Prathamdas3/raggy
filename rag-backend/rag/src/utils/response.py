from fastapi import Request
from fastapi.responses import JSONResponse
from lib.pydentic_models import ErrorResponse


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


async def api_error_handler(request: Request, exc: APIError):
    error = ErrorResponse(
        status="error", message=exc.message, code=exc.status_code, details=exc.details
    )
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())
