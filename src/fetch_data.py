# src/fetch_data.py

import time
import requests
import pandas as pd
import json
from pathlib import Path
from src import config

def load_wallets_from_excel(file_path: Path) -> list:
    """
    Load wallet addresses from the Excel file.
    Assumes the wallet addresses are in the first column.
    """
    df = pd.read_excel(file_path)
    wallets = df.iloc[:, 0].dropna().unique().tolist()
    return wallets


def fetch_wallet_txns(wallet_address: str, api_key: str) -> dict:
    """
    Fetch transaction history for a given wallet using Etherscan API.
    Returns the full response as a Python dictionary.
    """
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


def save_txns_to_file(wallet_address: str, data: dict):
    """
    Save fetched transaction data as JSON in the raw_transactions folder.
    """
    output_path = config.RAW_TXN_DIR / f"{wallet_address}.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def fetch_all_wallets():
    """
    Main controller function to load wallets and fetch txns with rate-limiting.
    """
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
