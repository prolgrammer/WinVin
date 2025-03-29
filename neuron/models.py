from pydantic import BaseModel
from typing import Dict, List, Optional

class AnalysisResponse(BaseModel):
    call_id: str
    sentiment: str
    sentiment_score: float
    competences: Dict
    total_score: float
    script_compliance: float
    pause_duration: float
    keywords: List[str]
    success: bool
    recommendations: List[str]
    processing_time: float
    text: Optional[str] = None
    status: str = "success"