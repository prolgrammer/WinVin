from typing import Dict, List
from utils.checklist_parser import CHECKLIST
from utils.logging_setup import setup_logging

logger = setup_logging()


def analyze_text(text: str) -> Dict:
    results = {"competences": {}, "total_score": 100, "keywords": []}
    total_penalty = 0
    keywords = ["продукт", "программа", "каталог", "ремонт", "цена", "доставка"]

    text_lower = text.lower().strip() if text else ""
    if not text_lower:
        logger.warning("Текст пустой, начисляем максимальные штрафы")
    else:
        results["keywords"] = [kw for kw in keywords if kw in text_lower]
        logger.info(f"Найденные ключевые слова: {results['keywords']}")

    for comp_name, comp_data in CHECKLIST.items():
        comp_results = {"score": 100, "indicators": {}, "total_penalty": 0}
        for idx, indicator in comp_data["indicators"].items():
            indicator_text = indicator["text"].lower()
            # Проверяем наличие ключевых слов или фраз
            key_phrases = indicator_text.split()
            # Учитываем синонимы или частичное совпадение
            found = False
            if text_lower:
                if "уточнил имя" in indicator_text and "как вас" in text_lower:
                    found = True
                elif "назвал свое" in indicator_text and ("это" in text_lower and "компания" in text_lower):
                    found = True
                elif "сфера деятельности" in indicator_text and any(
                        kw in text_lower for kw in ["сто", "магазин", "автопарк"]):
                    found = True
                elif "выявление лпр" in indicator_text and "работаете с" in text_lower:
                    found = True
                elif "информационные поводы" in indicator_text and "crm" in text_lower:
                    found = True
                # Добавляем остальные индикаторы по необходимости
                else:
                    # Общая проверка на наличие хотя бы одного слова из индикатора
                    found = any(phrase in text_lower for phrase in key_phrases if len(phrase) > 2)

            penalty = 0 if found else indicator["penalty"]
            comp_results["indicators"][idx] = {"found": found, "penalty": penalty}
            comp_results["total_penalty"] += penalty
            if found:
                logger.debug(f"Найден индикатор {idx} в {comp_name}: {indicator['text']}")

        comp_results["score"] = max(0, 100 - comp_results["total_penalty"])
        total_penalty += comp_results["total_penalty"]
        results["competences"][comp_name] = comp_results

    results["total_score"] = max(0, 100 - total_penalty)
    logger.info(f"Итоговый балл: {results['total_score']}")
    return results


def generate_recommendations(analysis: Dict) -> List[str]:
    low_scores = [comp_name for comp_name, comp_data in analysis["competences"].items() if comp_data["score"] < 70]
    if low_scores:
        return [f"Улучшить {', '.join(low_scores).lower()}"]
    return ["Отличная работа!"]