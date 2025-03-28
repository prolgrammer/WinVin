import os
import re
import uuid
import numpy as np
import torch
import librosa
import soundfile as sf
from typing import Dict, List, Optional
import io
from datetime import datetime
import logging
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from docx import Document
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from sentence_transformers import SentenceTransformer
import warnings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Call Analytics API")

# Конфигурация
DATA_DIR = "data"
CHECKLIST_FILE = "Чек-лист.docx"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

os.makedirs(DATA_DIR, exist_ok=True)

# Инициализация моделей
def load_models():
    logger.info("Начинаем загрузку моделей...")
    try:
        model_id = "openai/whisper-large-v3"
        logger.info(f"Загрузка модели Whisper ({model_id})...")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=TORCH_DTYPE, low_cpu_mem_usage=True, use_safetensors=True
        ).to(DEVICE)
        processor = AutoProcessor.from_pretrained(model_id)
        asr_pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=TORCH_DTYPE,
            device=DEVICE,
            chunk_length_s=30,
            stride_length_s=[5, 3],
        )

        logger.info("Загрузка модели для эмбеддингов...")
        embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        logger.info("Загрузка модели для анализа тональности...")
        sentiment_model = pipeline(
            "sentiment-analysis",
            model="blanchefort/rubert-base-cased-sentiment",
            device=DEVICE
        )

        logger.info("Все модели успешно загружены!")
        return asr_pipe, embedder, sentiment_model
    except Exception as e:
        logger.error(f"Ошибка при загрузке моделей: {str(e)}", exc_info=True)
        raise

try:
    ASR_PIPE, EMBEDDER, SENTIMENT_MODEL = load_models()
except Exception as e:
    logger.critical(f"Не удалось загрузить модели: {str(e)}", exc_info=True)
    raise

# Парсер Word-файла
def parse_word_checklist(filepath: str) -> Dict:
    logger.info(f"Парсинг чек-листа из файла: {filepath}")
    try:
        doc = Document(filepath)
        competences = {}
        current_comp = None

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue

            if text.startswith('#### Компетенция:'):
                comp_name = text.split(':', 1)[1].strip()
                current_comp = {"name": comp_name, "indicators": {}, "stage": None}
                competences[comp_name] = current_comp
                logger.debug(f"Найдена компетенция: {comp_name}")

            elif text.startswith('Этап продаж:'):
                if current_comp:
                    current_comp["stage"] = text.split(':', 1)[1].strip()
                    logger.debug(f"Этап продаж для {current_comp['name']}: {current_comp['stage']}")

            elif re.match(r'^\d+\.\s+.+:', text):
                if current_comp:
                    parts = re.split(r'[:–-]', text, maxsplit=1)
                    if len(parts) == 2:
                        idx_match = re.match(r'^(\d+)\.', text)
                        if idx_match:
                            idx = int(idx_match.group(1))
                            indicator_text = parts[1].strip()
                            penalty_match = re.search(r'Штрафной балл:\s*(\d+)', text)
                            penalty = int(penalty_match.group(1)) if penalty_match else 0
                            current_comp["indicators"][idx] = {
                                "text": indicator_text,
                                "penalty": penalty,
                                "examples": []
                            }
                            logger.debug(f"Добавлен индикатор {idx} для {current_comp['name']}")

        logger.info(f"Успешно распарсено {len(competences)} компетенций")
        return competences
    except Exception as e:
        logger.error(f"Ошибка при парсинге чек-листа: {str(e)}", exc_info=True)
        raise

try:
    CHECKLIST_PATH = os.path.join(DATA_DIR, CHECKLIST_FILE)
    if not os.path.exists(CHECKLIST_PATH):
        raise FileNotFoundError(f"Файл чек-листа не найден: {CHECKLIST_PATH}")
    CHECKLIST = parse_word_checklist(CHECKLIST_PATH)
except Exception as e:
    logger.critical(f"Не удалось загрузить чек-лист: {str(e)}", exc_info=True)
    raise

# Модель ответа
class AnalysisResponse(BaseModel):
    call_id: str
    sentiment: str
    sentiment_score: float
    competences: Dict
    total_score: float
    script_compliance: float
    pause_duration: float
    keywords: List[str]
    success: bool
    recommendations: List[str]
    processing_time: float
    status: str = "success"

def process_audio_file(audio_bytes: bytes) -> tuple[bytes, float]:
    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
        # Анализ пауз
        non_silent = librosa.effects.split(y, top_db=20)
        total_pause = len(y) - sum(len(segment) for segment in non_silent)
        pause_duration = total_pause / sr

        with io.BytesIO() as converted_audio:
            sf.write(converted_audio, y, sr, format='WAV')
            converted_audio.seek(0)
            return converted_audio.read(), pause_duration
    except Exception as e:
        logger.warning(f"Librosa не смог обработать файл: {e}, пробуем напрямую")
        return audio_bytes, 0.0

def adjust_sentiment(sentiment: Dict, text: str, total_score: float) -> Dict:
    negative_keywords = ["плохо", "ужасно", "невозможно", "отказ"]
    if sentiment["label"] == "NEGATIVE" and total_score > 80:
        if not any(kw in text.lower() for kw in negative_keywords):
            sentiment["label"] = "NEUTRAL"
    return sentiment

