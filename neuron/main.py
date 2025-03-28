import torch
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from fastapi import FastAPI, UploadFile, HTTPException
import io
import logging
from datetime import datetime
import uuid
import soundfile as sf

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Инициализация модели
def load_model():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    try:
        logger.info("Загрузка модели Whisper...")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to(device)

        processor = AutoProcessor.from_pretrained(model_id)

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
            chunk_length_s=30,  # Для длинных аудио
            stride_length_s=[5, 3],  # Перекрытие между чанками
            batch_size=8,  # Оптимально для большинства GPU
        )

        logger.info("Модель успешно загружена")
        return pipe
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {str(e)}")
        raise

# Загружаем модель при старте
try:
    asr_pipeline = load_model()
except Exception as e:
    logger.critical(f"Не удалось загрузить модель: {str(e)}")
    raise

@app.post("/analyze")
async def transcribe_audio(file: UploadFile):
    start_time = datetime.now()
    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] Начало обработки запроса")

    try:
        # Проверка формата файла
        if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.flac')):
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат аудио")

        # Чтение и конвертация аудио
        logger.info(f"[{request_id}] Чтение и конвертация аудио...")
        audio_bytes = await file.read()

        try:
            # Конвертируем в numpy массив
            with io.BytesIO(audio_bytes) as audio_stream:
                audio_data, sample_rate = sf.read(audio_stream)

                # Конвертируем в mono если нужно
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)

                # Нормализуем до float32
                audio_data = audio_data.astype(np.float32)

                # Подготавливаем входные данные для Whisper
                inputs = {
                    "raw": audio_data,
                    "sampling_rate": sample_rate
                }

                logger.info(f"[{request_id}] Запуск распознавания...")
                result = asr_pipeline(
                    inputs,
                    generate_kwargs={
                        "language": "russian",
                        "return_timestamps": True,  # Явно включаем временные метки
                        "task": "transcribe"  # Явно указываем задачу транскрибации
                    }
                )

                # Получаем только текст без временных меток
                text = result["text"]
                processing_time = (datetime.now() - start_time).total_seconds()

                logger.info(f"[{request_id}] Успешно распознано {len(text)} символов за {processing_time:.2f} сек")

                return {
                    "text": text,
                    "processing_time": processing_time,
                    "request_id": request_id
                }

        except sf.LibsndfileError as e:
            logger.error(f"[{request_id}] Ошибка чтения аудио: {str(e)}")
            raise HTTPException(status_code=400, detail="Некорректный аудиофайл")
        except Exception as e:
            logger.error(f"[{request_id}] Ошибка распознавания: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка обработки аудио")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Неожиданная ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)