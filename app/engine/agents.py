from abc import ABC, abstractmethod
from typing import List, Tuple
import pandas as pd
import numpy as np

from app.schemas import Candle, SignalType, AgentSignal
from app.engine.indicators import calculate_sma, calculate_rsi, calculate_macd, calculate_atr

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    def _candles_to_df(self, candles: List[Candle]) -> pd.DataFrame:
        data = [c.dict() for c in candles]
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df.sort_index()

    @abstractmethod
    def analyze(self, candles: List[Candle]) -> AgentSignal:
        pass

class TrendFollowingAgent(BaseAgent):
    def __init__(self):
        super().__init__("TrendFollowingAgent")

    def analyze(self, candles: List[Candle]) -> AgentSignal:
        df = self._candles_to_df(candles)
        if len(df) < 200:
             return AgentSignal(
                signal=SignalType.HOLD,
                confidence=0.0,
                agent_name=self.name,
                metadata={"reason": "Insufficient data for 200 SMA"}
            )

        # Strategy: Golden Cross / Death Cross
        sma_50 = calculate_sma(df['close'], 50).iloc[-1]
        sma_200 = calculate_sma(df['close'], 200).iloc[-1]
        
        # Calculate slope or recent trend strength for confidence
        # Simple heuristic: difference between MAs
        diff_pct = abs(sma_50 - sma_200) / sma_200
        confidence = min(0.5 + (diff_pct * 10), 0.95) # Base 0.5, scales with separation

        if sma_50 > sma_200:
            if diff_pct > 0.02: # Require 2% separation for strong signal
                signal = SignalType.BUY
                confidence = min(0.6 + (diff_pct * 10), 0.90)
                reasoning = f"Strong Golden Cross detected (SMA50 {sma_50:.2f} > SMA200 {sma_200:.2f}, Diff {diff_pct:.2%})"
            else:
                signal = SignalType.HOLD
                confidence = 0.3
                reasoning = f"Weak Golden Cross (SMA50 > SMA200), insufficient separation ({diff_pct:.2%})"

        elif sma_50 < sma_200:
            if diff_pct > 0.02: # Require 2% separation for strong signal
                signal = SignalType.SELL
                confidence = min(0.6 + (diff_pct * 10), 0.90)
                reasoning = f"Strong Death Cross detected (SMA50 {sma_50:.2f} < SMA200 {sma_200:.2f}, Diff {diff_pct:.2%})"
            else:
                signal = SignalType.HOLD
                confidence = 0.3
                reasoning = f"Weak Death Cross (SMA50 < SMA200), insufficient separation ({diff_pct:.2%})"
        else:
            signal = SignalType.HOLD
            confidence = 0.0
            reasoning = "SMA50 and SMA200 are effectively equal"

        return AgentSignal(
            signal=signal,
            confidence=round(confidence, 2),
            agent_name=self.name,
            metadata={
                "indicators_used": ["SMA50", "SMA200"],
                "reasoning": reasoning,
                "sma_50": sma_50,
                "sma_200": sma_200
            }
        )

