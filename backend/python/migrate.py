from pymongo import MongoClient
import uuid
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["call_analysis_db"]

operators_collection = db["operators"]
calls_collection = db["calls"]


def is_collection_empty(collection):
    return collection.count_documents({}) == 0


if is_collection_empty(operators_collection):
    operators = [
        {
            "operator_id": "0",
            "full_name": "Сидорова Анна Сергеевна",
            "start_date": "2022-09-01",  # Долгий стаж, senior
            "operator_type": "Менеджер",
            "call_count": 120,  # Много звонков, опыт
            "success_rate": 0.92,  # 92% успешных звонков
            "avg_call_duration": 150.3,  # 2.5 минуты, быстро и эффективно
            "emotional_index": 0.85,  # Высокий эмоциональный тон
            "recommendation": "Продолжайте в том же духе",
            "quality_index": 0.90,  # Высокий индекс качества
            "created_at": datetime.utcnow()
        },
        {
            "operator_id": "1",
            "full_name": "Лопушкина Валентина Дмитриевна",
            "start_date": "2024-01-15",  # Недавно начал, junior
            "operator_type": "Менеджер",
            "call_count": 10,  # Мало звонков, новичок
            "success_rate": 0.60,  # 60% успешных звонков
            "avg_call_duration": 240.5,  # 4 минуты, дольше из-за неопытности
            "emotional_index": 0.55,  # Средний эмоциональный тон
            "recommendation": "Улучшайте скорость ответа и уверенность",
            "quality_index": 0.50,  # Низкий индекс качества из-за опыта
            "created_at": datetime.utcnow()
        },
        {
            "operator_id": "2",
            "full_name": "Петрова Татьяна Юрьевна",
            "start_date": "2023-06-10",  # Средний стаж, middle
            "operator_type": "Менеджер",
            "call_count": 50,  # Умеренное количество звонков
            "success_rate": 0.78,  # 78% успешных звонков
            "avg_call_duration": 180.0,  # 3 минуты, оптимально
            "emotional_index": 0.70,  # Хороший эмоциональный тон
            "recommendation": "Старайтесь сокращать паузы",
            "quality_index": 0.75,  # Приличный индекс качества
            "created_at": datetime.utcnow()
        },
    ]
    operators_collection.insert_many(operators)
    print("Operators collection populated with 3 records.")
else:
    print("Operators collection already exists, skipping initialization.")

# 2. Заполнение коллекции calls (только если пустая)
if is_collection_empty(calls_collection):
    call_files = [
        "2025-03-10 09-03-23 +79143232053.mp3",
        "2025-03-19 09-43-47 +375291290705.mp3",
        "2025-03-21 14-18-02 +79260936538.mp3",
        "MToxMDIyNTI3NTo1NTI6MzMxOTcxOTE5.mp3",
        "MToxMDIyNTI3NTo1Nzg6NTQ2MTgzOTA.mp3",
        "2025-03-20 15-24-13 +79173434884.mp3",
        "2025-03-21 13-29-38 +79529820714.mp3",
        "2025-03-21 14-51-15 +79113824717.mp3",
        "2025-03-24 14-19-04 +79223210910.mp3",
        "2025-03-25 13-22-50 +79133105920.mp3"
    ]

    calls = []
    for i, filename in enumerate(call_files):
        date_str = filename.split(" ")[0] if filename[0].isdigit() else "2025-03-01"
        manager_id = 0  # Распределяем между операторами 0, 1, 2

        call_data = {
            "call_id": str(uuid.uuid4()),
            "manager_id": f"manager_00{manager_id}",
            "call_date": date_str,
            "text": None,
            "sentiment": "pending",
            "script_compliance": 0.0,
            "pause_duration": 0.0,
            "keywords": [],
            "success": False,
            "recommendations": ["Ожидает анализа"],
            "filename": filename,
            "created_at": datetime.utcnow()
        }
        calls.append(call_data)

    calls_collection.insert_many(calls)
    print("Calls collection populated with 10 records.")
else:
    print("Calls collection already exists, skipping initialization.")

# Проверка количества записей
print(f"Operators count: {operators_collection.count_documents({})}")
print(f"Calls count: {calls_collection.count_documents({})}")

