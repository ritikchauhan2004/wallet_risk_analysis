import time
import requests
import pandas as pd
import json
from pathlib import Path
from src import config

# Load wallet addresses from an Excel file
def load_wallets_from_excel(file_path: Path) -> list:
    
    df = pd.read_excel(file_path)
    wallets = df.iloc[:, 0].dropna().unique().tolist()
    return wallets

# Fetch transaction data for a single wallet using Etherscan API
def fetch_wallet_txns(wallet_address: str, api_key: str) -> dict:
 
    url = config.ETHERSCAN_API_URL
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "1":
        print(f"[!] Failed or empty response for wallet {wallet_address}: {data.get('message')}")
    return data

# Save fetched transactions to a JSON file
def save_txns_to_file(wallet_address: str, data: dict):

    output_path = config.RAW_TXN_DIR / f"{wallet_address}.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

# Fetch transactions for all wallets and save to files
def fetch_all_wallets():
    wallets = load_wallets_from_excel(config.WALLET_INPUT_FILE)
    total = len(wallets)

    print(f"[i] Fetching transactions for {total} wallets...")
    for idx, wallet in enumerate(wallets):
        print(f"[{idx+1}/{total}] Fetching txns for {wallet}...")

        data = fetch_wallet_txns(wallet, config.ETHERSCAN_API_KEY)
        save_txns_to_file(wallet, data)

        # Rate limit: 5 req/sec => sleep 0.21s minimum per request
        time.sleep(0.22)


if __name__ == "__main__":
    fetch_all_wallets()
