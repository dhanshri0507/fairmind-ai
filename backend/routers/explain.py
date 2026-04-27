"""
Router: POST /api/explain
Fetches audit from Supabase, calls Gemini for a bias explanation.
Always returns 200 — Gemini errors are handled gracefully with fallback content.
"""

from fastapi import APIRouter
from models.request_models import ExplainRequest
from services.gemini import explain_bias
from services.firestore import get_audit
from fastapi.responses import JSONResponse
import logging

router = APIRouter()
logger = logging.getLogger("fairmind.explain")


@router.post("/explain")
async def get_explanation(req: ExplainRequest):
    """
    Generate a Gemini AI explanation of a previous audit result.
    Falls back to static content on quota exhaustion — never returns 502.
    """
    if req.audit_results:
        audit = req.audit_results
    else:
        audit = await get_audit(req.audit_id)
        if not audit:
            return JSONResponse(
                status_code=404,
                content={"error": "Audit not found", "audit_id": req.audit_id},
            )

    explanation = explain_bias(audit, req.mode)
    return {"explanation": explanation, "mode": req.mode, "audit_id": req.audit_id}
