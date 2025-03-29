from pymongo import MongoClient
import uuid
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["call_analysis_db"]

operators_collection = db["operators"]
calls_collection = db["calls"]

def is_collection_empty(collection):
    return collection.count_documents({}) == 0

# 1. Заполнение коллекции operators
if is_collection_empty(operators_collection):
    operators = [
        {
            "operator_id": "0",
            "full_name": "Сидорова Анна Сергеевна",
            "start_date": "2022-09-01",
            "operator_type": "Менеджер",
            "call_count": 120,
            "success_rate": 0.92,
            "avg_call_duration": 150.3,
            "emotional_index": 0.85,
            "recommendation": "Продолжайте в том же духе",
            "quality_index": 0.90,
            "created_at": datetime.utcnow()
        },
        {
            "operator_id": "1",
            "full_name": "Лопушкина Валентина Дмитриевна",
            "start_date": "2024-01-15",
            "operator_type": "Менеджер",
            "call_count": 10,
            "success_rate": 0.60,
            "avg_call_duration": 240.5,
            "emotional_index": 0.55,
            "recommendation": "Улучшайте скорость ответа и уверенность",
            "quality_index": 0.50,
            "created_at": datetime.utcnow()
        },
        {
            "operator_id": "2",
            "full_name": "Петрова Татьяна Юрьевна",
            "start_date": "2023-06-10",
            "operator_type": "Менеджер",
            "call_count": 50,
            "success_rate": 0.78,
            "avg_call_duration": 180.0,
            "emotional_index": 0.70,
            "recommendation": "Старайтесь сокращать паузы",
            "quality_index": 0.75,
            "created_at": datetime.utcnow()
        },
    ]
    operators_collection.insert_many(operators)
    print("Operators collection populated with 1 record.")
else:
    print("Operators collection already exists, skipping initialization.")

