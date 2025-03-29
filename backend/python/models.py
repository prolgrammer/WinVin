from pydantic import BaseModel
from typing import Optional, Dict, Any, List
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

class SuccessRateResponse(BaseModel):
    success: int
    failed: int

class SentimentTrendResponse(BaseModel):
    dates: List[str]
    sentiment_scores: List[float]

class DashboardStatsResponse(BaseModel):
    total_calls: int
    success_rate: float
    avg_sentiment: float

class EmployeeStatsResponse(BaseModel):
    full_name: str
    hire_date: str
    position: str = "Менеджер"
    total_calls: int
    success_rate: float
    avg_call_duration: float
    avg_sentiment: float

class ManagerCallsResponse(BaseModel):
    calls: List[CallAnalysisResponse]

class NegativeTrendResponse(BaseModel):
    dates: List[str]
    actual: List[Optional[float]]
    trend: List[float]
    stats: Dict[str, Any]
    alert: bool
