
from fastapi import APIRouter,  status, HTTPException, Depends
from app.configs.rate_limiter import rate_limit_default
from app.schemas.rag.query import AnswerInput
from app.schemas.response import Response
from app.services.db.message import (
    create_message,
    get_answer as get_answer_generated,
    get_question,
)
from app.tasks.chains import chain_answer
from app.utils.logger import get_logger
from app.schemas.db.message import QueryInput, CreateMessage, GetAnswer
from app.services.auth.token import get_user_id_from_access_token
from app.configs.database import SessionDep
from uuid import UUID

router = APIRouter(prefix="/messages")
logger = get_logger(__name__)


@router.post(
    "/{chat_id}/query",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[rate_limit_default()],
)
def ask_question(
    data: QueryInput,
    chat_id: UUID,
    session: SessionDep,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:

        question_details = CreateMessage(
                user_id=user_id, chat_id=chat_id, content=data.question
            )
        question_id = create_message(details=question_details, session=session)
        if not question_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to recive the question",
            )

        details = AnswerInput(
            chat_id=chat_id,
            user_id=user_id,
            question_id=question_id,
            question=data.question,
        )
        chain_id = chain_answer(data=details)

        return Response(
            status="success",
            message="Successfully recived the question",
            data={"question_id": question_id, "task_id": chain_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to upload the query for answer generation: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload the question for answer generation",
        )


@router.get(
    "/{chat_id}/query/{question_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit_default()],
)
def get_answer(
    question_id: UUID,
    chat_id: UUID,
    session: SessionDep,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        details = GetAnswer(user_id=user_id, chat_id=chat_id, question_id=question_id)
        answers = get_answer_generated(details=details, session=session)

        return Response(
            status="success",
            message="Successfully fetched answer for the asked question",
            data=answers,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get the answer for the question with the question_id:{question_id}, error:{str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get the answer the for the question with the id",
        )


@router.get(
    "/{chat_id}/query/{question_id}/retry",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit_default()],
)
def get_retry_answer_generation(
    question_id: UUID,
    chat_id: UUID,
    session: SessionDep,
    user_id: UUID = Depends(get_user_id_from_access_token),
):
    try:
        question_details = GetAnswer(
            user_id=user_id, chat_id=chat_id, question_id=question_id
        )
        data = get_question(details=question_details, session=session)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )

        if not data["question"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question data",
            )
        answer_payload = AnswerInput(
            chat_id=chat_id,
            user_id=user_id,
            question_id=question_id,
            question=data["question"],
        )

        # Start Celery chain
        chain_id = chain_answer(data=answer_payload)

        return Response(
            status="success",
            message="Answer regeneration task started",
            data={
                "question_id": question_id,
                "task_id": chain_id,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to upload the query for answer generation: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload the question for answer generation",
        )
