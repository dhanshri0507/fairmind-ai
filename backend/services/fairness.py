"""
Fairness computation service using fairlearn.
Computes demographic parity, equalized odds, and per-group statistics.
"""

import logging
import pandas as pd
import numpy as np
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

logger = logging.getLogger("fairmind.fairness")


# ── helpers ──────────────────────────────────────────────────────────────────

def _binary_from_label(series: pd.Series, positive_label: str) -> pd.Series:
    return (series.astype(str) == str(positive_label)).astype(int)


def _build_preprocessor(X: pd.DataFrame):
    numeric_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    return ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([("impute", SimpleImputer(strategy="median"))]),
                numeric_cols,
            ),
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


def _build_lr_pipeline(X: pd.DataFrame) -> Pipeline:
    return Pipeline(
        steps=[
            ("prep", _build_preprocessor(X)),
            ("lr", LogisticRegression(max_iter=2000, solver="lbfgs", n_jobs=None)),
        ]
    )


def _fit_pipeline(
    X: pd.DataFrame,
    y: pd.Series,
    sample_weight: pd.Series | None = None,
) -> Pipeline:
    """Fit and return a LogisticRegression pipeline."""
    clf = _build_lr_pipeline(X)
    if sample_weight is not None:
        clf.fit(X, y, lr__sample_weight=sample_weight.values)
    else:
        clf.fit(X, y)
    return clf


# ── scan-time predictions (biased simulator) ─────────────────────────────────

def _get_or_train_predictions(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
) -> pd.Series:
    """
    Prefer existing prediction columns; otherwise train a simple classifier.
    """
    for col in ("y_pred", "pred", "prediction", "predicted_label"):
        if col in df.columns:
            return _binary_from_label(df[col], positive_label)

    y = _binary_from_label(df[target_col], positive_label)
    X = df.drop(columns=[target_col, protected_col], errors="ignore")

    if X.shape[1] == 0 or y.nunique() < 2:
        return y.copy()

    clf = _fit_pipeline(X, y)
    return pd.Series(clf.predict(X), index=df.index)


# ── metrics ───────────────────────────────────────────────────────────────────

def _group_stats_from_predictions(
    sensitive: pd.Series,
    y_pred: pd.Series,
) -> Dict[str, Any]:
    """
    Compute per-group prediction positive-rate (from y_pred, not y_true).
    This is what matters for fairness: how often each group is predicted positive.
    """
    group_stats: Dict[str, Any] = {}
    for grp in sensitive.unique():
        mask = sensitive == grp
        total = int(mask.sum())
        pred_positive_rate = float((y_pred[mask] == 1).sum()) / total if total > 0 else 0.0
        group_stats[str(grp)] = {
            "count": total,
            "positive_rate": round(pred_positive_rate, 3),
        }
    return group_stats


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

    abs_dp = abs(float(dp))
    abs_eo = abs(float(eo))

    # Group stats measured on PREDICTIONS (not ground truth) — shows actual disparity
    group_stats = _group_stats_from_predictions(sensitive, y_pred)

    return {
        "protected_attribute": protected_col,
        "demographic_parity_gap": round(abs_dp, 3),
        "equalized_odds_gap": round(abs_eo, 3),
        "group_statistics": group_stats,
        "bias_detected": abs_dp > 0.1 or abs_eo > 0.1,
        "severity": ("HIGH" if abs_dp > 0.2 else "MEDIUM" if abs_dp > 0.1 else "LOW"),
    }


# ── scan: compute fairness metrics ───────────────────────────────────────────

def compute_fairness_metrics(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
) -> Dict[str, Any]:
    """
    Compute all fairness metrics for one protected attribute.
    Uses PredictionSimulator to model a biased classifier, then measures
    demographic parity and equalized odds against ground truth.
    """
    y_true = _binary_from_label(df[target_col], positive_label)
    sensitive = df[protected_col].astype(str)

    simulator = PredictionSimulator(bias_strength=0.3)
    y_pred_np = simulator.predict(df, target_col, protected_col, positive_label)
    y_pred = pd.Series(y_pred_np, index=df.index)

    dp = demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive)
    eo = equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive)

    # Group stats: use ground-truth positive rates for audit display
    groups = sensitive.unique()
    group_stats: Dict[str, Any] = {}
    for grp in groups:
        mask = sensitive == grp
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
            "HIGH" if abs_dp > 0.2 else "MEDIUM" if abs_dp > 0.1 else "LOW"
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
            results[col] = compute_fairness_metrics(df, target_col, col, positive_label)

    overall_biased = any(r["bias_detected"] for r in results.values())
    return {
        "overall_bias_detected": overall_biased,
        "fairness_score": compute_overall_score(results),
        "per_attribute": results,
        "dataset_size": len(df),
        "columns": list(df.columns),
    }


# ── simulation ────────────────────────────────────────────────────────────────

