"""
Router: POST /api/report  |  GET /api/report/{audit_id}
Generates a downloadable JSON report from a stored audit.
Also lists recent audits.
"""

import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from services.firestore import get_audit, list_audits

router = APIRouter()


@router.get("/report/{audit_id}")
async def get_report(audit_id: str, fmt: str = "json"):
    """
    Retrieve a full audit report by ID.
    Returns JSON or a downloadable JSON file.
    """
    audit = await get_audit(audit_id)
    if not audit:
        return JSONResponse(status_code=404, content={"error": "Audit not found"})

    if fmt == "download":
        content = json.dumps(audit, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="fairmind_report_{audit_id[:8]}.json"'
            },
        )
    return JSONResponse(content=audit)


@router.get("/reports")
async def list_recent_reports():
    """List the 20 most recent audits."""
    audits = await list_audits(limit=20)
    return JSONResponse(content={"audits": audits})
