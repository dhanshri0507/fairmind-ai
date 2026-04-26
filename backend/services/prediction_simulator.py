import numpy as np
import pandas as pd

class PredictionSimulator:
    def __init__(self, bias_strength: float = 0.3, random_seed: int = 42):
        """
        bias_strength: Controls how unfair the model is (0.0 = perfectly fair, 1.0 = perfectly unfair).
        """
        self.bias_strength = bias_strength
        np.random.seed(random_seed)

    def predict(self, df: pd.DataFrame, target_col: str, protected_col: str, positive_label: str) -> np.ndarray:
        """
        Generates predictions that are biased against a protected group.
        """
        y_true = (df[target_col].astype(str) == str(positive_label)).astype(int)
        
        # Determine the protected group (the minority group, or simply anything not the majority)
        is_protected = df[protected_col].astype(str) != df[protected_col].astype(str).value_counts().idxmax()

        # Base prediction: start with some noise
        random_noise = np.random.rand(len(df))
        biased_predictions = y_true.astype(float) + (random_noise - 0.5) * 0.4

        # Apply bias: Lower the probability for the protected group
        bias_penalty = np.where(is_protected, -self.bias_strength, 0)
        final_prob = np.clip(biased_predictions + bias_penalty, 0, 1)

        # Convert to binary predictions
        return (final_prob > 0.5).astype(int)

    def mitigate_predictions(self, df: pd.DataFrame, protected_col: str, y_pred: np.ndarray) -> np.ndarray:
        """
        Applies a simulated mitigation: Improves recall for the protected group.
        """
        is_protected = df[protected_col].astype(str) != df[protected_col].astype(str).value_counts().idxmax()
        mitigated_predictions = y_pred.copy()

        # For the protected group, flip a certain percentage of negative predictions to positive.
        flip_rate = 0.2
        protected_negative_indices = np.where(is_protected & (y_pred == 0))[0]
        n_to_flip = int(len(protected_negative_indices) * flip_rate)
        
        if n_to_flip > 0:
            flip_indices = np.random.choice(protected_negative_indices, n_to_flip, replace=False)
            mitigated_predictions[flip_indices] = 1

        return mitigated_predictions
