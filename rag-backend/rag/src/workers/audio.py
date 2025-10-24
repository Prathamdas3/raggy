from lib.celery import celery
from lib.logger import get_logger
from gtts import gTTS
from pydub import AudioSegment

logger = get_logger("workers/audio")

@celery.task(bind=True)
def convert_text_to_audio(self,text:str,chat_id:str):
    pass