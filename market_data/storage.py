import json
import os
from typing import List, Dict, Any
from market_data.config import get_data_path

def save_candles(symbol: str, interval: str, candles: List[Dict[str, Any]], append: bool = False):
    """
    Saves candles to a JSON file.
    
    Args:
        symbol: e.g., "BTCUSDT"
        interval: e.g., "1m"
        candles: List of candle dicts
        append: If True, appends to existing file. If False, overwrites.
    """
    file_path = get_data_path(symbol, interval)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    existing_candles = []
    
    if append and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if content:
                    existing_candles = json.loads(content)
        except Exception as e:
            print(f"Error reading existing file for append: {e}")

    # Deduplication logic
    existing_timestamps = {c['timestamp'] for c in existing_candles}
    
    new_candles_to_add = []
    for candle in candles:
        if candle['timestamp'] not in existing_timestamps:
            new_candles_to_add.append(candle)
            
    final_candles = existing_candles + new_candles_to_add
    
    # Sort by timestamp just in case
    final_candles.sort(key=lambda x: x['timestamp'])
    
    with open(file_path, 'w') as f:
        json.dump(final_candles, f, indent=None) # Compact JSON for space, or indent=2 for readability? User asked for JSON, usually implied for structure. I'll use compact for storage efficiency but standard json valid.

def load_candles(symbol: str, interval: str) -> List[Dict[str, Any]]:
    """
    Loads candles from a JSON file.
    
    Returns:
        List of dicts.
    """
    file_path = get_data_path(symbol, interval)
    if not os.path.exists(file_path):
        return []
        
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Error loading candles from JSON: {e}")
        return []
