import json
import requests
import websocket
import datetime
import sys

# Configuration
SYMBOL_LOWER = "btcusdt"
SYMBOL_UPPER = "BTCUSDT"
INTERVAL = "5m"
LIMIT = 220
API_URL = "http://127.0.0.1:8000/analyze"
BINANCE_REST_URL = "https://api.binance.com/api/v3/klines"
BINANCE_WS_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL_LOWER}@kline_{INTERVAL}"

# Global buffer for candles
candles_buffer = []

def parse_rest_candle(c):
    # Binance REST format: [Open time, Open, High, Low, Close, Volume, Close time, ...]
    return {
        "timestamp": datetime.datetime.fromtimestamp(c[0] / 1000).isoformat(),
        "open": float(c[1]),
        "high": float(c[2]),
        "low": float(c[3]),
        "close": float(c[4]),
        "volume": float(c[5])
    }

def fetch_rest_history():
    print(f"Fetching {LIMIT} historical candles from Binance REST API...")
    params = {
        "symbol": SYMBOL_UPPER,
        "interval": INTERVAL,
        "limit": LIMIT
    }
    try:
        resp = requests.get(BINANCE_REST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        chk = [parse_rest_candle(c) for c in data]
        print(f"Loaded {len(chk)} candles.")
        return chk
    except Exception as e:
        print(f"Error fetching REST data: {e}")
        sys.exit(1)

def send_to_ai(candles):
    payload = {
        "symbol": f"{SYMBOL_UPPER} (Binance Live)",
        "timeframe": INTERVAL,
        "candles": candles
    }
    try:
        resp = requests.post(API_URL, json=payload)
        resp.raise_for_status()
        result = resp.json()
        return result
    except Exception as e:
        print(f"AI Engine Request Failed: {e}")
        return None

def on_message(ws, message):
    global candles_buffer
    data = json.loads(message)
    k = data['k']
    
    # Check if candle is closed
    if k['x']:
        closed_price = float(k['c'])
        print(f"Candle closed at {closed_price}. Updating buffer...")
        
        # New candle object
        new_candle = {
            "timestamp": datetime.datetime.fromtimestamp(k['t'] / 1000).isoformat(),
            "open": float(k['o']),
            "high": float(k['h']),
            "low": float(k['l']),
            "close": float(k['c']),
            "volume": float(k['v'])
        }
        
        # Update buffer: Remove oldest, add new
        candles_buffer.pop(0)
        candles_buffer.append(new_candle)
        
        # Analyze
        result = send_to_ai(candles_buffer)
        if result:
            print(f"Candle Closed: {closed_price} -> AI Signal: {result.get('signal')} ({result.get('confidence')})")
        else:
            print("Failed to get AI signal.")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed.")

def on_open(ws):
    print(f"Connected to Binance WebSocket: {BINANCE_WS_URL}")
    print("Waiting for candle close event (x=true)...")

def main():
    global candles_buffer
    
    # 1. Bootstrap via REST
    candles_buffer = fetch_rest_history()
    
    # 2. Initial Analysis
    print("Running initial analysis...")
    result = send_to_ai(candles_buffer)
    if result:
        print(f"Initial State -> AI Signal: {result.get('signal')} ({result.get('confidence')})")
    
    # 3. Start Stream
    ws = websocket.WebSocketApp(
        BINANCE_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
