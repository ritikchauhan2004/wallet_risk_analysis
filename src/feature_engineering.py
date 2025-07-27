import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime
from src import config

# Final output file
AGGREGATED_FEATURES_FILE = config.PROCESSED_FEATURES_DIR / "wallet_features.csv"
AGGREGATED_FEATURES_FILE.parent.mkdir(parents=True, exist_ok=True)

def unix_to_date(ts):
    return datetime.utcfromtimestamp(int(ts)).date()

def extract_features_from_wallet(wallet_file: Path) -> dict:
    df = pd.read_csv(wallet_file)
    action_counts = Counter(df["action"])
    total_txns = len(df)

    # BASIC FEATURES
    supply = action_counts.get("mint", 0) + action_counts.get("supply", 0)
    redeem = action_counts.get("redeem", 0) + action_counts.get("redeemUnderlying", 0) + action_counts.get("withdraw", 0)
    borrow = action_counts.get("borrow", 0)
    repay = action_counts.get("repayBorrow", 0) + action_counts.get("repayBorrowBehalf", 0) + action_counts.get("repay", 0)
    liquidation = action_counts.get("liquidateBorrow", 0) + action_counts.get("absorb", 0)

    repay_ratio = repay / borrow if borrow > 0 else 0
    net_borrow_score = borrow - repay
    supply_borrow_balance = supply / borrow if borrow > 0 else 0

    # ADVANCED FEATURES
    first_ts = df["timestamp"].min()
    last_ts = df["timestamp"].max()
    tx_span_days = (unix_to_date(last_ts) - unix_to_date(first_ts)).days or 1

    repay_consistency = repay / total_txns
    reborrow_rate = borrow / repay if repay > 0 else 0
    net_liquidation_ratio = liquidation / (borrow + repay) if (borrow + repay) > 0 else 0

    avg_gas = df["gas_used"].mean() if not df["gas_used"].isna().all() else 0

    # PROTOCOL VERSION (tags for analysis only)
    v2_keywords = {"mint", "redeem", "redeemUnderlying", "borrow", "repayBorrow", "repayBorrowBehalf", "liquidateBorrow"}
    v3_keywords = {"supply", "withdraw", "borrow", "repay", "absorb"}

    v2_used = any(a in v2_keywords for a in df["action"].unique())
    v3_used = any(a in v3_keywords for a in df["action"].unique())

    protocol_version = "both" if v2_used and v3_used else "v2" if v2_used else "v3"

    return {
        "wallet": wallet_file.stem,
        "total_txns": total_txns,
        "supply_count": supply,
        "redeem_count": redeem,
        "borrow_count": borrow,
        "repay_count": repay,
        "liquidation_count": liquidation,
        "borrow_repay_ratio": round(repay_ratio, 3),
        "net_borrow_score": net_borrow_score,
        "supply_borrow_balance": round(supply_borrow_balance, 3),

        # Advanced features
        "tx_activity_span_days": tx_span_days,
        "repay_consistency": round(repay_consistency, 3),
        "reborrow_rate": round(reborrow_rate, 3),
        "net_liquidation_ratio": round(net_liquidation_ratio, 3),
        "avg_gas_used": int(avg_gas),
        "protocol_version": protocol_version
    }

# Process all wallet CSV files and aggregate features
def process_all_wallets():
 
    all_features = []

    for csv_file in config.FEATURES_DIR.glob("*.csv"):
        try:
            features = extract_features_from_wallet(csv_file)
            all_features.append(features)
        except Exception as e:
            print(f"[!] Failed: {csv_file.name} - {e}")

    df_all = pd.DataFrame(all_features)
    df_all.to_csv(AGGREGATED_FEATURES_FILE, index=False)
    print(f"[✓] Saved {len(df_all)} wallet feature rows to: {AGGREGATED_FEATURES_FILE}")


if __name__ == "__main__":
    process_all_wallets()
