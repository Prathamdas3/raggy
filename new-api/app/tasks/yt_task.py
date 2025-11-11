from app.configs.celery import celery
from app.schemas.db.docs import CreateText, UpdateDocsData
from app.schemas.input.yt import YTInput
from app.schemas.rag.text_spliter import SplitTextArgs
from app.services.common.model import get_response
from app.utils.logger import get_logger
from fastapi import HTTPException, status
from app.services.input.yt import yt_mp3
from app.services.common.wav_converter import mp3_wav
from app.services.common.wav_text import wav_text
from app.services.db.docs import save_original_text, update_docs
from app.schemas.response import Response
from app.services.common.text_audio import text_audio
from app.services.minio_save import save_audio_minio
from app.services.rag.text_splitter import split_text
from app.services.rag.store_data import save_vectorsore

logger = get_logger(__name__)


@celery.task(bind=True)
def task_yt(self, data: YTInput):
    """Celery task for extracting the details from yt link, and coverteding them to text as well as to store them"""
    try:
        logger.debug("starting the task with youtube to db")

        # 1. convert the yt link into a mp3
        mp3_link = yt_mp3(link=data.link)
        if not mp3_link:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to convert the link to mp3",
            )

        # 2. convert the mp3 to wav
        wav_link = mp3_wav(mp3_link)
        if not wav_link:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to convert the mp3 to wav",
            )

        # 3. convert the wav to text
        text_wav = wav_text(wav_link)
        if not text_wav:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to convert the wav to text",
            )

        # 4. save the original text inside the db
        save_text = CreateText(
            user_id=data.user_id, chat_id=data.chat_id, original_text=text_wav
        )
        save_original_text(
            data=save_text,
        )  # pass the session here

        # 5. push the original data to a text spliter to save that in the vector store
        text_split = SplitTextArgs(
            chat_id=data.chat_id, user_id=data.user_id, text=text_wav
        )
        splited_text = split_text(data=text_split)

        save_vectorsore(chunks=splited_text)

        # 6. start creating the summary text
        summary_text = get_response(query=save_text)

        # 7. start creating the audio of the summary text
        temp_audio_path = text_audio(text=summary_text)

        audio_url = save_audio_minio(temp_audio_path)

        # 8. save the audio url and the summary text in the db
        save_summary_and_audio = UpdateDocsData(
            user_id=data.user_id,
            chat_id=data.chat_id,
            summary_text=summary_text,
            audio_url=audio_url,
        )
        update_docs(save_summary_and_audio)

        return Response(
            status="success",
            message="Successfully started the process of yt to text conversion",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while yt link task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to handle yt link task ",
        )
