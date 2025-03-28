import os
import re
import uuid
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from docx import Document
import torch
from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    pipeline,
    Pipeline
)
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Call Analytics API")

DATA_DIR = "data"
CHECKLIST_FILE = "Чек-лист.docx"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32


def load_models() -> tuple[Pipeline, SentenceTransformer]:
    """Загружает все необходимые модели"""
    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=TORCH_DTYPE,
        low_cpu_mem_usage=True,
        use_safetensors=True
    ).to(DEVICE)

    processor = AutoProcessor.from_pretrained(model_id)

    asr_pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=30,
        batch_size=16,
        torch_dtype=TORCH_DTYPE,
        device=DEVICE,
    )

    embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    return asr_pipe, embedder


ASR_PIPE, EMBEDDER = load_models()
SENTIMENT_MODEL = pipeline(
    "sentiment-analysis",
    model="blanchefort/rubert-base-cased-sentiment",
    device=DEVICE
)


def parse_word_checklist(filepath: str) -> Dict:
    doc = Document(filepath)
    competences = {}
    current_comp = None

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        if text.startswith('#### Компетенция:'):
            comp_name = text.split(':', 1)[1].strip()
            current_comp = {
                "name": comp_name,
                "indicators": {},
                "stage": None
            }
            competences[comp_name] = current_comp

        elif text.startswith('Этап продаж:'):
            if current_comp:
                current_comp["stage"] = text.split(':', 1)[1].strip()

        elif re.match(r'^\d+\.\s+.+:', text):
            if current_comp:
                parts = re.split(r'[:–-]', text, maxsplit=1)
                if len(parts) == 2:
                    idx_match = re.match(r'^(\d+)\.', text)
                    if idx_match:
                        idx = int(idx_match.group(1))
                        indicator_text = parts[1].strip()
                        penalty_match = re.search(r'Штрафной балл:\s*(\d+)', text)
                        penalty = int(penalty_match.group(1)) if penalty_match else 0

                        current_comp["indicators"][idx] = {
                            "text": indicator_text,
                            "penalty": penalty,
                            "examples": []
                        }
    return competences


def load_checklist() -> Dict:
    filepath = os.path.join(DATA_DIR, CHECKLIST_FILE)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Checklist file not found: {filepath}")
    return parse_word_checklist(filepath)


CHECKLIST = load_checklist()


class AnalysisResponse(BaseModel):
    call_id: str
    text: str
    sentiment: str
    sentiment_score: float
    competences: Dict
    total_score: float
    recommendations: List[str]
    processing_time: float


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_call(file: UploadFile):
    start_time = datetime.now()

    try:
        temp_file = f"temp_{uuid.uuid4()}.wav"
        with open(temp_file, "wb") as f:
            f.write(await file.read())

        result = ASR_PIPE(temp_file)
        text = result["text"]
        os.remove(temp_file)

        sentiment = SENTIMENT_MODEL(text)[0]
        analysis = analyze_text(text)

        recommendations = generate_recommendations(analysis)

        return AnalysisResponse(
            call_id=str(uuid.uuid4()),
            text=text,
            sentiment=sentiment['label'],
            sentiment_score=sentiment['score'],
            competences=analysis["competences"],
            total_score=analysis["total_score"],
            recommendations=recommendations,
            processing_time=(datetime.now() - start_time).total_seconds()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def analyze_text(text: str) -> Dict:
    """Анализирует текст по чек-листу"""
    results = {"competences": {}, "total_score": 100}
    total_penalty = 0

    for comp_name, comp_data in CHECKLIST.items():
        comp_results = {
            "score": 100,
            "indicators": {},
            "total_penalty": 0
        }

        for idx, indicator in comp_data["indicators"].items():
            found = indicator["text"].lower() in text.lower()
            penalty = 0 if found else indicator["penalty"]

            comp_results["indicators"][idx] = {
                "found": found,
                "penalty": penalty
            }
            comp_results["total_penalty"] += penalty

        comp_results["score"] = max(0, 100 - comp_results["total_penalty"])
        total_penalty += comp_results["total_penalty"]
        results["competences"][comp_name] = comp_results

    results["total_score"] = max(0, 100 - total_penalty)
    return results


def generate_recommendations(analysis: Dict) -> List[str]:
    """Генерирует рекомендации на основе анализа"""
    recommendations = []
    for comp_name, comp_data in analysis["competences"].items():
        if comp_data["score"] < 70:
            missing = [str(idx) for idx, ind in comp_data["indicators"].items() if not ind["found"]]
            if missing:
                recommendations.append(f"{comp_name}: пропущены индикаторы {', '.join(missing)}")

    if not recommendations:
        recommendations.append("Отличная работа! Все ключевые показатели выполнены.")

    return recommendations


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)