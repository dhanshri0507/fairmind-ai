import sys
sys.path.insert(0, '.')
from routers.report import _build_pdf

# Minimal audit payload matching what the frontend sends
audit = {
    "audit_id": "test-1234-abcd",
    "fairness_score": 81,
    "overall_bias_detected": True,
    "dataset_size": 500,
    "per_attribute": {
        "gender": {
            "demographic_parity_gap": 0.269,
            "equalized_odds_gap": 0.0,
            "bias_detected": True,
            "severity": "HIGH",
            "group_statistics": {
                "Male":   {"count": 260, "positive_rate": 0.62},
                "Female": {"count": 240, "positive_rate": 0.35},
            },
        },
        "race": {
            "demographic_parity_gap": 0.104,
            "equalized_odds_gap": 0.05,
            "bias_detected": True,
            "severity": "MEDIUM",
            "group_statistics": {
                "White": {"count": 200, "positive_rate": 0.6},
                "Black": {"count": 150, "positive_rate": 0.5},
                "Asian": {"count": 150, "positive_rate": 0.49},
            },
        },
    },
}

pdf_bytes = _build_pdf(audit, "test-1234-abcd")
with open("test_output_report.pdf", "wb") as f:
    f.write(pdf_bytes)

print(f"PDF generated successfully: {len(pdf_bytes)} bytes -> test_output_report.pdf")
