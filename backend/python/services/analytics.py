import signal
from collections import defaultdict
from datetime import datetime, timedelta
from http.client import HTTPException
from typing import Dict, List, Any

import numpy as np
from scipy.optimize import curve_fit

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

    async def get_success_rate_data(self, manager_id: str = None) -> Dict[str, int]:
        """
        Получение данных для круговой диаграммы успешных звонков
        Если manager_id не указан - статистика по всем менеджерам
        """
        query = {}
        if manager_id:
            query["manager_id"] = manager_id

        calls = list(db.calls.find(query))

        if not calls:
            return {"success": 0, "failed": 0}

        success = sum(1 for call in calls if call.get("success", False))
        failed = len(calls) - success

        return {"success": success, "failed": failed}

    async def get_sentiment_trend(self, manager_id: str = None, days: int = 7) -> Dict[str, List]:
        """
        Получение данных для линейного графика эмоционального индекса
        По умолчанию за последние 7 дней
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = {
            "call_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }

        if manager_id:
            query["manager_id"] = manager_id

        calls = list(db.calls.find(query))

        if not calls:
            return {"dates": [], "sentiment_scores": []}

        # Группируем по датам
        date_sentiment = {}
        for call in calls:
            call_date = call["call_date"][:10]  # Берем только дату без времени
            sentiment = 1 if call.get("sentiment") == "positive" else 0

            if call_date not in date_sentiment:
                date_sentiment[call_date] = []
            date_sentiment[call_date].append(sentiment)

        # Сортируем по дате и вычисляем среднее
        sorted_dates = sorted(date_sentiment.keys())
        sentiment_scores = [
            sum(date_sentiment[date]) / len(date_sentiment[date])
            for date in sorted_dates
        ]

        return {
            "dates": sorted_dates,
            "sentiment_scores": sentiment_scores
        }

    async def get_dashboard_stats(self, manager_id: str = None) -> Dict[str, Any]:
        """
        Получение основных метрик для дашборда
        """
        query = {}
        if manager_id:
            query["manager_id"] = manager_id

        calls = list(db.calls.find(query))

        if not calls:
            return {
                "total_calls": 0,
                "success_rate": 0,
                "avg_sentiment": 0
            }

        total_calls = len(calls)
        success_rate = sum(1 for call in calls if call.get("success", False)) / total_calls
        avg_sentiment = sum(
            1 if call.get("sentiment") == "positive" else 0
            for call in calls
        ) / total_calls

        return {
            "total_calls": total_calls,
            "success_rate": success_rate,
            "avg_sentiment": avg_sentiment
        }

    async def get_manager_details(self, manager_id: str) -> Dict[str, Any]:
        """Получение детальной статистики по менеджеру"""
        manager = db.managers.find_one({"manager_id": manager_id})
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

        calls = list(db.calls.find({"manager_id": manager_id}))
        total_calls = len(calls)

        if not calls:
            return {
                **manager,
                "total_calls": 0,
                "success_rate": 0,
                "avg_call_duration": 0,
                "avg_sentiment": 0
            }

        success_rate = sum(1 for call in calls if call.get("success")) / total_calls
        avg_duration = sum(call.get("duration", 0) for call in calls) / total_calls
        avg_sentiment = sum(
            1 if call.get("sentiment") == "positive" else 0
            for call in calls
        ) / total_calls

        return {
            **manager,
            "total_calls": total_calls,
            "success_rate": success_rate,
            "avg_call_duration": avg_duration,
            "avg_sentiment": avg_sentiment
        }

    async def get_manager_calls(self, manager_id: str) -> List[Dict[str, Any]]:
        """Получение всех звонков менеджера"""
        calls = list(db.calls.find({"manager_id": manager_id}))
        return [dict(call, _id=str(call["_id"])) for call in calls]

    async def get_negative_trend(self, manager_id: str, days: int = 30) -> Dict[str, Any]:
        """Анализ тренда негативных звонков с синусоидальной аппроксимацией"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        calls = list(db.calls.find({
            "manager_id": manager_id,
            "call_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }))

        # Группировка по дням
        daily_negatives = defaultdict(int)
        for call in calls:
            date = call["call_date"][:10]
            if call["sentiment"] == "negative":
                daily_negatives[date] += 1

        # Заполняем пропущенные дни нулями
        dates = sorted([
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((end_date - start_date).days + 1)
        ])

        negative_counts = [daily_negatives.get(date, 0) for date in dates]

        # Синусоидальная аппроксимация
        x = np.arange(len(negative_counts))
        y = np.array(negative_counts)

        try:
            # Находим параметры синусоиды (амплитуда, частота, фаза)
            params, _ = curve_fit(
                lambda x, A, freq, phi: A * np.sin(2 * np.pi * freq * x + phi),
                x, y,
                p0=[max(y), 1 / 7, 0]
            )
            A, freq, phi = params
            sine_wave = A * np.sin(2 * np.pi * freq * x + phi)
        except:
            # Если не удалось аппроксимировать - используем сглаживание
            sine_wave = signal.savgol_filter(y, window_length=7, polyorder=2)

        # Прогноз на 7 дней вперед
        future_dates = [
            (end_date + timedelta(days=i + 1)).strftime("%Y-%m-%d")
            for i in range(7)
        ]

        future_x = np.arange(len(dates), len(dates) + 7)
        future_y = A * np.sin(2 * np.pi * freq * future_x + phi) if 'A' in locals() else [y[-1]] * 7

        return {
            "dates": dates + future_dates,
            "actual": negative_counts + [None] * 7,
            "trend": sine_wave.tolist() + future_y.tolist(),
            "alert": any(fy > max(y) * 0.8 for fy in future_y),
            "stats": {
                "max": max(negative_counts),
                "avg": sum(negative_counts) / len(negative_counts),
                "last_week_avg": sum(negative_counts[-7:]) / 7
            }
        }