# 2. Заполнение коллекции calls
if is_collection_empty(calls_collection):
    calls = [
        # Плохие звонки
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-10",
            "text": None,
            "sentiment": "NEGATIVE",
            "script_compliance": 0.35,
            "pause_duration": 16.884,
            "keywords": ["каталог"],
            "success": False,
            "recommendations": ["Улучшить коммуникацию и аргументацию"],
            "filename": "2025-03-10 09-03-23 +79143232053.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 65, "indicators": {"1": {"found": False, "penalty": 3}, "2": {"found": True, "penalty": 0}, "3": {"found": False, "penalty": 3}, "4": {"found": False, "penalty": 3}, "5": {"found": False, "penalty": 2}}, "total_penalty": 11},
                "Эффективная коммуникация": {"score": 40, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": False, "penalty": 3}, "8": {"found": False, "penalty": 3}, "9": {"found": False, "penalty": 3}, "10": {"found": False, "penalty": 3}, "11": {"found": False, "penalty": 3}, "12": {"found": False, "penalty": 3}, "13": {"found": False, "penalty": 3}}, "total_penalty": 21},
                "Эффективная презентация": {"score": 60, "indicators": {"14": {"found": False, "penalty": 2}, "15": {"found": False, "penalty": 2}, "16": {"found": True, "penalty": 0}, "17": {"found": False, "penalty": 2}, "18": {"found": False, "penalty": 2}}, "total_penalty": 8},
                "Убедительная аргументация": {"score": 50, "indicators": {"19": {"found": False, "penalty": 4}, "20": {"found": False, "penalty": 4}, "21": {"found": False, "penalty": 4}, "22": {"found": False, "penalty": 4}}, "total_penalty": 16},
                "Ориентация на результат": {"score": 45, "indicators": {"23": {"found": False, "penalty": 2}, "24": {"found": False, "penalty": 2}, "25": {"found": False, "penalty": 2}, "26": {"found": False, "penalty": 2}, "27": {"found": True, "penalty": 0}, "28": {"found": False, "penalty": 2}}, "total_penalty": 10},
                "Инициативность": {"score": 80, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Клиентоориентированность": {"score": 85, "indicators": {"31": {"found": False, "penalty": 4}}, "total_penalty": 4},
                "Работа в СРМ": {"score": 60, "indicators": {"32": {"found": False, "penalty": 4}, "33": {"found": False, "penalty": 4}, "34": {"found": False, "penalty": 4}, "35": {"found": False, "penalty": 4}}, "total_penalty": 16}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 18.810857,
            "sentiment_score": 0.75,
            "total_score": 35
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-19",
            "text": None,
            "sentiment": "NEGATIVE",
            "script_compliance": 0.45,
            "pause_duration": 12.096,
            "keywords": [],
            "success": False,
            "recommendations": ["Улучшить презентацию и результат"],
            "filename": "2025-03-19 09-43-47 +375291290705.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 70, "indicators": {"1": {"found": False, "penalty": 3}, "2": {"found": True, "penalty": 0}, "3": {"found": False, "penalty": 3}, "4": {"found": False, "penalty": 3}, "5": {"found": False, "penalty": 2}}, "total_penalty": 11},
                "Эффективная коммуникация": {"score": 50, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": False, "penalty": 3}, "8": {"found": False, "penalty": 3}, "9": {"found": True, "penalty": 0}, "10": {"found": False, "penalty": 3}, "11": {"found": False, "penalty": 3}, "12": {"found": False, "penalty": 3}, "13": {"found": False, "penalty": 3}}, "total_penalty": 18},
                "Эффективная презентация": {"score": 55, "indicators": {"14": {"found": False, "penalty": 2}, "15": {"found": False, "penalty": 2}, "16": {"found": False, "penalty": 2}, "17": {"found": True, "penalty": 0}, "18": {"found": False, "penalty": 2}}, "total_penalty": 8},
                "Убедительная аргументация": {"score": 65, "indicators": {"19": {"found": False, "penalty": 4}, "20": {"found": False, "penalty": 4}, "21": {"found": True, "penalty": 0}, "22": {"found": False, "penalty": 4}}, "total_penalty": 12},
                "Ориентация на результат": {"score": 40, "indicators": {"23": {"found": False, "penalty": 2}, "24": {"found": False, "penalty": 2}, "25": {"found": False, "penalty": 2}, "26": {"found": False, "penalty": 2}, "27": {"found": False, "penalty": 2}, "28": {"found": False, "penalty": 2}}, "total_penalty": 12},
                "Инициативность": {"score": 80, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Клиентоориентированность": {"score": 85, "indicators": {"31": {"found": False, "penalty": 4}}, "total_penalty": 4},
                "Работа в СРМ": {"score": 70, "indicators": {"32": {"found": True, "penalty": 0}, "33": {"found": False, "penalty": 4}, "34": {"found": False, "penalty": 4}, "35": {"found": False, "penalty": 4}}, "total_penalty": 12}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 26.18552,
            "sentiment_score": 0.82,
            "total_score": 45
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-21",
            "text": None,
            "sentiment": "NEGATIVE",
            "script_compliance": 0.30,
            "pause_duration": 15.2784,
            "keywords": [],
            "success": False,
            "recommendations": ["Улучшить доверие и коммуникацию"],
            "filename": "2025-03-21 14-18-02 +79260936538.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 60, "indicators": {"1": {"found": False, "penalty": 3}, "2": {"found": False, "penalty": 3}, "3": {"found": False, "penalty": 3}, "4": {"found": True, "penalty": 0}, "5": {"found": False, "penalty": 2}}, "total_penalty": 11},
                "Эффективная коммуникация": {"score": 45, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": False, "penalty": 3}, "8": {"found": False, "penalty": 3}, "9": {"found": False, "penalty": 3}, "10": {"found": False, "penalty": 3}, "11": {"found": False, "penalty": 3}, "12": {"found": False, "penalty": 3}, "13": {"found": False, "penalty": 3}}, "total_penalty": 21},
                "Эффективная презентация": {"score": 65, "indicators": {"14": {"found": False, "penalty": 2}, "15": {"found": True, "penalty": 0}, "16": {"found": False, "penalty": 2}, "17": {"found": False, "penalty": 2}, "18": {"found": False, "penalty": 2}}, "total_penalty": 8},
                "Убедительная аргументация": {"score": 70, "indicators": {"19": {"found": False, "penalty": 4}, "20": {"found": True, "penalty": 0}, "21": {"found": False, "penalty": 4}, "22": {"found": False, "penalty": 4}}, "total_penalty": 12},
                "Ориентация на результат": {"score": 50, "indicators": {"23": {"found": True, "penalty": 0}, "24": {"found": False, "penalty": 2}, "25": {"found": False, "penalty": 2}, "26": {"found": False, "penalty": 2}, "27": {"found": False, "penalty": 2}, "28": {"found": False, "penalty": 2}}, "total_penalty": 10},
                "Инициативность": {"score": 85, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Клиентоориентированность": {"score": 85, "indicators": {"31": {"found": False, "penalty": 4}}, "total_penalty": 4},
                "Работа в СРМ": {"score": 65, "indicators": {"32": {"found": False, "penalty": 4}, "33": {"found": True, "penalty": 0}, "34": {"found": False, "penalty": 4}, "35": {"found": False, "penalty": 4}}, "total_penalty": 12}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 21.86956,
            "sentiment_score": 0.75,
            "total_score": 30
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-01",
            "text": None,
            "sentiment": "NEGATIVE",
            "script_compliance": 0.25,
            "pause_duration": 23.148,
            "keywords": [],
            "success": False,
            "recommendations": ["Улучшить презентацию и аргументацию"],
            "filename": "MToxMDIyNTI3NTo1NTI6MzMxOTcxOTE5.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 65, "indicators": {"1": {"found": False, "penalty": 3}, "2": {"found": True, "penalty": 0}, "3": {"found": False, "penalty": 3}, "4": {"found": False, "penalty": 3}, "5": {"found": False, "penalty": 2}}, "total_penalty": 11},
                "Эффективная коммуникация": {"score": 50, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": False, "penalty": 3}, "8": {"found": False, "penalty": 3}, "9": {"found": False, "penalty": 3}, "10": {"found": False, "penalty": 3}, "11": {"found": True, "penalty": 0}, "12": {"found": False, "penalty": 3}, "13": {"found": False, "penalty": 3}}, "total_penalty": 18},
                "Эффективная презентация": {"score": 55, "indicators": {"14": {"found": False, "penalty": 2}, "15": {"found": False, "penalty": 2}, "16": {"found": False, "penalty": 2}, "17": {"found": True, "penalty": 0}, "18": {"found": False, "penalty": 2}}, "total_penalty": 8},
                "Убедительная аргументация": {"score": 50, "indicators": {"19": {"found": False, "penalty": 4}, "20": {"found": False, "penalty": 4}, "21": {"found": False, "penalty": 4}, "22": {"found": False, "penalty": 4}}, "total_penalty": 16},
                "Ориентация на результат": {"score": 45, "indicators": {"23": {"found": False, "penalty": 2}, "24": {"found": False, "penalty": 2}, "25": {"found": False, "penalty": 2}, "26": {"found": True, "penalty": 0}, "27": {"found": False, "penalty": 2}, "28": {"found": False, "penalty": 2}}, "total_penalty": 10},
                "Инициативность": {"score": 80, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Клиентоориентированность": {"score": 85, "indicators": {"31": {"found": False, "penalty": 4}}, "total_penalty": 4},
                "Работа в СРМ": {"score": 60, "indicators": {"32": {"found": False, "penalty": 4}, "33": {"found": False, "penalty": 4}, "34": {"found": False, "penalty": 4}, "35": {"found": False, "penalty": 4}}, "total_penalty": 16}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 5.987774,
            "sentiment_score": 0.76,
            "total_score": 25
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-01",
            "text": None,
            "sentiment": "NEGATIVE",
            "script_compliance": 0.40,
            "pause_duration": 13.968,
            "keywords": ["ремонт"],
            "success": False,
            "recommendations": ["Улучшить доверие и коммуникацию"],
            "filename": "MToxMDIyNTI3NTo1Nzg6NTQ2MTgzOTA.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 60, "indicators": {"1": {"found": False, "penalty": 3}, "2": {"found": False, "penalty": 3}, "3": {"found": True, "penalty": 0}, "4": {"found": False, "penalty": 3}, "5": {"found": False, "penalty": 2}}, "total_penalty": 11},
                "Эффективная коммуникация": {"score": 45, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": False, "penalty": 3}, "8": {"found": False, "penalty": 3}, "9": {"found": False, "penalty": 3}, "10": {"found": False, "penalty": 3}, "11": {"found": False, "penalty": 3}, "12": {"found": False, "penalty": 3}, "13": {"found": False, "penalty": 3}}, "total_penalty": 21},
                "Эффективная презентация": {"score": 70, "indicators": {"14": {"found": True, "penalty": 0}, "15": {"found": False, "penalty": 2}, "16": {"found": False, "penalty": 2}, "17": {"found": True, "penalty": 0}, "18": {"found": False, "penalty": 2}}, "total_penalty": 6},
                "Убедительная аргументация": {"score": 65, "indicators": {"19": {"found": False, "penalty": 4}, "20": {"found": True, "penalty": 0}, "21": {"found": False, "penalty": 4}, "22": {"found": False, "penalty": 4}}, "total_penalty": 12},
                "Ориентация на результат": {"score": 55, "indicators": {"23": {"found": True, "penalty": 0}, "24": {"found": False, "penalty": 2}, "25": {"found": False, "penalty": 2}, "26": {"found": False, "penalty": 2}, "27": {"found": False, "penalty": 2}, "28": {"found": False, "penalty": 2}}, "total_penalty": 10},
                "Инициативность": {"score": 85, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Клиентоориентированность": {"score": 85, "indicators": {"31": {"found": False, "penalty": 4}}, "total_penalty": 4},
                "Работа в СРМ": {"score": 60, "indicators": {"32": {"found": False, "penalty": 4}, "33": {"found": False, "penalty": 4}, "34": {"found": False, "penalty": 4}, "35": {"found": False, "penalty": 4}}, "total_penalty": 16}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 21.269484,
            "sentiment_score": 0.75,
            "total_score": 40
        },
        # Хорошие звонки
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-20",
            "text": None,
            "sentiment": "POSITIVE",
            "script_compliance": 0.90,
            "pause_duration": 10.5,
            "keywords": ["программа", "каталог", "ремонт", "цена"],
            "success": True,
            "recommendations": ["Отличная работа!"],
            "filename": "2025-03-20 15-24-13 +79173434884.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 92, "indicators": {"1": {"found": True, "penalty": 0}, "2": {"found": True, "penalty": 0}, "3": {"found": False, "penalty": 3}, "4": {"found": True, "penalty": 0}, "5": {"found": True, "penalty": 0}}, "total_penalty": 3},
                "Эффективная коммуникация": {"score": 88, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": True, "penalty": 0}, "8": {"found": False, "penalty": 3}, "9": {"found": True, "penalty": 0}, "10": {"found": True, "penalty": 0}, "11": {"found": True, "penalty": 0}, "12": {"found": True, "penalty": 0}, "13": {"found": False, "penalty": 3}}, "total_penalty": 6},
                "Эффективная презентация": {"score": 94, "indicators": {"14": {"found": True, "penalty": 0}, "15": {"found": True, "penalty": 0}, "16": {"found": True, "penalty": 0}, "17": {"found": True, "penalty": 0}, "18": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Убедительная аргументация": {"score": 92, "indicators": {"19": {"found": True, "penalty": 0}, "20": {"found": True, "penalty": 0}, "21": {"found": True, "penalty": 0}, "22": {"found": False, "penalty": 4}}, "total_penalty": 4},
                "Ориентация на результат": {"score": 90, "indicators": {"23": {"found": True, "penalty": 0}, "24": {"found": True, "penalty": 0}, "25": {"found": True, "penalty": 0}, "26": {"found": False, "penalty": 2}, "27": {"found": True, "penalty": 0}, "28": {"found": True, "penalty": 0}}, "total_penalty": 2},
                "Инициативность": {"score": 96, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Клиентоориентированность": {"score": 96, "indicators": {"31": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Работа в СРМ": {"score": 88, "indicators": {"32": {"found": True, "penalty": 0}, "33": {"found": True, "penalty": 0}, "34": {"found": False, "penalty": 4}, "35": {"found": True, "penalty": 0}}, "total_penalty": 4}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 19.654027,
            "sentiment_score": 0.85,
            "total_score": 90
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-21",
            "text": None,
            "sentiment": "POSITIVE",
            "script_compliance": 0.85,
            "pause_duration": 11.2,
            "keywords": ["программа", "каталог", "ремонт", "доставка"],
            "success": True,
            "recommendations": ["Сократить паузы"],
            "filename": "2025-03-21 13-29-38 +79529820714.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 90, "indicators": {"1": {"found": True, "penalty": 0}, "2": {"found": True, "penalty": 0}, "3": {"found": False, "penalty": 3}, "4": {"found": True, "penalty": 0}, "5": {"found": True, "penalty": 0}}, "total_penalty": 3},
                "Эффективная коммуникация": {"score": 85, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": False, "penalty": 3}, "8": {"found": True, "penalty": 0}, "9": {"found": True, "penalty": 0}, "10": {"found": True, "penalty": 0}, "11": {"found": True, "penalty": 0}, "12": {"found": False, "penalty": 3}, "13": {"found": True, "penalty": 0}}, "total_penalty": 6},
                "Эффективная презентация": {"score": 90, "indicators": {"14": {"found": True, "penalty": 0}, "15": {"found": True, "penalty": 0}, "16": {"found": True, "penalty": 0}, "17": {"found": False, "penalty": 2}, "18": {"found": True, "penalty": 0}}, "total_penalty": 2},
                "Убедительная аргументация": {"score": 88, "indicators": {"19": {"found": True, "penalty": 0}, "20": {"found": False, "penalty": 4}, "21": {"found": True, "penalty": 0}, "22": {"found": True, "penalty": 0}}, "total_penalty": 4},
                "Ориентация на результат": {"score": 86, "indicators": {"23": {"found": True, "penalty": 0}, "24": {"found": True, "penalty": 0}, "25": {"found": False, "penalty": 2}, "26": {"found": True, "penalty": 0}, "27": {"found": True, "penalty": 0}, "28": {"found": False, "penalty": 2}}, "total_penalty": 4},
                "Инициативность": {"score": 96, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Клиентоориентированность": {"score": 96, "indicators": {"31": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Работа в СРМ": {"score": 88, "indicators": {"32": {"found": True, "penalty": 0}, "33": {"found": True, "penalty": 0}, "34": {"found": False, "penalty": 4}, "35": {"found": True, "penalty": 0}}, "total_penalty": 4}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 21.602857,
            "sentiment_score": 0.80,
            "total_score": 85
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-21",
            "text": None,
            "sentiment": "POSITIVE",
            "script_compliance": 0.88,
            "pause_duration": 9.8,
            "keywords": ["каталог", "ремонт", "цена"],
            "success": True,
            "recommendations": ["Отличная работа!"],
            "filename": "2025-03-21 14-51-15 +79113824717.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 94, "indicators": {"1": {"found": True, "penalty": 0}, "2": {"found": True, "penalty": 0}, "3": {"found": True, "penalty": 0}, "4": {"found": False, "penalty": 3}, "5": {"found": True, "penalty": 0}}, "total_penalty": 3},
                "Эффективная коммуникация": {"score": 91, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": True, "penalty": 0}, "8": {"found": True, "penalty": 0}, "9": {"found": False, "penalty": 3}, "10": {"found": True, "penalty": 0}, "11": {"found": True, "penalty": 0}, "12": {"found": True, "penalty": 0}, "13": {"found": True, "penalty": 0}}, "total_penalty": 3},
                "Эффективная презентация": {"score": 92, "indicators": {"14": {"found": True, "penalty": 0}, "15": {"found": True, "penalty": 0}, "16": {"found": False, "penalty": 2}, "17": {"found": True, "penalty": 0}, "18": {"found": True, "penalty": 0}}, "total_penalty": 2},
                "Убедительная аргументация": {"score": 92, "indicators": {"19": {"found": True, "penalty": 0}, "20": {"found": True, "penalty": 0}, "21": {"found": False, "penalty": 4}, "22": {"found": True, "penalty": 0}}, "total_penalty": 4},
                "Ориентация на результат": {"score": 90, "indicators": {"23": {"found": True, "penalty": 0}, "24": {"found": True, "penalty": 0}, "25": {"found": True, "penalty": 0}, "26": {"found": False, "penalty": 2}, "27": {"found": True, "penalty": 0}, "28": {"found": True, "penalty": 0}}, "total_penalty": 2},
                "Инициативность": {"score": 96, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Клиентоориентированность": {"score": 96, "indicators": {"31": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Работа в СРМ": {"score": 92, "indicators": {"32": {"found": True, "penalty": 0}, "33": {"found": True, "penalty": 0}, "34": {"found": True, "penalty": 0}, "35": {"found": False, "penalty": 4}}, "total_penalty": 4}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 25.448698,
            "sentiment_score": 0.87,
            "total_score": 88
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-24",
            "text": None,
            "sentiment": "POSITIVE",
            "script_compliance": 0.92,
            "pause_duration": 8.5,
            "keywords": ["программа", "ремонт", "доставка"],
            "success": True,
            "recommendations": ["Отличная работа!"],
            "filename": "2025-03-24 14-19-04 +79223210910.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 96, "indicators": {"1": {"found": True, "penalty": 0}, "2": {"found": True, "penalty": 0}, "3": {"found": True, "penalty": 0}, "4": {"found": True, "penalty": 0}, "5": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Эффективная коммуникация": {"score": 94, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": True, "penalty": 0}, "8": {"found": True, "penalty": 0}, "9": {"found": True, "penalty": 0}, "10": {"found": True, "penalty": 0}, "11": {"found": True, "penalty": 0}, "12": {"found": False, "penalty": 3}, "13": {"found": True, "penalty": 0}}, "total_penalty": 3},
                "Эффективная презентация": {"score": 90, "indicators": {"14": {"found": True, "penalty": 0}, "15": {"found": False, "penalty": 2}, "16": {"found": True, "penalty": 0}, "17": {"found": True, "penalty": 0}, "18": {"found": True, "penalty": 0}}, "total_penalty": 2},
                "Убедительная аргументация": {"score": 96, "indicators": {"19": {"found": True, "penalty": 0}, "20": {"found": True, "penalty": 0}, "21": {"found": True, "penalty": 0}, "22": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Ориентация на результат": {"score": 92, "indicators": {"23": {"found": True, "penalty": 0}, "24": {"found": True, "penalty": 0}, "25": {"found": True, "penalty": 0}, "26": {"found": True, "penalty": 0}, "27": {"found": False, "penalty": 2}, "28": {"found": True, "penalty": 0}}, "total_penalty": 2},
                "Инициативность": {"score": 96, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Клиентоориентированность": {"score": 96, "indicators": {"31": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Работа в СРМ": {"score": 88, "indicators": {"32": {"found": True, "penalty": 0}, "33": {"found": True, "penalty": 0}, "34": {"found": False, "penalty": 4}, "35": {"found": True, "penalty": 0}}, "total_penalty": 4}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 25.178738,
            "sentiment_score": 0.90,
            "total_score": 92
        },
        {
            "call_id": str(uuid.uuid4()),
            "manager_id": "manager_000",
            "call_date": "2025-03-25",
            "text": None,
            "sentiment": "POSITIVE",
            "script_compliance": 0.95,
            "pause_duration": 7.9,
            "keywords": ["каталог", "ремонт", "цена", "доставка"],
            "success": True,
            "recommendations": ["Отличная работа!"],
            "filename": "2025-03-25 13-22-50 +79133105920.mp3",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "updated_at": datetime.utcnow(),
            "competences": {
                "Умение формировать доверие": {"score": 96, "indicators": {"1": {"found": True, "penalty": 0}, "2": {"found": True, "penalty": 0}, "3": {"found": True, "penalty": 0}, "4": {"found": True, "penalty": 0}, "5": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Эффективная коммуникация": {"score": 97, "indicators": {"6": {"found": True, "penalty": 0}, "7": {"found": True, "penalty": 0}, "8": {"found": True, "penalty": 0}, "9": {"found": True, "penalty": 0}, "10": {"found": True, "penalty": 0}, "11": {"found": True, "penalty": 0}, "12": {"found": True, "penalty": 0}, "13": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Эффективная презентация": {"score": 94, "indicators": {"14": {"found": True, "penalty": 0}, "15": {"found": True, "penalty": 0}, "16": {"found": True, "penalty": 0}, "17": {"found": True, "penalty": 0}, "18": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Убедительная аргументация": {"score": 96, "indicators": {"19": {"found": True, "penalty": 0}, "20": {"found": True, "penalty": 0}, "21": {"found": True, "penalty": 0}, "22": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Ориентация на результат": {"score": 94, "indicators": {"23": {"found": True, "penalty": 0}, "24": {"found": True, "penalty": 0}, "25": {"found": True, "penalty": 0}, "26": {"found": True, "penalty": 0}, "27": {"found": True, "penalty": 0}, "28": {"found": False, "penalty": 2}}, "total_penalty": 2},
                "Инициативность": {"score": 96, "indicators": {"29": {"found": True, "penalty": 0}, "30": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Клиентоориентированность": {"score": 96, "indicators": {"31": {"found": True, "penalty": 0}}, "total_penalty": 0},
                "Работа в СРМ": {"score": 92, "indicators": {"32": {"found": True, "penalty": 0}, "33": {"found": True, "penalty": 0}, "34": {"found": True, "penalty": 0}, "35": {"found": False, "penalty": 4}}, "total_penalty": 4}
            },
            "processed_at": datetime.utcnow(),
            "processing_time": 28.510237,
            "sentiment_score": 0.92,
            "total_score": 95
        }
    ]
    calls_collection.insert_many(calls)
    print("Calls collection populated with 10 records.")
else:
    print("Calls collection already exists, skipping initialization.")

# Проверка количества записей
print(f"Operators count: {operators_collection.count_documents({})}")
print(f"Calls count: {calls_collection.count_documents({})}")