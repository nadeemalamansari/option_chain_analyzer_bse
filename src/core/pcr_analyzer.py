"""Put-Call Ratio Analysis"""

import pandas as pd
from dataclasses import dataclass


@dataclass
class PCRAnalysisResult:
    oi_pcr: float
    change_oi_pcr: float
    volume_pcr: float
    bias: str


class PCRAnalyzer:
    """Analyze Put-Call Ratio"""
    
    def analyze(self, df: pd.DataFrame) -> PCRAnalysisResult:
        """Perform PCR analysis"""
        
        # Calculate OI PCR
        total_ce_oi = df["OI"].sum()
        total_pe_oi = df["OI.1"].sum()
        oi_pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        
        # Calculate Change OI PCR
        total_ce_chg_oi = df["Chg in OI"].sum()
        total_pe_chg_oi = df["Chg in OI.1"].sum()
        change_oi_pcr = total_pe_chg_oi / total_ce_chg_oi if total_ce_chg_oi != 0 else 0
        
        # Calculate Volume PCR
        total_ce_volume = df["VOLUME"].sum()
        total_pe_volume = df["VOLUME.1"].sum()
        volume_pcr = total_pe_volume / total_ce_volume if total_ce_volume > 0 else 0
        
        # Determine bias
        bias = self._determine_bias(oi_pcr, change_oi_pcr)
        
        return PCRAnalysisResult(
            oi_pcr=oi_pcr,
            change_oi_pcr=change_oi_pcr,
            volume_pcr=volume_pcr,
            bias=bias
        )
    
    def _determine_bias(self, oi_pcr: float, change_oi_pcr: float) -> str:
        """Determine PCR bias"""
        # Standard PCR ranges
        # > 0.7 = Bearish (too much put protection)
        # < 0.4 = Bullish (too much call optimism)
        # 0.4 - 0.7 = Neutral
        
        if change_oi_pcr > 0:
            if oi_pcr > 0.7:
                return "BEARISH"
            elif oi_pcr < 0.4:
                return "BULLISH"
        
        if oi_pcr > 0.7:
            return "BEARISH"
        elif oi_pcr < 0.4:
            return "BULLISH"
        else:
            return "NEUTRAL"