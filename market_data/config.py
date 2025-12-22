import os

# Base directory for storing market data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Binance Public API Base URL
BINANCE_BASE_URL = "https://api.binance.com/api/v3"

# Supported Timeframes and their minute equivalents
TIMEFRAMES = {
    "1m": 1,
    "5m": 5,
    "10m": 10,  # Note: 10m is not standard in Binance, requires aggregation or limitation
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
    "1w": 10080,
}

# Binance API Interval Mapping (Binance does not support 10m natively)
BINANCE_INTERVALS = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "1w": "1w",
}

# Minimum candles required for safe prediction
MIN_CANDLES_REQUIRED = {
    "1m": 500,
    "5m": 300,
    "10m": 200,
    "1h": 200,
    "1d": 50,
    "1w": 20,
}

def get_data_path(symbol: str, interval: str) -> str:
    """Returns the absolute path to the CSV file for a given symbol and interval."""
    symbol_dir = os.path.join(DATA_DIR, symbol)
    if not os.path.exists(symbol_dir):
        os.makedirs(symbol_dir)
    return os.path.join(symbol_dir, f"{interval}.json")
