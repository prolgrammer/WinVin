import io
import numpy as np
import librosa
import soundfile as sf
from typing import Tuple
from utils.logging_setup import setup_logging

logger = setup_logging()

def process_audio_file(audio_bytes: bytes) -> Tuple[np.ndarray, int, float]:
    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
        total_duration = len(y) / sr
        logger.info(f"Длительность аудио: {total_duration:.2f} сек")
        non_silent = librosa.effects.split(y, top_db=20)
        total_pause = len(y) - sum(len(segment) for segment in non_silent)
        pause_duration = total_pause / sr

        if pause_duration > total_duration * 0.9:
            logger.warning("Паузы > 90% аудио, возможно, файл пустой")
            pause_duration = total_duration * 0.1  # Ограничиваем паузы

        return y, sr, pause_duration
    except Exception as e:
        logger.error(f"Ошибка обработки аудио: {str(e)}", exc_info=True)
        raise  # Бросаем исключение, чтобы не продолжать с пустыми данными