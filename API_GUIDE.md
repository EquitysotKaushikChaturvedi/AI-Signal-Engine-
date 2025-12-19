# API Guide: The `/analyze` Endpoint

The `/analyze` endpoint is the **heart** of the AI Signal Engine. It is the single entry point where you send market data to get a trading decision.

## 1. What is it?
It is a **REST POST data endpoint**.
-   **Input**: You give it a list of past price candles (Open, High, Low, Close).
-   **Output**: It gives you a trading signal (BUY, SELL, HOLD) and a confidence score.

## 2. Why use it?
The AI engine is **stateless**. It doesn't remember the past. To make a decision right *now*, it needs you to send it the history leading up to *now*.
This design makes the engine extremely reliable and testable. You can send it data from 2020 or 2025, and it will analyze it purely based on the numbers you provide.

## 3. How to use it

### Endpoint URL
`POST http://127.0.0.1:8000/analyze`

### Request Format (JSON)
You must send a JSON object with `symbol`, `timeframe`, and a list of `candles`.

```json
{
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "candles": [
    {
      "timestamp": "2024-01-01T00:00:00",
      "open": 50000.0,
      "high": 51000.0,
      "low": 49000.0,
      "close": 50500.0,
      "volume": 1000.0
    },
    ... (send at least 50-100 candles for best results)
  ]
}
```

### Response Format (JSON)
The engine returns its analysis.

```json
{
  "signal": "BUY",              // The decision: BUY, SELL, or HOLD
  "confidence": 0.85,           // How sure is it? (0.00 to 1.00)
  "reasoning": "Trend is UP...",// Explanation of why
  "timestamp": "..."            // Time of analysis
}
```

## 4. Example Use Cases
-   **Live Trading**: Your bot fetches live data from Binance/Coinbase, formats it into this JSON list, sends it to `/analyze`, and places a trade based on the response.
-   **Backtesting**: You send historical data from last year to see how the AI *would have* performed.
-   **Testing**: You manually send a fake "perfect uptrend" pattern to see if the AI detects it correctly.
