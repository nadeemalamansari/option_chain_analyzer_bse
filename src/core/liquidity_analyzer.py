"""Liquidity Analysis"""

import pandas as pd
from typing import Dict
from dataclasses import dataclass


@dataclass
class LiquidityResult:
    bid_ask_spread: float
    volume_ratio: float
    active_strikes_ratio: float
    liquidity_score: float
    bias: str


class LiquidityAnalyzer:
    """Analyze Liquidity in option chain"""
    
    def analyze(self, df: pd.DataFrame) -> LiquidityResult:
        """Perform liquidity analysis"""
        
        # Calculate average bid-ask spread
        spreads = []
        for _, row in df.iterrows():
            ce_spread = row.get("ASK PRICE", 0) - row.get("BID PRICE", 0)
            pe_spread = row.get("ASK PRICE.1", 0) - row.get("BID PRICE.1", 0)
            if ce_spread > 0:
                spreads.append(ce_spread)
            if pe_spread > 0:
                spreads.append(pe_spread)
        
        avg_spread = sum(spreads) / len(spreads) if spreads else 0
        
        # Calculate active strikes ratio
        total_strikes = len(df)
        active_ce = (df["OI"] > 0).sum()
        active_pe = (df["OI.1"] > 0).sum()
        active_ratio = (active_ce + active_pe) / (2 * total_strikes) if total_strikes > 0 else 0
        
        # Volume ratio
        total_ce_vol = df["VOLUME"].sum()
        total_pe_vol = df["VOLUME.1"].sum()
        vol_ratio = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 0
        
        # Liquidity score (0-100)
        spread_score = max(0, 100 - avg_spread * 10)  # Lower spread = higher score
        active_score = active_ratio * 100
        volume_score = min(100, (total_ce_vol + total_pe_vol) / 10000)
        
        liquidity_score = (spread_score * 0.3 + active_score * 0.4 + volume_score * 0.3)
        
        # Determine bias
        if liquidity_score > 70:
            bias = "BULLISH"  # Good liquidity = easier trading
        elif liquidity_score < 40:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"
        
        return LiquidityResult(
            bid_ask_spread=avg_spread,
            volume_ratio=vol_ratio,
            active_strikes_ratio=active_ratio,
            liquidity_score=liquidity_score,
            bias=bias
        )