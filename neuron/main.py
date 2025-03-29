import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, HTTPException
from utils.logging_setup import setup_logging
from utils.model_loader import load_models
from utils.audio_processing import process_audio_file
from utils.analysis import analyze_text, generate_recommendations
from models import AnalysisResponse
import torch
import numpy as np

logger = setup_logging()
app = FastAPI(title="Call Analytics API")

try:
    PROCESSOR, MODEL, SENTIMENT_MODEL = load_models()
except Exception as e:
    logger.critical(f"Не удалось загрузить модели: {str(e)}")
    raise

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_call(file: UploadFile):
    start_time = datetime.now()
    call_id = str(uuid.uuid4())
    logger.info(f"[{call_id}] Начало обработки: {file.filename}")

    if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.flac')):
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат")

    try:
        audio_bytes = await file.read()
        audio_data, sr, pause_duration = process_audio_file(audio_bytes)

        # Распознавание речи
        inputs = PROCESSOR(audio_data, sampling_rate=sr, return_tensors="pt")
        input_features = inputs.input_features.to(MODEL.device)
        generated_ids = MODEL.generate(input_features, language="russian")
        text = PROCESSOR.batch_decode(generated_ids, skip_special_tokens=True)[0]
        logger.info(f"[{call_id}] Распознанный текст: {text[:100]}...")
    except Exception as e:
        logger.error(f"[{call_id}] Ошибка распознавания/обработки: {str(e)}", exc_info=True)
        text = ""
        pause_duration = 0.0

    # Анализ тональности
    sentiment = {"label": "UNKNOWN", "score": 0.0}
    if text.strip():
        try:
            sentiment_result = SENTIMENT_MODEL(text[:2000])[0]
            sentiment = {"label": sentiment_result["label"], "score": sentiment_result["score"]}
            logger.info(f"[{call_id}] Тональность: {sentiment['label']} ({sentiment['score']})")
        except Exception as e:
            logger.error(f"[{call_id}] Ошибка анализа тональности: {str(e)}")

    # Анализ текста
    analysis = analyze_text(text)
    analysis["pause_duration"] = pause_duration
    recommendations = generate_recommendations(analysis)
    processing_time = (datetime.now() - start_time).total_seconds()

    response = AnalysisResponse(
        call_id=call_id,
        sentiment=sentiment["label"],
        sentiment_score=sentiment["score"],
        competences=analysis["competences"],
        total_score=analysis["total_score"],
        script_compliance=analysis["total_score"] / 100,
        pause_duration=pause_duration,
        keywords=analysis["keywords"],
        success=analysis["total_score"] > 80,
        recommendations=recommendations,
        processing_time=processing_time,
        # text не включаем в ответ, он остается только в логах
    )
    logger.info(f"[{call_id}] Обработка завершена: score={response.total_score}")
    return response

if __name__ == "__main__":
    import uvicorn
    logger.info("Запуск сервера FastAPI...")
    logger.info(f"Используется устройство: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    uvicorn.run(app, host="0.0.0.0", port=8000)