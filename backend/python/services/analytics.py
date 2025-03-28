from .database import db

class AnalyticsService:
    async def get_manager_stats(self, manager_id: str, start_date: str, end_date: str) -> dict:
        """
        Получение статистики менеджера из MongoDB.
        """
        calls = db.get_all_calls(start_date, end_date)
        manager_calls = [call for call in calls if call["manager_id"] == manager_id]

        if not manager_calls:
            return None

        total_calls = len(manager_calls)
        success_rate = sum(1 for call in manager_calls if call["success"]) / total_calls
        avg_call_duration = sum(call["pause_duration"] for call in manager_calls) / total_calls  # Упрощение
        avg_sentiment = sum(1 if call["sentiment"] == "positive" else 0 for call in manager_calls) / total_calls
        common_issues = ["длинные паузы"] if avg_call_duration > 5 else []

        stats = {
            "manager_id": manager_id,
            "total_calls": total_calls,
            "success_rate": success_rate,
            "avg_call_duration": avg_call_duration,
            "avg_sentiment": avg_sentiment,
            "common_issues": common_issues
        }
        db.upsert_manager_stats(manager_id, stats)
        return stats

    async def get_dashboard_stats(self, start_date: str, end_date: str) -> dict:
        """
        Получение общей статистики для дашборда.
        """
        calls = db.get_all_calls(start_date, end_date)

        if not calls:
            return {"total_calls": 0, "success_rate": 0, "avg_call_duration": 0, "avg_sentiment": 0, "problematic_calls": []}

        total_calls = len(calls)
        success_rate = sum(1 for call in calls if call["success"]) / total_calls
        avg_call_duration = sum(call["pause_duration"] for call in calls) / total_calls
        avg_sentiment = sum(1 if call["sentiment"] == "positive" else 0 for call in calls) / total_calls
        problematic_calls = [
            {"call_id": call["call_id"], "reason": "negative sentiment"}
            for call in calls if call["sentiment"] == "negative"
        ]

        return {
            "total_calls": total_calls,
            "success_rate": success_rate,
            "avg_call_duration": avg_call_duration,
            "avg_sentiment": avg_sentiment,
            "problematic_calls": problematic_calls
        }

    async def get_recommendations(self, manager_id: str) -> dict:
        """
        Получение рекомендаций для менеджера.
        """
        stats = db.get_manager_stats(manager_id)
        if not stats:
            return None

        recommendations = []
        if stats["avg_sentiment"] < 0.7:
            recommendations.append("Старайтесь поддерживать позитивный тон")
        if stats["avg_call_duration"] > 5:
            recommendations.append("Сокращайте паузы в разговоре")
        if stats["success_rate"] < 0.8:
            recommendations.append("Работайте над улучшением скриптов")

        return {"manager_id": manager_id, "recommendations": recommendations}