from dataclasses import dataclass
from app.core import get_logger
from app.models import CreateUser, SigninUser, UpdatePassword, Response, Status
from app.db import AsyncDatabaseService

logger = get_logger(__name__)


# class AuthService:
    