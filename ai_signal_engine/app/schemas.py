from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class Candle(BaseModel):
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(..., ge=0)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentSignal(BaseModel):
    signal: SignalType
    confidence: float = Field(..., ge=0.0, le=1.0)
    agent_name: str
    metadata: Dict[str, Any] = {}

class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: str
    candles: List[Candle]

class AnalysisResponse(BaseModel):
    signal: SignalType
    confidence: float
    symbol: str
    timeframe: str
    reasoning: str
    agent_signals: List[AgentSignal]
    indicators: Dict[str, Any]
    timestamp: str
