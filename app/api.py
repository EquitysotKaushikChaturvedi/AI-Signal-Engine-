from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.schemas import AnalysisRequest, AnalysisResponse, Candle, SignalType
from app.engine.signal_engine import engine

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Signal Engine"}

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_market(request: AnalysisRequest):
    """
    Analyzes list of candles and returns a trading signal.
    """
    if not request.candles:
         raise HTTPException(status_code=400, detail="No candle data provided")
    
    # Sort candles by timestamp just in case
    sorted_candles = sorted(request.candles, key=lambda c: c.timestamp)
    
    response = engine.analyze(
        candles=sorted_candles, 
        symbol=request.symbol, 
        timeframe=request.timeframe
    )
    return response

@router.get("/signals/latest", response_model=AnalysisResponse)
def get_latest_signal():
    """
    Returns the latest generated signal from memory.
    """
    latest = engine.get_latest_analysis()
    if not latest:
        raise HTTPException(status_code=404, detail="No analysis performed yet")
    return latest

@router.get("/signals/explain")
def explain_signal():
    """
    Returns detailed explanation of the latest signal.
    """
    latest = engine.get_latest_analysis()
    if not latest:
        raise HTTPException(status_code=404, detail="No analysis performed yet")
    
    return {
        "signal": latest.signal,
        "confidence": latest.confidence,
        "reasoning": latest.reasoning,
        "agents": [
            {
                "name": agent.agent_name,
                "signal": agent.signal,
                "reason": agent.metadata.get("reasoning", "N/A")
            }
            for agent in latest.agent_signals
        ]
    }
