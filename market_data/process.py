import time
import urllib.request
import json
from typing import List, Dict, Any, Optional
from market_data.config import TIMEFRAMES, MIN_CANDLES_REQUIRED, BINANCE_BASE_URL, BINANCE_INTERVALS

def get_latest_candle(symbol: str, interval: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the single latest candle from Binance to check for closure.
    """
    if interval not in BINANCE_INTERVALS:
        return None
        
    binance_interval = BINANCE_INTERVALS[interval]
    url = f"{BINANCE_BASE_URL}/klines?symbol={symbol}&interval={binance_interval}&limit=1"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if not data:
                return None
            
            kline = data[0]
            # [0: Open Time, ..., 4: Close, ..., 6: Close Time]
            return {
                "timestamp": int(kline[0]),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": int(kline[6])
            }
    except Exception as e:
        print(f"Error fetching latest candle: {e}")
        return None

def should_predict(candle: Dict[str, Any]) -> bool:
    """
    Determines if we should predict based on the candle state.
    Prediction happens ONLY when the candle is closed.
    
    In a live loop, we usually check if the current time > close_time.
    However, Binance's 'latest' candle is usually the OPEN one.
    To be safe, we look for 'previous' candle closure.
    
    Strategy:
    We fetch 1 candle. If it's the *same* candle we saw last time, we wait.
    If it's a NEW candle, it means the previous one closed.
    
    But to support the 'candle closed' check strictly:
    We can fetch the last 2 candles. If the 2nd to last one is new, we use it.
    """
    # Simple timestamp check: if current time > close_time, it is closed.
    current_time = int(time.time() * 1000)
    if current_time > candle.get("close_time", float('inf')):
        return True
    return False

def validate_minimum_candles(candles: List[Dict[str, Any]], interval: str) -> bool:
    """
    Checks if we have enough historical data to make a safe prediction.
    """
    min_required = MIN_CANDLES_REQUIRED.get(interval, 50)
    if len(candles) < min_required:
        print(f"Insufficient data: Have {len(candles)}, require {min_required} for {interval}")
        return False
    return True
