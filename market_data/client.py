import urllib.request
import json
import time
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional, Any
from market_data.config import BINANCE_BASE_URL, BINANCE_INTERVALS

def fetch_historical_data(symbol: str, interval: str, start_time: int, end_time: int) -> List[Dict[str, Any]]:
    """
    Fetches historical kline data from Binance using urllib.
    
    Args:
        symbol: e.g., "BTCUSDT"
        interval: e.g., "1m", "5m"
        start_time: Start timestamp in milliseconds
        end_time: End timestamp in milliseconds
        
    Returns:
        List of OHLCV dictionaries.
    """
    if interval not in BINANCE_INTERVALS:
        print(f"Warning: Interval {interval} not directly supported by Binance. Skipping fetch.")
        return []
    
    binance_interval = BINANCE_INTERVALS[interval]
    limit = 1000  # Binance max limit
    all_candles = []
    
    current_start = start_time
    
    while current_start < end_time:
        # Calculate safe end time for this chunk to avoid over-fetching usually handled by limit, 
        # but we use limit=1000 so we just request from current_start
        
        params = {
            "symbol": symbol,
            "interval": binance_interval,
            "startTime": current_start,
            "endTime": end_time,
            "limit": limit
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{BINANCE_BASE_URL}/klines?{query_string}"
        
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                
                if not data:
                    break
                    
                for kline in data:
                    # Binance kline format: 
                    # [0: Open Time, 1: Open, 2: High, 3: Low, 4: Close, 5: Volume, ...]
                    candle = {
                        "timestamp": int(kline[0]),
                        "open": float(kline[1]),
                        "high": float(kline[2]),
                        "low": float(kline[3]),
                        "close": float(kline[4]),
                        "volume": float(kline[5])
                    }
                    all_candles.append(candle)
                
                # Update current_start to the last timestamp + 1ms to avoid duplicates
                last_timestamp = all_candles[-1]["timestamp"]
                current_start = last_timestamp + 1
                
                # Rate limit safety
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error fetching data: {e}. Retrying in 2 seconds...")
            time.sleep(2)
            continue
            
    return all_candles
