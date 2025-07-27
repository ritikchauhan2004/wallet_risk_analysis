# src/scoring.py

import pandas as pd
import numpy as np
from scipy.stats import rankdata
from src import config

INPUT_FEATURES_FILE = config.PROCESSED_FEATURES_DIR / "wallet_features.csv"
OUTPUT_FILE = config.OUTPUT_FILE

def normalize_rank(series, ascending=True):
    """
    Converts a series into percentile rank [0, 1].
    Lower is riskier if ascending=True.
    """
    ranks = rankdata(series, method='average')
    if not ascending:
        ranks = len(series) - ranks + 1
    return (ranks - 1) / (len(series) - 1)


def score_wallets():
    df = pd.read_csv(INPUT_FEATURES_FILE)

    # Define scoring direction: True = safe is higher
    feature_weights = {
        "repay_consistency": (0.20, True),
        "borrow_repay_ratio": (0.20, True),
        "supply_borrow_balance": (0.15, True),
        "tx_activity_span_days": (0.10, True),
        "net_borrow_score": (0.10, False),
        "net_liquidation_ratio": (0.20, False),
        "reborrow_rate": (0.05, False),
    }

    score_col = np.zeros(len(df))

    for feature, (weight, safe_high) in feature_weights.items():
        if feature not in df.columns:
            continue
        norm_scores = normalize_rank(df[feature], ascending=safe_high)
        score_col += norm_scores * weight * 1000

    # Round and clamp
    df["score"] = score_col.round().astype(int).clip(0, 1000)
    df[["wallet", "score"]].to_csv(OUTPUT_FILE, index=False)
    print(f"[✓] Score distribution saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    score_wallets()
