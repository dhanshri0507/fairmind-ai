"""
Router: POST /api/scan
Accepts CSV upload, runs fairness audit, saves to Supabase, returns results.
"""

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
import io
import uuid
from services.fairness import run_full_audit
from services.firestore import save_audit

router = APIRouter()


@router.post("/scan")
async def scan_dataset(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    protected_attributes: str = Form(...),   # comma-separated
    positive_label: str = Form(...),
):
    """
    Upload a CSV and run a full fairness audit.
    Returns per-attribute bias metrics and an overall fairness score.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        protected_list = [x.strip() for x in protected_attributes.split(",")]
        audit_id = str(uuid.uuid4())

        results = run_full_audit(df, target_column, protected_list, positive_label)
        results["audit_id"] = audit_id
        results["filename"] = file.filename

        # Persist to Supabase (errors are swallowed inside save_audit)
        await save_audit(audit_id, results)

        return JSONResponse(content=results)

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e), "detail": "Failed to process dataset."},
        )
