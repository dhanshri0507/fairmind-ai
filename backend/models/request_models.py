from pydantic import BaseModel
from typing import Optional


class ExplainRequest(BaseModel):
    audit_id: str
    mode: str = "professional"  # "professional" or "casual"
    audit_results: Optional[dict] = None


class SimulateRequest(BaseModel):
    audit_id: str
    mitigation_strategy: str  # "reweighing", "threshold", "equalized_odds"
    target_attribute: Optional[str] = None


class ReportRequest(BaseModel):
    audit_id: str
    format: str = "json"  # "json" or "pdf"
