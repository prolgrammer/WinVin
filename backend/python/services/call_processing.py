import uuid
from .database import db
from models import CallMetadata, CallAnalysisResponse

class CallProcessingService:
    async def process_audio(self, file_content: bytes, metadata: CallMetadata) -> str:
        """
        Обработка аудиофайла: сохранение в MongoDB с базовыми данными.
        """
        call_id = str(uuid.uuid4())

        # Формируем данные для сохранения
        call_data = {
            "call_id": call_id,
            "manager_id": metadata.manager_id,
            "call_date": metadata.call_date,
            "text": None,  # Будет заполнено нейронкой позже
            "sentiment": "pending",
            "script_compliance": 0.0,
            "pause_duration": 0.0,
            "keywords": [],
            "success": False,
            "recommendations": ["Ожидает анализа"]
        }

        # Сохранение в MongoDB
        db.insert_call(call_data)

        # Сохранение файла на диск
        with open(f"temp_{call_id}.wav", "wb") as f:
            f.write(file_content)

        return call_id

    async def get_call_analysis(self, call_id: str) -> dict:
        call = db.get_call(call_id)
        if not call:
            return None
        call.pop("_id", None)
        return call