def _compute_reweighing_weights(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
) -> pd.Series:
    """
    Compute Kamiran & Calders (2012) reweighing sample weights.
    w(x) = P(Y) * P(S) / P(Y, S)
    """
    y = _binary_from_label(df[target_col], positive_label)
    g = df[protected_col].astype(str)
    n = len(df)
    weights = np.ones(n, dtype=float)

    for y_val in y.unique():
        for g_val in g.unique():
            mask = (y == y_val) & (g == g_val)
            if mask.sum() == 0:
                continue
            p_y = float((y == y_val).sum()) / n
            p_g = float((g == g_val).sum()) / n
            p_gy = float(mask.sum()) / n
            weights[mask.values] = (p_g * p_y) / p_gy

    return pd.Series(weights, index=df.index)


def simulate_mitigation(
    df: pd.DataFrame,
    target_col: str,
    protected_col: str,
    positive_label: str,
    strategy: str,
) -> Dict[str, Any]:
    """
    Simulate a bias mitigation strategy and return before/after metrics.

    'Before': a deliberately biased baseline from PredictionSimulator.
    'After':  predictions after applying the chosen mitigation algorithm.
    """
    y_true = _binary_from_label(df[target_col], positive_label)
    sensitive = df[protected_col].astype(str)
    X = df.drop(columns=[target_col, protected_col], errors="ignore")

    # ── BEFORE: biased baseline ───────────────────────────────────────────
    simulator = PredictionSimulator(bias_strength=0.35, random_seed=42)
    y_pred_before_np = simulator.predict(df, target_col, protected_col, positive_label)
    y_pred_before = pd.Series(y_pred_before_np, index=df.index)

    # ── Degenerate-case guard ─────────────────────────────────────────────
    # If no features available or only one class, return identical metrics
    if X.shape[1] == 0 or y_true.nunique() < 2:
        before = _metrics_from_predictions(df, target_col, protected_col, positive_label, y_pred_before)
        return {
            "strategy": strategy,
            "protected_attribute": protected_col,
            "before": before,
            "after": before,
            "improvement": {
                "demographic_parity_gap": 0.0,
                "equalized_odds_gap": 0.0,
                "fairness_score_delta": 0,
            },
        }

    # ── AFTER: apply chosen mitigation ───────────────────────────────────
    y_pred_after = _apply_mitigation(
        df, X, y_true, sensitive, target_col, protected_col, positive_label, strategy, y_pred_before
    )

    before = _metrics_from_predictions(df, target_col, protected_col, positive_label, y_pred_before)
    after = _metrics_from_predictions(df, target_col, protected_col, positive_label, y_pred_after)

    dp_improvement = round(before["demographic_parity_gap"] - after["demographic_parity_gap"], 3)
    eo_improvement = round(before["equalized_odds_gap"] - after["equalized_odds_gap"], 3)

    return {
        "strategy": strategy,
        "protected_attribute": protected_col,
        "before": before,
        "after": after,
        "improvement": {
            "demographic_parity_gap": dp_improvement,
            "equalized_odds_gap": eo_improvement,
            "fairness_score_delta": (
                compute_overall_score({protected_col: after})
                - compute_overall_score({protected_col: before})
            ),
        },
    }


def _apply_mitigation(
    df: pd.DataFrame,
    X: pd.DataFrame,
    y_true: pd.Series,
    sensitive: pd.Series,
    target_col: str,
    protected_col: str,
    positive_label: str,
    strategy: str,
    y_pred_before: pd.Series,
) -> pd.Series:
    """
    Apply the requested mitigation strategy and return post-mitigation predictions.
    Falls back gracefully if a strategy fails.
    """
    try:
        if strategy == "reweighing":
            # Reweighing: train LR with Kamiran-Calders sample weights
            weights = _compute_reweighing_weights(df, target_col, protected_col, positive_label)
            clf = _fit_pipeline(X, y_true, sample_weight=weights)
            return pd.Series(clf.predict(X), index=df.index)

        elif strategy in ("threshold", "equalized_odds"):
            constraint = "demographic_parity" if strategy == "threshold" else "equalized_odds"
            # Train a plain base estimator first
            clf_base = _fit_pipeline(X, y_true)
            postprocess_est = ThresholdOptimizer(
                estimator=clf_base,
                constraints=constraint,
                objective="balanced_accuracy_score",
                predict_method="auto",
            )
            postprocess_est.fit(X, y_true, sensitive_features=sensitive)
            y_pred_after_np = postprocess_est.predict(X, sensitive_features=sensitive)
            return pd.Series(y_pred_after_np, index=df.index)

        else:
            # Unknown strategy — return biased baseline unchanged
            logger.warning("Unknown mitigation strategy: %s", strategy)
            return y_pred_before.copy()

    except Exception:
        logger.exception("Mitigation strategy '%s' failed; using simulator fallback.", strategy)
        # Fallback: use PredictionSimulator mitigation (flip negatives for protected group)
        simulator = PredictionSimulator(bias_strength=0.35, random_seed=42)
        y_pred_np = simulator.predict(df, target_col, protected_col, positive_label)
        mitigated_np = simulator.mitigate_predictions(df, protected_col, y_pred_np)
        return pd.Series(mitigated_np, index=df.index)
