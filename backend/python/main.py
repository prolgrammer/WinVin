from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from models import CallMetadata, DateFilter
from services import call_processing_service, analytics_service
import json
import migrate  # Импорт файла миграции

app = FastAPI(title="Call Analysis API", description="API для анализа звонков менеджеров")


# Вызов миграции при запуске приложения
def run_migration():
    print("Running database migration...")
    migrate  # Просто импортируем, так как migrate.py сам выполняется при импорте
    print("Migration completed.")


@app.post("/upload-call", response_model=dict)
async def upload_call(file: UploadFile = File(...), metadata: str = File(...)):
    """
    Загрузка аудиозаписи звонка для анализа.
    Ожидается файл и метаданные в формате JSON через form-data.
    """
    try:
        # Парсим metadata из строки JSON
        metadata_dict = json.loads(metadata)
        metadata_obj = CallMetadata(**metadata_dict)

        file_content = await file.read()
        call_id = await call_processing_service.process_audio(file_content, metadata_obj)
        return {"call_id": call_id, "status": "processing"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata format. Expected JSON.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid metadata: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/call-analysis/{call_id}", response_model=dict)
async def get_call_analysis(call_id: str):
    analysis = await call_processing_service.get_call_analysis(call_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Call not found")
    return analysis


@app.get("/manager-stats/{manager_id}", response_model=dict)
async def get_manager_stats(manager_id: str, filters: DateFilter = Depends()):
    stats = await analytics_service.get_manager_stats(manager_id, filters.start_date, filters.end_date)
    if not stats:
        raise HTTPException(status_code=404, detail="Manager not found")
    return stats


@app.get("/dashboard", response_model=dict)
async def get_dashboard(filters: DateFilter = Depends()):
    stats = await analytics_service.get_dashboard_stats(filters.start_date, filters.end_date)
    return stats


@app.get("/recommendations/{manager_id}", response_model=dict)
async def get_recommendations(manager_id: str):
    recommendations = await analytics_service.get_recommendations(manager_id)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Manager not found")
    return recommendations


if __name__ == "__main__":
    run_migration()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
