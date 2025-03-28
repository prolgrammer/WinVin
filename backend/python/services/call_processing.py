import uuid
from datetime import datetime
from typing import Dict, Any
import httpx
from fastapi import HTTPException
import logging

from migrate import db
from models import CallMetadata

logger = logging.getLogger(__name__)


class CallProcessingService:
    def __init__(self):
        self.analytics_service_url = "http://localhost:8000/analyze"  # URL сервиса анализа

    async def process_audio_background(
            self,
            file_content: bytes,
            metadata: CallMetadata,
            filename: str
    ) -> None:
        """Фоновая обработка аудиофайла"""
        try:
            # Обновляем статус на "processing"
            self.update_call_status(filename, "processing")

            # Отправляем файл в сервис анализа
            async with httpx.AsyncClient(timeout=300.0) as client:
                files = {"file": (filename, file_content, "audio/wav")}
                data = {
                    "manager_id": metadata.manager_id,
                    "call_date": metadata.call_date
                }

                response = await client.post(
                    self.analytics_service_url,
                    files=files,
                    data=data
                )

                if response.status_code != 200:
                    raise HTTPException(response.status_code, detail=response.text)

                result = response.json()

            # Сохраняем результаты
            self.save_analysis_results(filename, {
                **result,
                "status": "completed",
                "processed_at": datetime.now().isoformat()
            })

        except httpx.RequestError as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.update_call_status(filename, "failed", error=error_msg)
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.update_call_status(filename, "failed", error=error_msg)

    def create_call_record(self, data: Dict[str, Any]) -> str:
        """Создание временной записи о звонке"""
        call_id = str(uuid.uuid4())
        call_data = {
            **data,
            "call_id": call_id,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Вставка в MongoDB
        result = db.calls.insert_one(call_data)
        if not result.inserted_id:
            raise RuntimeError("Failed to create call record")

        return call_id

    def update_call_status(self, filename: str, status: str, error: str = None) -> None:
        """Обновление статуса обработки"""
        update_data = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }

        if error:
            update_data["error"] = error
            update_data["recommendations"] = [f"Ошибка обработки: {error}"]

        result = db.calls.update_one(
            {"filename": filename},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            logger.warning(f"No call found with filename: {filename}")

    def save_analysis_results(self, filename: str, results: Dict[str, Any]) -> None:
        """Сохранение результатов анализа"""
        update_data = {k: v for k, v in results.items() if k != "text"}
        update_data["updated_at"] = datetime.now().isoformat()

        result = db.calls.update_one(
            {"filename": filename},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            logger.error(f"Failed to save results for file: {filename}")
            raise RuntimeError("Call record not found")

    async def get_call_analysis(self, call_id: str) -> Dict[str, Any]:
        """Получение результатов анализа"""
        call = db.calls.find_one({"call_id": call_id})
        if not call:
            return None

        # Удаляем _id из результата
        call.pop("_id", None)
        return call


# Создаем экземпляр сервиса для использования в роутерах
call_processing_service = CallProcessingService()