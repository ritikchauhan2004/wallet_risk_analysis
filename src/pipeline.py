import time
import subprocess

# --- STEP MODULES --- #
from src.fetch_data import fetch_all_wallets
from src.protocol_parser import parse_all_wallets
from src.feature_engineering import process_all_wallets
from src.scoring import score_wallets as score_all_wallets
from src.config import get_compound_v3_markets

def run_full_pipeline():
     
    print("🔁 STEP 0: Loading Compound V3 Markets...")
    v3 = get_compound_v3_markets()
    print(f"[i] Loaded {len(v3.get('ethereum', {}))} Compound V3 markets")

    print("🔁 STEP 1: Fetching transaction data...")
    fetch_all_wallets()

    print("\n🔍 STEP 2: Parsing Compound-specific txns...")
    parse_all_wallets()

    print("\n📊 STEP 3: Feature engineering...")
    process_all_wallets()

    print("\n🧠 STEP 4: Risk scoring...")
    score_all_wallets()

    print("\n✅ Pipeline complete! Check output CSV in: data/output/wallet_scores.csv")


if __name__ == "__main__":
    start = time.time()
    run_full_pipeline()
    print(f"\n⏱️ Total time: {round(time.time() - start, 2)} seconds")
