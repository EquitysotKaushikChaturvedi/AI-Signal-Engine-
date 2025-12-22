from typing import List
from collections import defaultdict
from app.schemas import AgentSignal, AnalysisResponse, SignalType, Candle

class SignalAggregator:
    def aggregate(self, agent_signals: List[AgentSignal], symbol: str, timeframe: str) -> AnalysisResponse:
        
        # Weighted Consensus Logic
        # BUY = 1, SELL = -1, HOLD = 0
        score = 0.0
        total_weight = 0.0
        
        # Reasoning accumulation
        consolidated_reasoning = []
        indicators_all = {}
        
        for ag in agent_signals:
            weight = ag.confidence
            
            # Map signal to value
            val = 0
            if ag.signal == SignalType.BUY:
                val = 1
            elif ag.signal == SignalType.SELL:
                val = -1
            
            score += val * weight
            total_weight += weight
            
            # Collect metadata
            if "reasoning" in ag.metadata:
                consolidated_reasoning.append(f"[{ag.agent_name}]: {ag.metadata['reasoning']}")
            
            # Flatten indicators for the summary
            # (In a real app, this might be more structured)
            indicators_all[ag.agent_name] = ag.metadata
            
        # Normalize score (-1 to 1)
        # Avoid division by zero
        normalized_score = score / total_weight if total_weight > 0 else 0
        
        # Determine final signal
        final_signal = SignalType.HOLD
        final_confidence = abs(normalized_score)
        
        if normalized_score >= 0.4: # Higher threshold (was 0.25)
            final_signal = SignalType.BUY
        elif normalized_score <= -0.4: # Higher threshold (was -0.25)
            final_signal = SignalType.SELL
            
        # Human readable summary
        summary_text = f"Final Signal: {final_signal}. "
        if final_signal == SignalType.HOLD:
             summary_text += f"No strong consensus (Score: {normalized_score:.2f}). Agents conflicting or signals weak."
        else:
             summary_text += f"Strong consensus achieved (Score: {normalized_score:.2f})."

        return AnalysisResponse(
            signal=final_signal,
            confidence=round(final_confidence, 2),
            symbol=symbol,
            timeframe=timeframe,
            reasoning=summary_text + " Details: " + " | ".join(consolidated_reasoning),
            agent_signals=agent_signals,
            indicators=indicators_all,
            timestamp="" # Populated by caller or API
        )
