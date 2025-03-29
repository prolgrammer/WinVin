import logging

from utils.checklist_parser import CHECKLIST

logger = logging.getLogger("call_analytics")


def analyze_text(text):
    if not text or not text.strip():
        logger.warning("Текст отсутствует, выставляем минимальные баллы.")
        return {"competences": {}, "total_score": 0}

    results = {"competences": {}, "total_score": 100}
    total_penalty = 0

    for comp_name, comp_data in CHECKLIST.items():
        comp_results = {"score": 100, "indicators": {}, "total_penalty": 0}

        for idx, indicator in comp_data["indicators"].items():
            found = indicator["text"].lower() in text.lower()
            penalty = 0 if found else indicator["penalty"]
            comp_results["indicators"][idx] = {"found": found, "penalty": penalty}
            comp_results["total_penalty"] += penalty

        comp_results["score"] = max(0, 100 - comp_results["total_penalty"])
        total_penalty += comp_results["total_penalty"]
        results["competences"][comp_name] = comp_results

    results["total_score"] = max(0, 100 - total_penalty)
    logger.info(f"Анализ текста завершен. Итоговый балл: {results['total_score']}")
    return results


def generate_recommendations(analysis):
    recommendations = []
    for comp_name, comp_data in analysis["competences"].items():
        if comp_data["score"] < 70:
            recommendations.append(f"Обратите внимание на {comp_name}")

    if not recommendations:
        recommendations.append("Отличная работа! Все ключевые показатели выполнены.")

    return recommendations
