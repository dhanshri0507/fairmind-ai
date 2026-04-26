"""
Router: POST /api/simulate
Runs a mitigation simulation on a stored audit's dataset.
"""

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
import io
from services.fairness import simulate_mitigation
from models.request_models import SimulateRequest

router = APIRouter()


@router.post("/simulate")
async def simulate_bias_mitigation(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    protected_attribute: str = Form(...),
    positive_label: str = Form(...),
    mitigation_strategy: str = Form(...),  # "reweighing", "threshold", "equalized_odds"
):
    """
    Upload CSV and simulate bias mitigation strategy.
    Returns before/after metrics to show the improvement.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        result = simulate_mitigation(
            df,
            target_column,
            protected_attribute,
            positive_label,
            mitigation_strategy,
        )
        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e), "detail": "Simulation failed."},
        )
