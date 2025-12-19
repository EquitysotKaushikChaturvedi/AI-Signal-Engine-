# AI Signal Engine

## Overview
The **AI Signal Engine** is a modular, production-style trading backend designed to ingest market data, apply multiple technical strategies via independent agents, and generate a consolidated trading signal with clear explainability. It is built with **FastAPI** and **Python**, emphasizing separation of concerns, type safety, and extensibility.


## Architecture

The system follows a pipeline architecture:

1.  **API Layer**: Receives OHLCV candle data via REST.
2.  **Indicators Layer**: Pure functions calculating technical metrics (SMA, RSI, MACD, ATR, Bollinger Bands).
3.  **Agents Layer**: Independent logic units (Trend, Momentum, Volatility) that analyze data and output signals with confidence scores.
4.  **Aggregator**: Weighs agent outputs to form a consensus signal (BUY, SELL, HOLD) and synthesizes reasoning.
5.  **LLM Reasoner (OpenAI)**: *[Optional]* If an API Key is provided, GPT-4o reviews the aggregated signal and technical data to provide a final refined judgment and reasoning.

```
Request (Pydantic) -> SignalEngine -> Agents -> Aggregator -> [LLM Check] -> Response
```

### Key Components

-   `app/engine/indicators.py`: Stateless technical analysis math.
-   `app/engine/agents.py`: Strategy logic encapsulated in classes.
-   `app/engine/aggregator.py`: Weighted consensus logic.
-   `app/schemas.py`: Strict data contracts using Pydantic.

## Folder Structure Explained

Explanation of what every file and folder does.

### `app/` (The Main Application Folder)
This folder contains all the code that runs the AI Engine.

-   **`main.py`**: **The Entrance**. This is the starting point. It turns on the server so it can listen for questions (requests).
-   **`api.py`**: **The Receptionist**. It defines the "endpoints" (like `/analyze`) where people send data. It takes the request and passes it to the engine.
-   **`schemas.py`**: **The Rulebook**. It defines strict rules for data. For example, "A candle must have an Open, High, Low, and Close price."

### `app/engine/` (The Brain)
This is where the actual thinking happens.

-   **`signal_engine.py`**: **The Manager**. It coordinates everything. It takes data, gives it to the Agents, gets their answers, and gives them to the Aggregator.
-   **`agents.py`**: **The Analysts**. These are the smart bots.
    -   *TrendFollowingAgent*: Checks if the price is going up or down over time.
    -   *MomentumAgent*: Checks if the price is moving too fast (overbought/oversold).
    -   *VolatilityAgent*: Checks if the price is jumping around too much.
-   **`indicators.py`**: **The Calculator**. It does the math. It calculates averages (SMA), strength (RSI), and other technical numbers. It doesn't make decisions; it just does math.
-   **`aggregator.py`**: **The Judge**. It looks at what all the Agents said using a voting system. If one says BUY and another says SELL, the Judge decides the final answer (usually HOLD).

### `app/utils/` (Helpers)
-   **`helpers.py`**: **Tools**. Small helpful tools, like setting up the intricate logging system to track what the computer is doing.

### `data/` (Test Data)
-   **`sample_request.json`**: **Fake Data**. A file containing fake market history (Bitcoin prices) used to test if the engine works without needing real stock market connection.

### Other Files
-   **`requirements.txt`**: **Shopping List**. A list of all the Python libraries (like pandas, fastapi) that need to be installed for this code to work.
-   **`README.md`**: **The Manual**. The file you are reading right now!

## API Documentation

### POST `/analyze`
Analyzes a provided list of market candles.

**Request Body**:
```json
{
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "candles": [
    {
      "timestamp": "2023-10-01T00:00:00",
      "open": 50000,
      "high": 51000,
      "low": 49500,
      "close": 50500,
      "volume": 1200
    },
    ...
  ]
}
```

**Response**:
```json
{
  "signal": "BUY",
  "confidence": 0.85,
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "reasoning": "Consensus score: 0.85. Details: [TrendFollowingAgent]: Golden Cross detected... | [MomentumAgent]: RSI oversold...",
  "agent_signals": [...],
  "indicators": {...},
  "timestamp": "2023-10-27T10:00:00"
}
```

### GET `/signals/latest`
Target for polling. Returns the result of the last analysis performed.

### GET `/signals/explain`
Returns a dedicated explanation view of the latest signal.

## How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    Server runs at `http://127.0.0.1:8000`.

3.  **Test**:
    Use `curl` or Postman to send data to `/analyze`.

## Design Decisions

-   **Statelessness**: The engine does not maintain internal state of the market; it re-analyzes provided history. This ensures determinism and simplified scaling.
-   **Pydantic**: Used heavily for robust data validation.
-   **Modularity**: Adding a new strategy (e.g., "SentimentAgent") only requires extending `BaseAgent` and adding it to the `SignalEngine` list.
-   **No Database**: In-memory architecture fits the demo scope and reduces easy-to-break dependency chains.

## Limitations

-   **Memory**: Large datasets are processed in-memory (Pandas).
-   **Single Timeframe**: Logic assumes all candles belong to the requested timeframe.
-   **Demo Logic**: Strategies are standard textbook implementations, not optimized for alpha.

## OpenAI Integration (New)

This project now supports **OpenAI GPT-4o** to refine trading signals with advanced reasoning.

**How it works**:
-   The core engine calculates Buy/Sell/Hold based on math (Indicators).
-   If `OPENAI_API_KEY` is set, the engine sends the indicators and agent results to GPT-4o.
-   GPT-4o acts as a senior analyst: it reviews the data and can confirm or override the signal with a detailed explanation.

**To Enable**:
1.  Set the environment variable:
    -   Windows PowerShell: `$env:OPENAI_API_KEY="sk-..."`
    -   Linux/Mac: `export OPENAI_API_KEY="sk-..."`
2.  Restart the server.
3.  If no key is found, the system automatically falls back to standard rule-based mode.
