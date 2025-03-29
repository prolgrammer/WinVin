import os
import re
from docx import Document
from typing import Dict
from config import DATA_DIR, CHECKLIST_FILE
from utils.logging_setup import setup_logging

logger = setup_logging()

def parse_word_checklist(filepath: str) -> Dict:
    logger.info(f"Парсинг чек-листа: {filepath}")
    doc = Document(filepath)
    competences = {}
    current_comp = None

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        if text.startswith('#### Компетенция:'):
            comp_name = text.split(':', 1)[1].strip()
            current_comp = {"name": comp_name, "indicators": {}, "stage": None}
            competences[comp_name] = current_comp

        elif text.startswith('Этап продаж:'):
            if current_comp:
                current_comp["stage"] = text.split(':', 1)[1].strip()

        elif re.match(r'^\d+\.\s+.+:', text):
            if current_comp:
                parts = re.split(r'[:–-]', text, maxsplit=1)
                if len(parts) == 2:
                    idx_match = re.match(r'^(\d+)\.', text)
                    idx = int(idx_match.group(1)) if idx_match else None
                    indicator_text = parts[1].strip()
                    penalty_match = re.search(r'Штрафной балл:\s*(\d+)', text)
                    penalty = int(penalty_match.group(1)) if penalty_match else 10  # По умолчанию 10
                    current_comp["indicators"][idx] = {
                        "text": indicator_text,
                        "penalty": penalty,
                        "examples": []
                    }

    logger.info(f"Распарсено {len(competences)} компетенций")
    return competences

CHECKLIST_PATH = os.path.join(DATA_DIR, CHECKLIST_FILE)
if not os.path.exists(CHECKLIST_PATH):
    raise FileNotFoundError(f"Чек-лист не найден: {CHECKLIST_PATH}")
CHECKLIST = parse_word_checklist(CHECKLIST_PATH)