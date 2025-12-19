import json
import random
from datetime import datetime, timedelta
import os

def generate_full_request(n=300):
    candles = []
    price = 100.0
    time = datetime.utcnow() - timedelta(days=n)
    
    for _ in range(n):
        change = random.uniform(-2, 2)
        open_p = price
        close_p = price + change
        high_p = max(open_p, close_p) + random.uniform(0, 1)
        low_p = min(open_p, close_p) - random.uniform(0, 1)
        volume = random.uniform(1000, 5000)
        
        candles.append({
            "timestamp": time.isoformat(),
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": round(volume, 2)
        })
        
        price = close_p
        time += timedelta(days=1)
        
    return {
        "symbol": "BTC/USD",
        "timeframe": "1d",
        "candles": candles
    }

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    data = generate_full_request()
    with open("data/sample_request.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Generated data/sample_request.json")
