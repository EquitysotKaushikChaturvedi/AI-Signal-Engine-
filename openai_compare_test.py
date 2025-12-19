import requests
import datetime
import sys

# Configuration
SYMBOL = "BTCUSDT"
INTERVAL = "5m"
LIMIT = 220
API_URL = "http://127.0.0.1:8000/analyze"
BINANCE_REST_URL = "https://api.binance.com/api/v3/klines"

def parse_candle(c):
    return {
        "timestamp": datetime.datetime.fromtimestamp(c[0] / 1000).isoformat(),
        "open": float(c[1]),
        "high": float(c[2]),
        "low": float(c[3]),
        "close": float(c[4]),
        "volume": float(c[5])
    }

def main():
    print("Fetching snapshot from Binance REST API...")
    try:
        params = {"symbol": SYMBOL, "interval": INTERVAL, "limit": LIMIT}
        resp = requests.get(BINANCE_REST_URL, params=params)
        resp.raise_for_status()
        candles = [parse_candle(c) for c in resp.json()]
        print(f"Fetched {len(candles)} candles.")
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

    print("Sending to AI Engine...")
    payload = {
        "symbol": f"{SYMBOL} (Snapshot)",
        "timeframe": INTERVAL,
        "candles": candles
    }
    
    try:
        resp = requests.post(API_URL, json=payload)
        resp.raise_for_status()
        result = resp.json()
        
        print("\n=== AI RESULT ===")
        print(f"Signal: {result.get('signal')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Reasoning: {result.get('reasoning')[:200]}...") # Trimmed
        print("=================\n")
        
    except Exception as e:
        print(f"AI Request Failed: {e}")

if __name__ == "__main__":
    main()
