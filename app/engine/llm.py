import os
import json
from typing import Optional, Dict, Any
from app.schemas import AnalysisResponse, SignalType

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMReasoner:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = None
        if self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        return self.client is not None

    def analyze(self, current_analysis: AnalysisResponse) -> AnalysisResponse:
        """
        Refines the rule-based analysis using OpenAI.
        """
        if not self.is_available():
            return current_analysis

        # Construct the prompt
        indicators_summary = json.dumps(current_analysis.indicators, indent=2)
        agents_summary = "\n".join([
            f"- {a.agent_name}: {a.signal} (Conf: {a.confidence}) - {a.metadata.get('reasoning', '')}" 
            for a in current_analysis.agent_signals
        ])

        system_prompt = (
            "You are a conservative AI Trading Risk Manager. "
            "Your goal is to validate trading signals for accuracy and safety. "
            "PRINCIPLES: \n"
            "1. PREFER 'HOLD' over risky 'BUY'/'SELL'. If agents conflict, choose HOLD.\n"
            "2. SAFETY FIRST. Do not endorse signals catching falling knives.\n"
            "3. EXPLAINABILITY. Briefly explain WHY the signal is chosen in simple terms."
        )

        user_prompt = (
            f"Review this market analysis for {current_analysis.symbol} ({current_analysis.timeframe}).\n\n"
            f"--- AGENT INPUTS ---\n{agents_summary}\n\n"
            f"--- TECHNICAL DATA ---\n{indicators_summary}\n\n"
            f"--- PROPOSED DECISION ---\n"
            f"Signal: {current_analysis.signal}\n"
            f"Confidence: {current_analysis.confidence}\n"
            f"Reasoning: {current_analysis.reasoning}\n\n"
            "INSTRUCTIONS:\n"
            "1. Evaluate if the proposed decision is supported by data. If agents are weak/conflicted, enforce HOLD.\n"
            "2. If the signal is BUY/SELL, ensure multiple indicators confirm it. If unsure, override to HOLD.\n"
            "3. Return JSON: { 'signal': 'BUY'|'SELL'|'HOLD', 'confidence': float(0.0-1.0), 'explanation': 'One sentence summary.' }"
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0, # Strict, deterministic
                max_tokens=150
            )
            
            content = response.choices[0].message.content
            if not content:
                print("LLM returned empty content.")
                return current_analysis

            llm_result = json.loads(content)
            
            # Update the analysis object
            # We preserve the original agents/indicators but override the final judgment
            updated_analysis = current_analysis.copy()
            
            signal_str = llm_result.get("signal", "HOLD").upper()
            if signal_str in ["BUY", "SELL", "HOLD"]:
                updated_analysis.signal = SignalType(signal_str)
            
            updated_analysis.confidence = float(llm_result.get("confidence", current_analysis.confidence))
            
            # Append LLM reasoning to existing reasoning
            llm_explanation = llm_result.get("explanation", "No explanation provided.")
            updated_analysis.reasoning = f"[AI REASONING]: {llm_explanation} | [ORIGINAL]: {current_analysis.reasoning}"
            
            return updated_analysis

        except Exception as e:
            print(f"LLM Analysis failed: {e}")
            return current_analysis
