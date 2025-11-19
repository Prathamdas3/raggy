from pydantic import BaseModel, field_validator
from uuid import UUID


class QueryInput(BaseModel):
    chat_id: UUID
    user_id: UUID
    question: str

    @field_validator("chat_id", "user_id", mode="before")
    def check_ids(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be a valid uuid")

    @field_validator("question", mode="before")
    def check_questiono(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be a type of string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v


class AnswerInput(BaseModel):
    chat_id:UUID
    user_id:UUID
    question_id:UUID
    question:str

    @field_validator("chat_id", "user_id", "question_id", mode="before")
    def check_ids(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be a valid uuid")

    @field_validator("question", mode="before")
    def check_questiono(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be a type of string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v
