import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env values (API key)
load_dotenv()

# === Project Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent
WALLET_INPUT_FILE = BASE_DIR / "data" / "wallets.xlsx"
RAW_TXN_DIR = BASE_DIR / "data" / "raw_transactions"
FEATURES_DIR = BASE_DIR / "data" / "features"
PROCESSED_FEATURES_DIR = BASE_DIR / "data" / "processed_features"
OUTPUT_FILE = BASE_DIR / "data" / "output" / "wallet_scores.csv"

# Ensure all required directories exist
for folder in [RAW_TXN_DIR, FEATURES_DIR, PROCESSED_FEATURES_DIR, OUTPUT_FILE.parent]:
    folder.mkdir(parents=True, exist_ok=True)

# === Etherscan Configuration ===
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_RATE_LIMIT = 4  # max 4 requests/sec for safety on free tier

# === Compound V2 Contracts (Ethereum) ===
COMPOUND_CONTROLLER = "0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b"
COMPOUND_V2_CONTRACTS = {
    COMPOUND_CONTROLLER.lower(): "Comptroller",
    "0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5": "cETH",
    "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643": "cDAI",
    "0x39aa39c021dfbae8fac545936693ac917d5e7563": "cUSDC",
    "0xf5dce57282a584d2746faf1593d3121fcac444dc": "cUSDT",
    "0x35a18000230da775cac24873d00ff85bccded550": "cUNI",
    "0xface851a4921ce59e912d19329929ce6da6eb0c7": "cWBTC",
    "0x158079ee67fce2f58472a96584a73c7ab9ac95c1": "cREP",
    "0x6c8c6b02e7b2be14d4fa6022dfd6d5c73a6ee621": "cBAT",
    "0x5b281a6dda0b271e91ae35de655ad301c976edb1": "cZRX",
    "0x7713dd9ca933848f6819f38b8352d9a15ea73f67": "cMKR",
    "0x95b4ef2869ebd94beb4eee400a99824bf5dc325b": "cYFI",
    "0x041171993284df560249b57358f931d9eb7b925d": "cFEI",
}
COMPOUND_V2_CONTRACTS = {k.lower(): v for k, v in COMPOUND_V2_CONTRACTS.items()}

# === Compound V3 Market Sync ===

# V3 Registry address (not currently exposed directly via Etherscan)
# We simulate discovery by loading known proxy contracts
COMPOUND_V3_FALLBACK_FILE = BASE_DIR / "data" / "compound_v3_markets.json"

def fetch_compound_v3_from_api() -> dict:
   # Fetch Compound V3 markets from a remote source.
   # This could be a maintained GitHub list, subgraph API, etc.
    try:
        # Example: Pull from GitHub maintained list or subgraph API
        # Placeholder below simulates that response
        response = {
            "ethereum": {
                "USDC": "0xc3d688b66703497daa19211eedff47f25384cdc3",
                "WETH": "0xa17581a9e3356d9a858b789d68b4d866e593a22f"
            },
            "arbitrum": {
                "USDC": "0x9eeb6e7c3d69e3ee58d97b6fb6f7a8c09b5d0ae6"
            }
        }
        # Save for local use
        with open(COMPOUND_V3_FALLBACK_FILE, "w") as f:
            json.dump(response, f, indent=2)
        return response
    except Exception as e:
        print(f"[WARN] Failed to fetch Compound V3 markets dynamically: {e}")
        return {}

def get_compound_v3_markets() -> dict:
    # Try to load from local cache first
    if COMPOUND_V3_FALLBACK_FILE.exists():
        try:
            with open(COMPOUND_V3_FALLBACK_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load V3 from cache: {e}")

    return fetch_compound_v3_from_api()
