import uuid

from ..models import CallMetadata
from database import db
import httpx
from fastapi import HTTPException


class CallProcessingService:
    def __init__(self):
        self.analytics_service_url = "http://localhost:8000"  # URL вашего сервиса анализа

    async def process_audio(self, file_content: bytes, metadata: CallMetadata, filename: str) -> str:
        """Обновленная версия с интеграцией с сервисом анализа"""
        call_id = str(uuid.uuid4())
        existing_call = db.calls.find_one({"filename": filename})

        try:
            # Отправляем файл на анализ
            async with httpx.AsyncClient() as client:
                files = {"file": (filename, file_content, "audio/wav")}
                data = {
                    "manager_id": metadata.manager_id,
                    "call_date": metadata.call_date.isoformat() if hasattr(metadata.call_date,
                                                                           "isoformat") else metadata.call_date
                }
                response = await client.post(
                    f"{self.analytics_service_url}/analyze_call",
                    files=files,
                    data=data
                )

                if response.status_code != 200:
                    raise HTTPException(response.status_code, detail=response.text)

                analysis = response.json()
        except Exception as e:
            # В случае ошибки сохраняем базовую информацию
            analysis = {
                "text": None,
                "sentiment": "error",
                "sentiment_score": 0.0,
                "script_compliance": 0.0,
                "pause_duration": 0.0,
                "keywords": [],
                "success": False,
                "recommendations": ["Ошибка анализа: " + str(e)]
            }

        # Формируем данные для сохранения
        call_data = {
            "call_id": call_id if not existing_call else existing_call["call_id"],
            "manager_id": metadata.manager_id,
            "call_date": metadata.call_date,
            "filename": filename,
            **analysis
        }

        if existing_call:
            db.calls.update_one({"filename": filename}, {"$set": call_data})
        else:
            db.insert_call(call_data)

        return call_data["call_id"]

    async def get_call_analysis(self, call_id: str) -> dict:
        call = db.get_call(call_id)
        if not call:
            return None
        call.pop("_id", None)
        return call