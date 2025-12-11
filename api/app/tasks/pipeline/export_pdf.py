from app.configs.celery import celery
from app.configs.database import get_celery_session
from app.schemas.db.chat import GetSummary
from app.services.common.export import build_export_chat_content, generate_chat_pdf
from app.utils.logger import get_logger
from sqlmodel import select
from app.models.all_schema import User, Chats
from app.config import config
from app.services.common.minio_save import upload_to_minio
from pathlib import Path

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_export_chat(self, details: dict):
    data = GetSummary(**details)
    logger.debug(f"Starting export task for chat_id: {data.chat_id}")

    try:
        with get_celery_session() as session:
            user = session.exec(select(User).where(User.id == data.user_id)).first()
            if not user:
                raise ValueError(f"User {data.user_id} does not exist")

            chat = session.exec(select(Chats).where(Chats.id == data.chat_id)).first()
            if not chat:
                raise ValueError(f"Chat {data.chat_id} does not exist")

            # Build content for PDF
            content = build_export_chat_content(details=data, session=session)
            if not content:
                raise ValueError("No content found for PDF export")

            logger.debug(f"Export content prepared for chat: {data.chat_id}")

            # Generate PDF locally
            Path(config.TEMP_DIR).mkdir(parents=True, exist_ok=True)
            temp_path = Path(config.TEMP_DIR) / f"chat_{data.chat_id}.pdf"

            generate_chat_pdf(content=content, output_path=str(temp_path))

            logger.debug(f"PDF generated at: {temp_path}")

            # Upload PDF to MinIO
            minio_url = upload_to_minio(
                file_path=temp_path,
                chat_id=data.chat_id,
                folder="pdf", 
                content_type="application/pdf",
                expires_days=7,
            )

            logger.info(f"PDF uploaded to MinIO for chat {data.chat_id}: {minio_url}")

            # RETURN URL (task result)
            return str(minio_url)

    # Error Handling
    except ValueError as e:
        logger.error(f"Validation error during export: {e}", exc_info=True)
        raise  # do NOT retry user errors

    except Exception as e:
        logger.error(f"Export task failed for chat {data.chat_id}: {e}", exc_info=True)

        raise self.retry(exc=e)
