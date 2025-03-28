from pydantic import BaseModel
from typing import Optional

class CallMetadata(BaseModel):
    manager_id: str
    call_date: str

class DateFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CallAnalysisResponse(BaseModel):
    call_id: str
    manager_id: str
    text: str
    sentiment: str
    script_compliance: float
    pause_duration: float
    keywords: list[str]
    success: bool
    recommendations: list[str]