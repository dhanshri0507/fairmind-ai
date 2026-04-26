"""
Router: POST /api/report  |  GET /api/report/{audit_id}
Generates a downloadable JSON report from a stored audit.
Also lists recent audits.
"""

import json
import io
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from services.firestore import get_audit, list_audits
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

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
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("FairMind AI - Audit Report", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Audit ID: {audit_id}", styles['Normal']))
        elements.append(Paragraph(f"Dataset Size: {audit.get('dataset_size', 'N/A')}", styles['Normal']))
        elements.append(Paragraph(f"Fairness Score: {audit.get('fairness_score', 'N/A')}/100", styles['Normal']))
        elements.append(Spacer(1, 24))

        data = [["Attribute", "DP Gap", "Severity", "Status"]]
        per_attr = audit.get("per_attribute", {})
        for attr, metrics in per_attr.items():
            dp_gap = round(metrics.get("demographic_parity_gap", 0), 3)
            severity = metrics.get("severity", "UNKNOWN")
            status = "Biased" if metrics.get("bias_detected") else "Fair"
            data.append([attr, str(dp_gap), severity, status])

        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1"))
        ]))
        elements.append(t)

        doc.build(elements)
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": f'attachment; filename="fairmind_report_{audit_id[:8]}.pdf"'
            },
        )
    return JSONResponse(content=audit)


@router.get("/reports")
async def list_recent_reports():
    """List the 20 most recent audits."""
    audits = await list_audits(limit=20)
    return JSONResponse(content={"audits": audits})
