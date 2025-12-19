import json
import sys
import pandas as pd
from app.engine.signal_engine import engine
from app.schemas import Candle

def test_engine():
    print("Loading sample request...")
    with open("data/sample_request.json", "r") as f:
        payload = json.load(f)
    
    candles_data = payload["candles"]
    candles = [Candle(**c) for c in candles_data]
    
    print(f"Loaded {len(candles)} candles.")
    
    print("Running analysis...")
    try:
        result = engine.analyze(candles, payload["symbol"], payload["timeframe"])
        print("\n=== ANALYSIS RESULT ===")
        print(f"Signal: {result.signal}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
        print("=======================")
        
        # Check explanation endpoint logic via engine cache
        cached = engine.get_latest_analysis()
        assert cached == result
        print("Cache verification passed.")
        
    except Exception as e:
        print(f"Analysis Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_engine()
