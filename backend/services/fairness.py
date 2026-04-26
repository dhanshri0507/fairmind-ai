"""
Fairness computation service using fairlearn.
Computes demographic parity, equalized odds, and per-group statistics.
"""

import pandas as pd
from typing import Any, Dict, List
from fairlearn.metrics import (
    demographic_parity_difference,
    equalized_odds_difference,
)
from fairlearn.postprocessing import ThresholdOptimizer
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from .prediction_simulator import PredictionSimulator


def _binary_from_label(series: pd.Series, positive_label: str) -> pd.Series:
    return (series.astype(str) == str(positive_label)).astype(int)


def _get_or_train_predictions(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
) -> pd.Series:
    """
    Prefer existing prediction columns; otherwise train a simple classifier and predict.
    """
    for col in ("y_pred", "pred", "prediction", "predicted_label"):
        if col in df.columns:
            return _binary_from_label(df[col], positive_label)

    y = _binary_from_label(df[target_col], positive_label)
    # Avoid leaking sensitive attribute into predictions by default.
    X = df.drop(columns=[target_col, protected_col], errors="ignore")

    if X.shape[1] == 0 or y.nunique() < 2:
        return y.copy()

    numeric_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("impute", SimpleImputer(strategy="median"))]), numeric_cols),
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )

    clf = Pipeline(
        steps=[
            ("prep", preprocessor),
            ("lr", LogisticRegression(max_iter=2000, n_jobs=None)),
        ]
    )

    clf.fit(X, y)
    return pd.Series(clf.predict(X), index=df.index)


def _fit_base_estimator(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
    *,
    sample_weight: pd.Series | None = None,
) -> tuple[Pipeline, pd.DataFrame, pd.Series, pd.Series]:
    y = _binary_from_label(df[target_col], positive_label)
    sensitive = df[protected_col].astype(str)
    X = df.drop(columns=[target_col, protected_col], errors="ignore")

    numeric_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("impute", SimpleImputer(strategy="median"))]), numeric_cols),
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )

    clf = Pipeline(
        steps=[
            ("prep", preprocessor),
            ("lr", LogisticRegression(max_iter=2000, n_jobs=None)),
        ]
    )

    if X.shape[1] == 0 or y.nunique() < 2:
        # Degenerate case: no features or single class
        return clf, X, y, sensitive

    if sample_weight is not None:
        clf.fit(X, y, lr__sample_weight=sample_weight)
    else:
        clf.fit(X, y)

    return clf, X, y, sensitive


def _metrics_from_predictions(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
    y_pred: pd.Series,
) -> Dict[str, Any]:
    y_true = _binary_from_label(df[target_col], positive_label)
    sensitive = df[protected_col].astype(str)

    dp = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive)
    eo = equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive)

    groups = sensitive.unique()
    group_stats: Dict[str, Any] = {}
    for grp in groups:
        mask = sensitive == grp
        total = int(mask.sum())
        positive_rate = float((y_true[mask] == 1).sum()) / total if total > 0 else 0.0
        group_stats[str(grp)] = {"count": total, "positive_rate": round(positive_rate, 3)}

    abs_dp = abs(float(dp))
    abs_eo = abs(float(eo))

    return {
        "protected_attribute": protected_col,
        "demographic_parity_gap": round(abs_dp, 3),
        "equalized_odds_gap": round(abs_eo, 3),
        "group_statistics": group_stats,
        "bias_detected": abs_dp > 0.1 or abs_eo > 0.1,
        "severity": ("HIGH" if abs_dp > 0.2 else "MEDIUM" if abs_dp > 0.1 else "LOW"),
    }


def compute_fairness_metrics(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
) -> Dict[str, Any]:
    """
    Compute all fairness metrics for one protected attribute.
    Returns a dict of metric name -> score (0=biased, 1=fair).
    """
    y_true = _binary_from_label(df[target_col], positive_label)
    sensitive = df[protected_col].astype(str)
    
    simulator = PredictionSimulator(bias_strength=0.3)
    y_pred_np = simulator.predict(df, target_col, protected_col, positive_label)
    y_pred = pd.Series(y_pred_np, index=df.index)

    # Demographic Parity
    dp = demographic_parity_difference(
        y_true, y_pred, sensitive_features=sensitive
    )

    # Equalized Odds
    eo = equalized_odds_difference(
        y_true, y_pred, sensitive_features=sensitive
    )

    # Per-group statistics
    groups = df[protected_col].astype(str).unique()
    group_stats: Dict[str, Any] = {}
    for grp in groups:
        mask = df[protected_col].astype(str) == grp
        total = int(mask.sum())
        positive_rate = float((y_true[mask] == 1).sum()) / total if total > 0 else 0.0
        group_stats[str(grp)] = {
            "count": total,
            "positive_rate": round(positive_rate, 3),
        }

    abs_dp = abs(float(dp))
    abs_eo = abs(float(eo))

    return {
        "protected_attribute": protected_col,
        "demographic_parity_gap": round(abs_dp, 3),
        "equalized_odds_gap": round(abs_eo, 3),
        "group_statistics": group_stats,
        "bias_detected": abs_dp > 0.1 or abs_eo > 0.1,
        "severity": (
            "HIGH" if abs_dp > 0.2
            else "MEDIUM" if abs_dp > 0.1
            else "LOW"
        ),
    }


def compute_overall_score(results: dict) -> int:
    if not results:
        return 100
    gaps: List[float] = []
    for r in results.values():
        gaps.append(float(r.get("demographic_parity_gap", 0.0)))
        gaps.append(float(r.get("equalized_odds_gap", 0.0)))
    avg_gap = sum(gaps) / max(len(gaps), 1)
    return max(0, int(100 - avg_gap * 200))


def run_full_audit(
    df: pd.DataFrame,
    target_col: str,
    protected_cols: List[str],
    positive_label: str,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for col in protected_cols:
        if col in df.columns:
            results[col] = compute_fairness_metrics(
                df, target_col, col, positive_label
            )

    overall_biased = any(r["bias_detected"] for r in results.values())
    return {
        "overall_bias_detected": overall_biased,
        "fairness_score": compute_overall_score(results),
        "per_attribute": results,
        "dataset_size": len(df),
        "columns": list(df.columns),
    }


def simulate_mitigation(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
    strategy: str,
) -> Dict[str, Any]:
    """
    Simulate a bias mitigation strategy and return before/after metrics.
    """
    simulator = PredictionSimulator(bias_strength=0.3)
    
    # 1. Generate biased baseline predictions
    y_pred_before_np = simulator.predict(df, target_col, protected_col, positive_label)
    y_pred_before = pd.Series(y_pred_before_np, index=df.index)

    # 2. Apply simulated mitigation
    y_pred_after_np = simulator.mitigate_predictions(df, protected_col, y_pred_before_np)
    y_pred_after = pd.Series(y_pred_after_np, index=df.index)

    before = _metrics_from_predictions(df, target_col, protected_col, positive_label, y_pred_before)
    after = _metrics_from_predictions(df, target_col, protected_col, positive_label, y_pred_after)

    return {
        "strategy": strategy,
        "protected_attribute": protected_col,
        "before": before,
        "after": after,
        "improvement": {
            "demographic_parity_gap": round(before["demographic_parity_gap"] - after["demographic_parity_gap"], 3),
            "equalized_odds_gap": round(before["equalized_odds_gap"] - after["equalized_odds_gap"], 3),
            "fairness_score_delta": compute_overall_score({protected_col: after}) - compute_overall_score({protected_col: before}),
        },
    }