def extract_keywords(text: str) -> List[str]:
    predefined_keywords = ["продукт", "программа", "каталог", "ремонт", "цена", "доставка"]
    return [kw for kw in predefined_keywords if kw in text.lower()]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_call(file: UploadFile):
    start_time = datetime.now()
    call_id = str(uuid.uuid4())
    logger.info(f"[{call_id}] Начало обработки")

    try:
        if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.flac')):
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат")

        audio_bytes = await file.read()
        processed_audio, pause_duration = process_audio_file(audio_bytes)

        with io.BytesIO(processed_audio) as audio_stream:
            try:
                data, samplerate = sf.read(audio_stream)
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)
                inputs = {"raw": data.astype(np.float32), "sampling_rate": samplerate}
                result = ASR_PIPE(inputs, generate_kwargs={"language": "russian"})
                text = result["text"]
            except Exception as e:
                logger.error(f"Ошибка обработки аудио: {str(e)}")
                raise HTTPException(status_code=400, detail="Ошибка декодирования аудио")

        # Анализ тональности
        logger.info(f"[{call_id}] Анализ тональности...")
        try:
            truncated_text = text[:2000]
            logger.info(f"[{call_id}] Анализируемый текст для тональности: {truncated_text}")
            sentiment = SENTIMENT_MODEL(truncated_text)[0]
            logger.info(f"[{call_id}] Тональность: {sentiment['label']} ({sentiment['score']})")
        except Exception as e:
            logger.error(f"[{call_id}] Ошибка анализа тональности: {str(e)}", exc_info=True)
            sentiment = {"label": "ERROR", "score": 0.0}

        # Анализ текста
        logger.info(f"[{call_id}] Анализ по чек-листу...")
        try:
            analysis = analyze_text(text)
            analysis["pause_duration"] = pause_duration
            analysis["keywords"] = extract_keywords(text)
            # Корректировка тональности
            sentiment = adjust_sentiment(sentiment, text, analysis["total_score"])
            logger.info(f"[{call_id}] Общий балл: {analysis['total_score']}")
        except Exception as e:
            logger.error(f"[{call_id}] Ошибка анализа текста: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка анализа текста")

        # Генерация рекомендаций
        logger.info(f"[{call_id}] Генерация рекомендаций...")
        try:
            recommendations = generate_recommendations(analysis)
            logger.info(f"[{call_id}] Сгенерировано {len(recommendations)} рекомендаций")
        except Exception as e:
            logger.error(f"[{call_id}] Ошибка генерации рекомендаций: {str(e)}", exc_info=True)
            recommendations = ["Ошибка генерации рекомендаций"]

        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[{call_id}] Обработка завершена за {processing_time:.2f} сек")

        return AnalysisResponse(
            call_id=call_id,
            sentiment=sentiment['label'],
            sentiment_score=sentiment['score'],
            competences=analysis["competences"],
            total_score=analysis["total_score"],
            script_compliance=analysis["total_score"] / 100,
            pause_duration=analysis["pause_duration"],
            keywords=analysis["keywords"],
            success=analysis["total_score"] > 80,
            recommendations=recommendations,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{call_id}] Неожиданная ошибка: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

def analyze_text(text: str) -> Dict:
    logger.debug("Начало анализа текста по чек-листу")
    results = {"competences": {}, "total_score": 100}
    total_penalty = 0

    for comp_name, comp_data in CHECKLIST.items():
        logger.debug(f"Анализ компетенции: {comp_name}")
        comp_results = {"score": 100, "indicators": {}, "total_penalty": 0}

        for idx, indicator in comp_data["indicators"].items():
            found = indicator["text"].lower() in text.lower()
            penalty = 0 if found else indicator["penalty"]
            comp_results["indicators"][idx] = {"found": found, "penalty": penalty}
            comp_results["total_penalty"] += penalty
            logger.debug(f"Индикатор {idx}: found={found}, penalty={penalty}")

        comp_results["score"] = max(0, 100 - comp_results["total_penalty"])
        total_penalty += comp_results["total_penalty"]
        results["competences"][comp_name] = comp_results
        logger.debug(f"Итоги по компетенции {comp_name}: score={comp_results['score']}")

    results["total_score"] = max(0, 100 - total_penalty)
    logger.info(f"Общий балл после анализа: {results['total_score']}")
    return results

def generate_recommendations(analysis: Dict) -> List[str]:
    logger.debug("Генерация рекомендаций...")
    recommendations = []
    for comp_name, comp_data in analysis["competences"].items():
        if comp_data["score"] < 70:
            missing = [str(idx) for idx, ind in comp_data["indicators"].items() if not ind["found"]]
            if missing:
                rec_text = f"{comp_name}: пропущены индикаторы {', '.join(missing)}"
                recommendations.append(rec_text)
                logger.debug(f"Добавлена рекомендация: {rec_text}")

    if not recommendations:
        recommendations.append("Отличная работа! Все ключевые показатели выполнены.")
        logger.debug("Все показатели выполнены, добавлена позитивная рекомендация")

    return recommendations

if __name__ == "__main__":
    import uvicorn
    logger.info("Запуск сервера FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=8000)