from pydantic import BaseModel
from typing import Optional, List, Any

class QuestionRequest(BaseModel):
    question: str

class MetricsResponse(BaseModel):
    receita_total: float
    ticket_medio: float
    taxa_inadimplencia: float
    total_transacoes: int
    evolucao_temporal: List[dict]

class UploadResponse(BaseModel):
    message: str
    metrics: MetricsResponse
    insights: List[str]

class AskResponse(BaseModel):
    question: str
    answer: str
