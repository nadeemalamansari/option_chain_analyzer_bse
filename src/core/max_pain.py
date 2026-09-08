"""Max Pain Calculator"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class MaxPainResult:
    max_pain_strike: float
    bias: str = "NEUTRAL"
    pain_values: Dict[float, float] = None


class MaxPainCalculator:
    """Calculate Max Pain for option chain"""
    
    def calculate(self, df: pd.DataFrame) -> MaxPainResult:
        """Calculate Max Pain strike"""
        
        if df.empty:
            return MaxPainResult(0, "NEUTRAL", {})
        
        strikes = df["STRIKE PRICE"].unique()
        strikes = sorted([s for s in strikes if s > 0])
        
        if len(strikes) < 2:
            return MaxPainResult(0, "NEUTRAL", {})
        
        pain_values = {}
        
        for strike in strikes:
            pain = self._calculate_pain_at_strike(df, strike)
            pain_values[strike] = pain
        
        if not pain_values:
            return MaxPainResult(0, "NEUTRAL", {})
        
        max_pain_strike = min(pain_values, key=pain_values.get)
        
        return MaxPainResult(
            max_pain_strike=max_pain_strike,
            bias="NEUTRAL",
            pain_values=pain_values
        )
    
    def _calculate_pain_at_strike(self, df: pd.DataFrame, target_strike: float) -> float:
        """Calculate total pain at a given strike"""
        total_pain = 0
        
        for _, row in df.iterrows():
            strike = row["STRIKE PRICE"]
            ce_oi = row.get("OI", 0)
            pe_oi = row.get("OI.1", 0)
            
            if strike < target_strike:
                ce_pain = ce_oi * (target_strike - strike)
            else:
                ce_pain = 0
            
            if strike > target_strike:
                pe_pain = pe_oi * (strike - target_strike)
            else:
                pe_pain = 0
            
            total_pain += ce_pain + pe_pain
        
        return total_pain