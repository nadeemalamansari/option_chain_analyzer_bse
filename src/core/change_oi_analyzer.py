"""Change in Open Interest Analysis"""

import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ChangeOIAnalysisResult:
    total_ce_chg_oi: int
    total_pe_chg_oi: int
    change_oi_pcr: float
    bias: str
    buildup_bias: str
    call_buildup: Dict = field(default_factory=dict)
    put_buildup: Dict = field(default_factory=dict)


class ChangeOIAnalyzer:
    """Analyze Change in Open Interest"""
    
    def analyze(self, df: pd.DataFrame, atm_strike: float) -> ChangeOIAnalysisResult:
        """Perform Change OI analysis"""
        
        total_ce_chg_oi = int(df["Chg in OI"].sum())
        total_pe_chg_oi = int(df["Chg in OI.1"].sum())
        change_oi_pcr = total_pe_chg_oi / total_ce_chg_oi if total_ce_chg_oi != 0 else 0
        
        # Detect buildup patterns
        call_buildup = self._detect_buildup(df, "call")
        put_buildup = self._detect_buildup(df, "put")
        
        # Determine biases
        bias = self._determine_bias(change_oi_pcr)
        buildup_bias = self._determine_buildup_bias(call_buildup, put_buildup)
        
        return ChangeOIAnalysisResult(
            total_ce_chg_oi=total_ce_chg_oi,
            total_pe_chg_oi=total_pe_chg_oi,
            change_oi_pcr=change_oi_pcr,
            bias=bias,
            buildup_bias=buildup_bias,
            call_buildup=call_buildup,
            put_buildup=put_buildup
        )
    
    def _detect_buildup(self, df: pd.DataFrame, side: str) -> Dict:
        """Detect buildup patterns for call or put side"""
        if side == "call":
            oi_col = "OI"
            chg_oi_col = "Chg in OI"
            price_col = "LTP"
        else:
            oi_col = "OI.1"
            chg_oi_col = "Chg in OI.1"
            price_col = "LTP.1"
        
        result = {
            "long_buildup": [],
            "short_buildup": [],
            "long_unwinding": [],
            "short_covering": []
        }
        
        for _, row in df.iterrows():
            oi_change = row.get(chg_oi_col, 0)
            price_change = row.get(price_col, 0)
            
            if abs(oi_change) < 10 or abs(price_change) < 0.5:
                continue
            
            if price_change > 0 and oi_change > 0:
                result["long_buildup"].append(float(row["STRIKE PRICE"]))
            elif price_change < 0 and oi_change > 0:
                result["short_buildup"].append(float(row["STRIKE PRICE"]))
            elif price_change < 0 and oi_change < 0:
                result["long_unwinding"].append(float(row["STRIKE PRICE"]))
            elif price_change > 0 and oi_change < 0:
                result["short_covering"].append(float(row["STRIKE PRICE"]))
        
        return result
    
    def _determine_bias(self, change_oi_pcr: float) -> str:
        """Determine Change OI bias"""
        if change_oi_pcr < 0.4:
            return "BEARISH"
        elif change_oi_pcr > 0.8:
            return "BULLISH"
        else:
            return "NEUTRAL"
    
    def _determine_buildup_bias(self, call_buildup: Dict, put_buildup: Dict) -> str:
        """Determine buildup bias"""
        call_short = len(call_buildup.get("short_buildup", []))
        put_short = len(put_buildup.get("short_buildup", []))
        call_long = len(call_buildup.get("long_buildup", []))
        put_long = len(put_buildup.get("long_buildup", []))
        
        if call_short > put_short + 3:
            return "BEARISH"
        elif put_short > call_short + 3:
            return "BULLISH"
        elif call_long > put_long + 3:
            return "BULLISH"
        elif put_long > call_long + 3:
            return "BEARISH"
        else:
            return "NEUTRAL"