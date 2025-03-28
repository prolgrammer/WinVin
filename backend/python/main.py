from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from models import CallMetadata, DateFilter, CallAnalysisResponse
from services import call_processing_service, analytics_service
import json
import migrate
from datetime import datetime
from typing import Dict, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Call Analysis API", description="API для анализа звонков менеджеров")


def run_migration():
    logger.info("Running database migration...")
    migrate
    logger.info("Migration completed.")


@app.post("/upload-call", response_model=Dict[str, Any])
async def upload_call(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        metadata: str = File(...)
):
    """
    Загрузка аудиозаписи звонка для анализа.
    Возвращает немедленный ответ с call_id, реальная обработка идет в фоне.
    """
    try:
        # Валидация метаданных
        metadata_dict = json.loads(metadata)
        metadata_obj = CallMetadata(**metadata_dict)

        # Проверка формата файла
        if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.flac')):
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Чтение файла
        file_content = await file.read()

        # Создаем временную запись в БД
        call_id = str(datetime.now().timestamp())
        initial_data = {
            "call_id": call_id,
            "manager_id": metadata_obj.manager_id,
            "call_date": metadata_obj.call_date,
            "filename": file.filename,
            "status": "queued",
            "created_at": datetime.now().isoformat()
        }
        call_processing_service.create_call_record(initial_data)

        # Запускаем фоновую задачу
        background_tasks.add_task(
            call_processing_service.process_audio_background,
            file_content,
            metadata_obj,
            file.filename
        )

        return {
            "call_id": call_id,
            "status": "queued",
            "message": "Call is being processed. Check status later."
        }

    except json.JSONDecodeError:
        logger.error("Invalid JSON metadata")
        raise HTTPException(status_code=400, detail="Invalid metadata format. Expected JSON.")
    except ValueError as ve:
        logger.error(f"Metadata validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Invalid metadata: {str(ve)}")
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/call-analysis/{call_id}", response_model=CallAnalysisResponse)
async def get_call_analysis(call_id: str):
    """
    Получение результатов анализа звонка.
    Возвращает 404 если анализ еще не завершен или не найден.
    """
    analysis = await call_processing_service.get_call_analysis(call_id)
    if not analysis or analysis.get("status") != "completed":
        raise HTTPException(
            status_code=404,
            detail="Analysis not found or still in progress"
        )
    return analysis


# Остальные эндпоинты остаются без изменений
@app.get("/manager-stats/{manager_id}", response_model=dict)
async def get_manager_stats(manager_id: str, filters: DateFilter = Depends()):
    stats = await analytics_service.get_manager_stats(manager_id, filters.start_date, filters.end_date)
    if not stats:
        raise HTTPException(status_code=404, detail="Manager not found")
    return stats


@app.get("/dashboard", response_model=dict)
async def get_dashboard(filters: DateFilter = Depends()):
    return await analytics_service.get_dashboard_stats(filters.start_date, filters.end_date)


@app.get("/recommendations/{manager_id}", response_model=dict)
async def get_recommendations(manager_id: str):
    recommendations = await analytics_service.get_recommendations(manager_id)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Manager not found")
    return recommendations


if __name__ == "__main__":
    run_migration()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)