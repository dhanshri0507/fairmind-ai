"""
Router: POST /api/explain
Fetches audit from Supabase, calls Gemini for a bias explanation.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.request_models import ExplainRequest
from services.gemini import explain_bias
from services.firestore import get_audit
import logging

router = APIRouter()
logger = logging.getLogger("fairmind.explain")


@router.post("/explain")
async def get_explanation(req: ExplainRequest):
    """
    Generate a Gemini AI explanation of a previous audit result.
    """
    if req.audit_results:
        audit = req.audit_results
    else:
        audit = await get_audit(req.audit_id)
        if not audit:
            return JSONResponse(status_code=404, content={"error": "Audit not found", "audit_id": req.audit_id})

    # explain_bias is now synchronous
    explanation = explain_bias(audit, req.mode)
    
    # If the new explain_bias fails, it returns a string starting with "The Gemini API encountered an error:"
    if explanation.startswith("The Gemini API"):
        return JSONResponse(
            status_code=502,
            content={
                "error": "Gemini service unavailable",
                "detail": explanation,
            },
        )

    return {"explanation": explanation, "mode": req.mode, "audit_id": req.audit_id}
