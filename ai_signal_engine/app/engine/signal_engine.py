from datetime import datetime
from typing import List, Optional
from app.schemas import Candle, AnalysisResponse
from app.engine.agents import TrendFollowingAgent, MomentumAgent, VolatilityAgent
from app.engine.aggregator import SignalAggregator
from app.engine.llm import LLMReasoner

class SignalEngine:
    def __init__(self):
        self.agents = [
            TrendFollowingAgent(),
            MomentumAgent(),
            VolatilityAgent()
        ]
        self.aggregator = SignalAggregator()
        self.llm = LLMReasoner()
        self._latest_analysis: Optional[AnalysisResponse] = None

    def analyze(self, candles: List[Candle], symbol: str, timeframe: str) -> AnalysisResponse:
        """
        Orchestrates the analysis process: 
        Agents -> Aggregator -> (Optional) LLM Reasoning -> Result
        """
        agent_signals = []
        
        # Run each agent
        for agent in self.agents:
            try:
                sig = agent.analyze(candles)
                agent_signals.append(sig)
            except Exception as e:
                # Log error in production, distinct from crashing
                # For now just skip this agent or return error signal
                print(f"Agent {agent.name} failed: {e}")
                
        # Aggregate (Rule-Based)
        result = self.aggregator.aggregate(agent_signals, symbol, timeframe)
        
        # Refine with LLM if available
        if self.llm.is_available():
            result = self.llm.analyze(result)
        
        # Timestamp
        result.timestamp = datetime.utcnow().isoformat()
        
        # Cache outcome (stateless, except for this latest-view requirement)
        self._latest_analysis = result
        
        return result

    def get_latest_analysis(self) -> Optional[AnalysisResponse]:
        return self._latest_analysis

# Global Instance
engine = SignalEngine()
