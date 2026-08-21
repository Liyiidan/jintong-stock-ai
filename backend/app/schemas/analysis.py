from datetime import datetime
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field

from app.schemas.expert import ExpertSignalOut

# 这个文件定义了分析相关的 Pydantic 模型，主要用于接口请求和响应的数据验证和序列化。
# 比如前端发送的请求的格式
# 比如返回给前端的数据格式
class AnalysisRequest(BaseModel):
    user_id: int
    stock_symbol: str


class DataSourceStatus(BaseModel):
    dataset: str
    source: str
    fetched_at: datetime | None = None
    sync_status: Literal["success", "failed", "stale"]


class AIAnalysisStatus(BaseModel):
    status: Literal["llm_success", "rules_fallback", "failed"]
    provider: str | None = None
    model: str | None = None
    fallback_components: List[str] = Field(default_factory=list)
    fallback_reasons: Dict[str, str] = Field(default_factory=dict)


class AnalysisOut(BaseModel):
    id: int
    user_id: int
    stock_symbol: str
    created_at: datetime
    final_action: str
    position_size: float
    rationale: Dict[str, Any]
    risk_notes: List[str]
    expert_signals: List[ExpertSignalOut]
    data_source_status: List[DataSourceStatus]
    ai_analysis_status: AIAnalysisStatus

    model_config = {"from_attributes": True}


class AnalysisTaskOut(BaseModel):
    task_id: str
    stock_symbol: str
    status: str
    current_step: int
    total_steps: int
    queue_position: int | None = None
    stage: str
    message: str | None = None
    error: str | None = None
    ai_analysis_status: Literal["llm_success", "rules_fallback", "failed"] | None = None
    analysis_id: int | None = None
    result: Dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class MacroStandaloneOut(BaseModel):
    generated_at: datetime
    report: Dict[str, Any]
