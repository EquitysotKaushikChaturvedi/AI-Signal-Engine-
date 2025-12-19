# Live Usage Guide: AI Signal Engine with Binance Data

This guide explains how to run the AI engine using **Real-Time Market Data** from Binance.

## 1. Start the AI Server (Required)
The AI Brain must be running to receive data.

1.  Open a terminal in the project folder:
    ```powershell
    cd "d:\AI-Driven Trading Signal Web App\ai_signal_engine"
    ```
2.  Start the server:
    ```powershell
    uvicorn app.main:app --reload
    ```
    *Keep this terminal open.*

## 2. Run Live Data Streaming
This script connects to Binance WebSocket and sends candles to your local AI server every 5 minutes.

1.  Open a **NEW** terminal window.
2.  Activate your environment (if needed):
    ```powershell
    & "d:/AI-Driven Trading Signal Web App/.venv/Scripts/Activate.ps1"
    ```
3.  Run the live test script:
    ```powershell
    python binance_ws_test.py
    ```

**What you will see:**
-   **Startup**: It fetches the last 220 candles immediately and prints the AI's first signal.
-   **Updates**: Every time a 5-minute candle closes (e.g., 12:00, 12:05, 12:10), a new line will appear:
    ```text
    Candle Closed: 87125.95 -> AI Signal: HOLD (0.02)
    ```

## 3. (Optional) OpenAI Comparison
If you want to see how OpenAI changes the *explanation* (Reasoning) without affecting the decision:

1.  **Stop** the server (`Ctrl+C` in Terminal 1).
2.  **Set the Key**:
    ```powershell
    $env:OPENAI_API_KEY="sk-your-key-here"
    ```
3.  **Restart** the server:
    ```powershell
    uvicorn app.main:app --reload
    ```
4.  Run the comparison script:
    ```powershell
    python openai_compare_test.py
    ```
    *Result*: The "Signal" will match your previous tests, but "Reasoning" will be detailed and human-like.

## troubleshooting
-   **WebSocket Closed / Error**: Public internet streams sometimes disconnect. Just run `python binance_ws_test.py` again.
-   **Module Not Found**: If you see this, run:
    ```powershell
    & "d:/AI-Driven Trading Signal Web App/.venv/Scripts/python.exe" -m pip install requests websocket-client
    ```
