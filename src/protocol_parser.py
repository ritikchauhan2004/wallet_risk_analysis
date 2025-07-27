import json
from pathlib import Path
from src.config import (
    RAW_TXN_DIR,
    FEATURES_DIR,
    COMPOUND_V2_CONTRACTS,
    get_compound_v3_markets
)
import pandas as pd

# --- V2 Method Map ---
METHOD_MAP_V2 = {
    "0xa0712d68": "borrow",
    "0x3e1d2167": "repayBorrow",
    "0x4e4d9fea": "repayBorrowBehalf",
    "0x93e84d7f": "mint",
    "0xdb006a75": "redeem",
    "0x852a12e3": "redeemUnderlying",
    "0x6ef9d8dc": "liquidateBorrow",
    "0x3b4da69f": "enterMarkets"
}

# --- V3 Method Map ---
METHOD_MAP_V3 = {
    "0x3df02124": "supply",
    "0xb760faf9": "withdraw",
    "0x4c9f059f": "borrow",
    "0x854eb6c9": "repay",
    "0x61b9c6be": "absorb",
    "0x5e1eb6a8": "buyCollateral"
}

# Load V3 market addresses dynamically
V3_MARKETS = get_compound_v3_markets()
V3_ETH_CONTRACTS = set(market.lower() for market in V3_MARKETS.get("ethereum", {}).values())

# Extract action from a transaction
def extract_action(tx: dict) -> str:

    to_address = tx["to"].lower()
    input_sig = tx["input"][:10]

    # Check V2
    if to_address in COMPOUND_V2_CONTRACTS and input_sig in METHOD_MAP_V2:
        return METHOD_MAP_V2[input_sig]

    # Check V3
    if to_address in V3_ETH_CONTRACTS and input_sig in METHOD_MAP_V3:
        return METHOD_MAP_V3[input_sig]

    return None


# Parse transactions for a single wallet
def parse_wallet_transactions(wallet_address: str):

    input_file = RAW_TXN_DIR / f"{wallet_address}.json"
    output_file = FEATURES_DIR / f"{wallet_address}.csv"

    with open(input_file, "r") as f:
        data = json.load(f)

    txns = data.get("result", [])
    relevant_rows = []

    for tx in txns:
        action = extract_action(tx)
        if action:
            row = {
                "hash": tx["hash"],
                "timestamp": int(tx["timeStamp"]),
                "block_number": int(tx["blockNumber"]),
                "from": tx["from"],
                "to": tx["to"],
                "value": int(tx["value"]),
                "input": tx["input"],
                "gas_used": int(tx["gasUsed"]),
                "action": action
            }
            relevant_rows.append(row)

    if relevant_rows:
        df = pd.DataFrame(relevant_rows)
        df.to_csv(output_file, index=False)
        print(f"[+] Parsed Compound txns: {wallet_address} → {output_file.name}")
    else:
        print(f"[-] No Compound txns found for {wallet_address} (txs: {len(txns)})")

# Parse all wallets in the raw transactions directory
def parse_all_wallets():

    for json_file in RAW_TXN_DIR.glob("*.json"):
        wallet_address = json_file.stem
        parse_wallet_transactions(wallet_address)


if __name__ == "__main__":
    parse_all_wallets()
