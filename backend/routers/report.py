"""
Router: POST /api/report/generate  — generate PDF from audit data in request body
         GET  /api/report/{audit_id} — retrieve stored audit (JSON or PDF)
         GET  /api/reports           — list recent audits
"""

import io
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse, Response
from services.firestore import get_audit, list_audits
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter()


def _build_pdf(audit: dict, audit_id: str) -> bytes:
    """Build a PDF report from an audit dict and return raw bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=48,
        leftMargin=48,
        topMargin=56,
        bottomMargin=48,
    )
    styles = getSampleStyleSheet()
    elements = []

    # ── Title ──────────────────────────────────────────────────────────────
    elements.append(Paragraph("FairMind AI — Audit Report", styles["Title"]))
    elements.append(Spacer(1, 8))
    elements.append(
        Paragraph(
            f"<font size='9' color='#64748b'>Audit ID: {audit_id}</font>",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 4))

    # ── Summary ────────────────────────────────────────────────────────────
    elements.append(
        Paragraph(
            f"Dataset Size: <b>{audit.get('dataset_size', 'N/A')}</b>&nbsp;&nbsp;&nbsp;"
            f"Fairness Score: <b>{audit.get('fairness_score', 'N/A')}/100</b>&nbsp;&nbsp;&nbsp;"
            f"Status: <b>{'⚠ Biased' if audit.get('overall_bias_detected') else '✓ Fair'}</b>",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 24))

    # ── Per-attribute table ────────────────────────────────────────────────
    data = [["Attribute", "DP Gap", "EO Gap", "Severity", "Status"]]
    per_attr = audit.get("per_attribute", {})
    for attr, metrics in per_attr.items():
        dp_gap = round(metrics.get("demographic_parity_gap", 0), 3)
        eo_gap = round(metrics.get("equalized_odds_gap", 0), 3)
        severity = metrics.get("severity", "UNKNOWN")
        status = "Biased" if metrics.get("bias_detected") else "Fair"
        data.append([attr, str(dp_gap), str(eo_gap), severity, status])

    t = Table(data, colWidths=[120, 65, 65, 70, 60])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TOPPADDING", (0, 1), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 24))

    # ── Group statistics per attribute ────────────────────────────────────
    for attr, metrics in per_attr.items():
        grp_stats = metrics.get("group_statistics", {})
        if not grp_stats:
            continue
        elements.append(
            Paragraph(f"Group Statistics — {attr}", styles["Heading3"])
        )
        elements.append(Spacer(1, 6))
        grp_data = [["Group", "Count", "Positive Rate (%)"]]
        for grp, stats in grp_stats.items():
            grp_data.append(
                [
                    str(grp),
                    str(stats.get("count", 0)),
                    f"{round(stats.get('positive_rate', 0) * 100, 1)}%",
                ]
            )
        gt = Table(grp_data, colWidths=[150, 80, 120])
        gt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f1f5f9"), colors.white]),
                ]
            )
        )
        elements.append(gt)
        elements.append(Spacer(1, 16))

    # ── Footer note ────────────────────────────────────────────────────────
    elements.append(Spacer(1, 8))
    elements.append(
        Paragraph(
            "<font size='8' color='#94a3b8'>Generated by FairMind AI — "
            "Build with AI Solution Challenge 2026</font>",
            styles["Normal"],
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# ── NEW: generate PDF from request body ─────────────────────────────────────

@router.post("/report/generate")
async def generate_report(payload: dict = Body(...)):
    """
    Generate a PDF audit report from the audit data passed in the request body.
    Does NOT require Supabase — works purely from the in-memory results.

    Body: { "audit_data": { ...full audit results... } }
    """
    audit = payload.get("audit_data", {})
    audit_id = audit.get("audit_id", "unknown")

    if not audit:
        return JSONResponse(status_code=400, content={"error": "audit_data is required"})

    try:
        pdf_bytes = _build_pdf(audit, audit_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="fairmind_report_{str(audit_id)[:8]}.pdf"',
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"PDF generation failed: {str(e)}"})


# ── Existing: look up stored audit ──────────────────────────────────────────

@router.get("/report/{audit_id}")
async def get_report(audit_id: str, fmt: str = "json"):
    """
    Retrieve a full audit report by ID (from Supabase).
    Returns JSON or a downloadable PDF (fmt=download).
    """
    audit = await get_audit(audit_id)
    if not audit:
        return JSONResponse(status_code=404, content={"error": "Audit not found"})

    if fmt == "download":
        try:
            pdf_bytes = _build_pdf(audit, audit_id)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="fairmind_report_{audit_id[:8]}.pdf"',
                },
            )
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"PDF generation failed: {str(e)}"})

    return JSONResponse(content=audit)


@router.get("/reports")
async def list_recent_reports():
    """List the 20 most recent audits."""
    audits = await list_audits(limit=20)
    return JSONResponse(content={"audits": audits})
