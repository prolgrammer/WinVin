from pymongo import MongoClient


class Database:
    def __init__(self):
        # Подключение к MongoDB (локально или через URL)
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["call_analysis_db"]
        # Коллекции
        self.calls = self.db["calls"]
        self.managers = self.db["managers"]

    def insert_call(self, call_data: dict):
        """Сохранение данных о звонке."""
        self.calls.insert_one(call_data)

    def get_call(self, call_id: str) -> dict:
        """Получение данных о звонке по ID."""
        return self.calls.find_one({"call_id": call_id})

    def upsert_manager_stats(self, manager_id: str, stats: dict):
        """Обновление или вставка статистики менеджера."""
        self.managers.update_one(
            {"manager_id": manager_id},
            {"$set": stats},
            upsert=True
        )

    def get_manager_stats(self, manager_id: str) -> dict:
        """Получение статистики менеджера."""
        return self.managers.find_one({"manager_id": manager_id})

    def get_all_calls(self, start_date: str = None, end_date: str = None) -> list:
        """Получение всех звонков с фильтром по датам."""
        query = {}
        if start_date:
            query["call_date"] = {"$gte": start_date}
        if end_date:
            query["call_date"] = {"$lte": end_date}
        return list(self.calls.find(query))


db = Database()
