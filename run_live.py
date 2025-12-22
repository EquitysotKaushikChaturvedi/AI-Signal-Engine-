import time
import argparse
import urllib.request
import json
from market_data.storage import load_candles, save_candles
from market_data.process import get_latest_candle, validate_minimum_candles
from market_data.config import TIMEFRAMES
from datetime import datetime

# Local API Endpoint
API_URL = "http://localhost:8000/analyze"

def post_analyze(candles, symbol, timeframe):
    """
    Sends the candle data to the AI engine for analysis.
    """
    payload = {
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": candles
    }
    
    try:
        req = urllib.request.Request(
            API_URL, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result
    except Exception as e:
        print(f"API Error: {e}")
        return None

def run_live(symbol, interval):
    print(f"--- Starting Safe Mode Live Prediction: {symbol} [{interval}] ---")
    
    # 1. Load History
    history = load_candles(symbol, interval)
    if not history:
        print("No historical data found! Please run download_history.py first.")
        return

    print(f"Loaded {len(history)} historical candles.")
    
    # Track last processed candle timestamp to avoid duplicates
    last_processed_time = history[-1]['timestamp']
    
    while True:
        try:
            # 2. Fetch Latest Candle
            # We strictly want COMPLETED candles.
            # Binance API result: if we ask for limit=1, it gives specific latest.
            # Strategy: poll every few seconds. If a NEW candle appears that has a timestamp
            # greater than our `last_processed_time` AND it is considered 'closed' (based on time)
            # then we proceed.
            
            # Actually, to be safe and simple:
            # We fetch the LAST 2 candles.
            # If the 2nd to last candle (index 0) has a timestamp > last_processed_time,
            # it means it has definitely closed because a new one (index 1) has started.
            
            # Re-implementing fetch here slightly differently for this logic
            binance_interval = interval # Assuming valid mapping exists or is same
            from market_data.config import BINANCE_INTERVALS
            b_interval = BINANCE_INTERVALS.get(interval)
            
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={b_interval}&limit=2"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                
                # Check the closed candle (the one before the currently open one, index 0)
                closed_kline = data[0]
                closed_ts = int(closed_kline[0])
                
                if closed_ts > last_processed_time:
                    # found a new CLOSED candle
                    new_candle = {
                        "timestamp": closed_ts,
                        "open": float(closed_kline[1]),
                        "high": float(closed_kline[2]),
                        "low": float(closed_kline[3]),
                        "close": float(closed_kline[4]),
                        "volume": float(closed_kline[5])
                    }
                    
                    # print(f"\n[NEW CANDLE] {datetime.fromtimestamp(closed_ts/1000)}")
                    
                    # 3. Append & Save
                    history.append(new_candle)
                    save_candles(symbol, interval, [new_candle], append=True)
                    last_processed_time = closed_ts
                    
                    # 4. Validate
                    if validate_minimum_candles(history, interval):
                        # 5. Predict
                        print("Sending to AI Engine...")
                        # Limit context to last 1000 to avoid huge payloads
                        prediction = post_analyze(history[-1000:], symbol, interval)
                        
                        if prediction:
                            t_str = datetime.fromtimestamp(closed_ts/1000).strftime('%Y-%m-%d %H:%M:%S')
                            print(f"Candle closed: {new_candle['close']} -> AI Signal: {prediction.get('signal')} ({prediction.get('confidence')}) | {symbol} | {t_str}")
                    else:
                        print("Skipping prediction: Insufficient data.")
                        
                else:
                    # unique visual heartbeat
                    print(".", end="", flush=True)
            
            # Sleep to respect rate limits and avoid busy loop
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\nStopping Live Mode.")
            break
        except Exception as e:
            print(f"\nError in loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, default="BTCUSDT")
    parser.add_argument("--interval", type=str, default="1m")
    args = parser.parse_args()
    
    run_live(args.symbol, args.interval)
