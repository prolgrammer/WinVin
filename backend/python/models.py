from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class CallMetadata(BaseModel):
    manager_id: str
    call_date: str  # или datetime если предпочитаете

class DateFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CallAnalysisResponse(BaseModel):
    call_id: str
    manager_id: str
    sentiment: str
    script_compliance: float
    pause_duration: float
    keywords: list[str]
    status: str  # добавлено поле статуса
    created_at: Optional[str] = None
    processed_at: Optional[str] = None
    error: Optional[str] = None
    recommendations: list[str]