class MomentumAgent(BaseAgent):
    def __init__(self):
        super().__init__("MomentumAgent")

    def analyze(self, candles: List[Candle]) -> AgentSignal:
        df = self._candles_to_df(candles)
        if len(df) < 30:
            return AgentSignal(
                signal=SignalType.HOLD,
                confidence=0.0,
                agent_name=self.name,
                metadata={"reason": "Insufficient data"}
            )

        rsi = calculate_rsi(df['close'], 14).iloc[-1]
        macd_df = calculate_macd(df['close'])
        macd_val = macd_df['macd'].iloc[-1]
        signal_val = macd_df['signal'].iloc[-1]

        # RSI Logic
        rsi_signal = SignalType.HOLD
        if rsi < 30: rsi_signal = SignalType.BUY
        elif rsi > 70: rsi_signal = SignalType.SELL
        
        # MACD Logic
        macd_signal = SignalType.HOLD
        if macd_val > signal_val: macd_signal = SignalType.BUY
        elif macd_val < signal_val: macd_signal = SignalType.SELL

        # Combine
        final_signal = SignalType.HOLD
        confidence = 0.5
        reason = []

        if rsi_signal == SignalType.BUY and macd_signal == SignalType.BUY:
            final_signal = SignalType.BUY
            confidence = 0.80
            reason.append("RSI oversold (<30) and MACD bullish")
        elif rsi_signal == SignalType.SELL and macd_signal == SignalType.SELL:
            final_signal = SignalType.SELL
            confidence = 0.80
            reason.append("RSI overbought (>70) and MACD bearish")
        elif rsi_signal == SignalType.BUY:
            final_signal = SignalType.HOLD # Downgrade single indicator
            confidence = 0.4
            reason.append("RSI oversold but MACD not confirming (Wait)")
        elif rsi_signal == SignalType.SELL:
            final_signal = SignalType.HOLD # Downgrade single indicator
            confidence = 0.4
            reason.append("RSI overbought but MACD not confirming (Wait)")
        elif macd_signal != SignalType.HOLD:
             # MACD only is weaker than RSI extremes
            final_signal = SignalType.HOLD # Prefer HOLD if only MACD
            confidence = 0.3
            reason.append(f"MACD {'Bullish' if macd_signal == SignalType.BUY else 'Bearish'} crossover (Unconfirmed by RSI)")
        else:
            reason.append("Momentum indicators neutral")

        return AgentSignal(
            signal=final_signal,
            confidence=round(confidence, 2),
            agent_name=self.name,
            metadata={
                "indicators_used": ["RSI", "MACD"],
                "reasoning": "; ".join(reason),
                "rsi": rsi,
                "macd": macd_val
            }
        )

class VolatilityAgent(BaseAgent):
    def __init__(self):
        super().__init__("VolatilityAgent")

    def analyze(self, candles: List[Candle]) -> AgentSignal:
        df = self._candles_to_df(candles)
        if len(df) < 20: # Bollinger bands
             return AgentSignal(
                signal=SignalType.HOLD,
                confidence=0.0,
                agent_name=self.name,
                metadata={"reason": "Insufficient data"}
            )
        
        # Bollinger Bands (Mean Reversion)
        sma_20 = calculate_sma(df['close'], 20)
        std_20 = df['close'].rolling(window=20).std()
        upper_band = sma_20 + (std_20 * 2)
        lower_band = sma_20 - (std_20 * 2)
        
        current_close = df['close'].iloc[-1]
        upper_val = upper_band.iloc[-1]
        lower_val = lower_band.iloc[-1]
        
        signal = SignalType.HOLD
        confidence = 0.5
        reason = "Within bands"

        if current_close > upper_val:
            signal = SignalType.SELL
            confidence = 0.6 # Lower confidence on blind mean reversion
            reason = f"Price {current_close:.2f} above Upper Band {upper_val:.2f} (Potential Overextension)"
        elif current_close < lower_val:
            signal = SignalType.BUY
            confidence = 0.6 # Lower confidence on blind mean reversion
            reason = f"Price {current_close:.2f} below Lower Band {lower_val:.2f} (Potential Oversold)"

        # Safety: If the move is extremely strong (e.g. Price > Bands by > 1%), prefer HOLD to avoid catching falling knife
        band_width = upper_val - lower_val
        if signal == SignalType.SELL and (current_close - upper_val) > (band_width * 0.1):
             signal = SignalType.HOLD
             confidence = 0.2
             reason += " - BUT momentum strong, waiting for confirmation"
        elif signal == SignalType.BUY and (lower_val - current_close) > (band_width * 0.1):
             signal = SignalType.HOLD
             confidence = 0.2
             reason += " - BUT momentum strong, waiting for confirmation"

        return AgentSignal(
            signal=signal,
            confidence=round(confidence, 2),
            agent_name=self.name,
            metadata={
                "indicators_used": ["Bollinger Bands"],
                "reasoning": reason,
                "upper_band": upper_val,
                "lower_band": lower_val
            }
        )
