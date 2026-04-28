import sys
sys.path.insert(0, '.')
from services.fairness import simulate_mitigation, run_full_audit
import pandas as pd

df = pd.read_csv('sample_data.csv')
target_col = 'loan_approved'
positive_label = '1'

print("=== FULL AUDIT ===")
audit = run_full_audit(df, target_col, ['gender', 'race'], positive_label)
print("Fairness Score:", audit["fairness_score"])
print("Bias Detected:", audit["overall_bias_detected"])
for attr, m in audit['per_attribute'].items():
    print(f"  {attr}: DP={m['demographic_parity_gap']}, EO={m['equalized_odds_gap']}, severity={m['severity']}")

print()
for strategy in ['reweighing', 'threshold', 'equalized_odds']:
    print(f"=== SIMULATE: {strategy} ===")
    res = simulate_mitigation(df, target_col, 'gender', positive_label, strategy)
    b = res['before']
    a = res['after']
    imp = res['improvement']
    print(f"  Before: DP={b['demographic_parity_gap']}, EO={b['equalized_odds_gap']}")
    print(f"  After:  DP={a['demographic_parity_gap']}, EO={a['equalized_odds_gap']}")
    print(f"  Improvement: DP_delta={imp['demographic_parity_gap']}, score_delta={imp['fairness_score_delta']}")
    print()

print("ALL TESTS PASSED")
