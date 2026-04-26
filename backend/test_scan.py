import requests, json

with open('sample_data.csv', 'rb') as f:
    resp = requests.post(
        'http://localhost:8000/api/scan',
        files={'file': ('sample_data.csv', f, 'text/csv')},
        data={
            'target_column': 'loan_approved',
            'protected_attributes': 'gender,race',
            'positive_label': '1',
        },
        timeout=30,
    )

r = resp.json()
print('Status:', resp.status_code)
print('Fairness Score:', r.get('fairness_score'))
print('Bias Detected:', r.get('overall_bias_detected'))
audit_id = r.get('audit_id', '')
print('Audit ID:', audit_id[:16])
for attr, data in r.get('per_attribute', {}).items():
    dp = data["demographic_parity_gap"]
    eo = data["equalized_odds_gap"]
    sev = data["severity"]
    print(f'  [{attr}] DP={dp}  EO={eo}  Severity={sev}')

print('\nFull JSON (truncated):')
print(json.dumps(r, indent=2)[:800])
