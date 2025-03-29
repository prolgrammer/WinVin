from transformers import WhisperProcessor, WhisperForConditionalGeneration, pipeline
from sentence_transformers import SentenceTransformer
from config import DEVICE, TORCH_DTYPE
from utils.logging_setup import setup_logging

logger = setup_logging()


def load_models():
    logger.info("Загрузка моделей...")
    try:
        # Whisper для распознавания речи
        model_id = "openai/whisper-large-v3"
        processor = WhisperProcessor.from_pretrained(model_id)
        model = WhisperForConditionalGeneration.from_pretrained(
            model_id, torch_dtype=TORCH_DTYPE, low_cpu_mem_usage=True
        ).to(DEVICE)

        # Модель для тональности
        sentiment_model = pipeline(
            "sentiment-analysis",
            model="blanchefort/rubert-base-cased-sentiment",
            device=0 if DEVICE.startswith("cuda") else -1
        )

        logger.info("Все модели загружены успешно!")
        return processor, model, sentiment_model
    except Exception as e:
        logger.error(f"Ошибка загрузки моделей: {str(e)}", exc_info=True)
        raise