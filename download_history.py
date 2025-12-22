import argparse
import time
from datetime import datetime, timedelta
from market_data.client import fetch_historical_data
from market_data.storage import save_candles

def main():
    parser = argparse.ArgumentParser(description="Download Historical Data from Binance")
    parser.add_argument("--symbol", type=str, required=True, help="Trading Pair (e.g., BTCUSDT)")
    parser.add_argument("--interval", type=str, required=True, help="Timeframe (e.g., 1m, 5m, 1h)")
    parser.add_argument("--days", type=int, default=365, help="Number of days of history to download")
    
    args = parser.parse_args()
    
    symbol = args.symbol
    interval = args.interval
    days = args.days
    
    print(f"--- Starting Download: {symbol} [{interval}] for {days} days ---")
    
    end_time = int(time.time() * 1000)
    start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
    
    print(f"Time Range: {datetime.fromtimestamp(start_time/1000)} to {datetime.fromtimestamp(end_time/1000)}")
    
    candles = fetch_historical_data(symbol, interval, start_time, end_time)
    
    if candles:
        print(f"Downloaded {len(candles)} candles.")
        save_candles(symbol, interval, candles, append=False)
        print(f"Saved to data/{symbol}/{interval}.json")
    else:
        print("No data downloaded.")

if __name__ == "__main__":
    main()
