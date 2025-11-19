from fastapi import APIRouter, status, HTTPException, Depends
from app.configs.rate_limiter import rate_limit_default
from app.schemas.rag.query import AnswerInput
from app.schemas.response import Response
from app.services.db.message import create_message, get_answer as get_answer_generated
from app.tasks.chains import chain_answer
from app.utils.logger import get_logger
from app.schemas.db.message import QueryInput, CreateMessage, GetAnswer
from app.services.auth.token import get_user_id_from_access_token
from app.configs.database import SessionDep
from uuid import UUID

router = APIRouter(prefix="/messages")
logger = get_logger(__name__)


@router.post(
    "{chat_id}/query",
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
        details = CreateMessage(user_id=user_id, chat_id=chat_id, content=data.question)
        question_id = create_message(details=details, session=session)
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
        answer = get_answer_generated(details=details, session=session)

        if not answer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No answer found for the given question id:{question_id}",
            )

        return Response(
            status="success",
            message="Successfully fetched answer for the asked question",
            data=answer,
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
