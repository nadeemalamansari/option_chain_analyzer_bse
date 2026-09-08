"""Volume Analysis"""

import pandas as pd
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class VolumeAnalysisResult:
    total_ce_volume: int
    total_pe_volume: int
    volume_pcr: float
    high_volume_strikes: List[Dict]
    bias: str


class VolumeAnalyzer:
    """Analyze Volume data"""
    
    def analyze(self, df: pd.DataFrame, atm_strike: float) -> VolumeAnalysisResult:
        """Perform volume analysis"""
        
        total_ce_volume = int(df["VOLUME"].sum())
        total_pe_volume = int(df["VOLUME.1"].sum())
        volume_pcr = total_pe_volume / total_ce_volume if total_ce_volume > 0 else 0
        
        # Identify high volume strikes
        high_volume_strikes = self._get_high_volume_strikes(df)
        
        # Determine bias
        bias = self._determine_bias(volume_pcr, high_volume_strikes, atm_strike)
        
        return VolumeAnalysisResult(
            total_ce_volume=total_ce_volume,
            total_pe_volume=total_pe_volume,
            volume_pcr=volume_pcr,
            high_volume_strikes=high_volume_strikes,
            bias=bias
        )
    
    def _get_high_volume_strikes(self, df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """Get strikes with highest volume"""
        df_copy = df.copy()
        df_copy["total_volume"] = df_copy["VOLUME"] + df_copy["VOLUME.1"]
        
        top_strikes = df_copy.nlargest(top_n, "total_volume")
        
        result = []
        for _, row in top_strikes.iterrows():
            result.append({
                "strike": row["STRIKE PRICE"],
                "ce_volume": int(row["VOLUME"]),
                "pe_volume": int(row["VOLUME.1"]),
                "total_volume": int(row["total_volume"])
            })
        
        return result
    
    def _determine_bias(self, volume_pcr: float, high_volume_strikes: List[Dict], atm_strike: float) -> str:
        """Determine volume bias"""
        # Check if high volume is concentrated near ATM
        atm_volume = 0
        total_high_volume = 0
        
        for strike_data in high_volume_strikes:
            if abs(strike_data["strike"] - atm_strike) / atm_strike < 0.01:
                atm_volume = strike_data["total_volume"]
            total_high_volume += strike_data["total_volume"]
        
        # If high volume is near ATM, it's a neutral signal
        if total_high_volume > 0 and atm_volume / total_high_volume > 0.3:
            return "NEUTRAL"
        
        # Volume PCR bias
        if volume_pcr > 1.2:
            return "BEARISH"  # More put volume
        elif volume_pcr < 0.7:
            return "BULLISH"   # More call volume
        else:
            return "NEUTRAL"