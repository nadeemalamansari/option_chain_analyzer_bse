"""Open Interest Analysis"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class OIAnalysisResult:
    total_ce_oi: int
    total_pe_oi: int
    oi_pcr: float
    highest_ce_oi_strike: float
    highest_pe_oi_strike: float
    atm_data: Optional[object]
    bias: str


@dataclass
class ATMData:
    strike: float
    ce_oi: int
    pe_oi: int
    ce_chg_oi: int
    pe_chg_oi: int
    ce_volume: int
    pe_volume: int
    ce_ltp: float
    pe_ltp: float
    ce_iv: float
    pe_iv: float


class OIAnalyzer:
    """Analyze Open Interest data"""
    
    def analyze(self, df: pd.DataFrame, atm_strike: float) -> OIAnalysisResult:
        """Perform OI analysis"""
        
        # Calculate totals
        total_ce_oi = int(df["OI"].sum())
        total_pe_oi = int(df["OI.1"].sum())
        oi_pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        
        # Find highest OI strikes
        highest_ce_idx = df["OI"].idxmax() if df["OI"].max() > 0 else None
        highest_pe_idx = df["OI.1"].idxmax() if df["OI.1"].max() > 0 else None
        
        highest_ce_oi_strike = df.loc[highest_ce_idx, "STRIKE PRICE"] if highest_ce_idx is not None else 0
        highest_pe_oi_strike = df.loc[highest_pe_idx, "STRIKE PRICE"] if highest_pe_idx is not None else 0
        
        # Get ATM data
        atm_data = self._get_atm_data(df, atm_strike)
        
        # Determine bias
        bias = self._determine_bias(total_ce_oi, total_pe_oi, atm_data)
        
        return OIAnalysisResult(
            total_ce_oi=total_ce_oi,
            total_pe_oi=total_pe_oi,
            oi_pcr=oi_pcr,
            highest_ce_oi_strike=highest_ce_oi_strike,
            highest_pe_oi_strike=highest_pe_oi_strike,
            atm_data=atm_data,
            bias=bias
        )
    
    def _get_atm_data(self, df: pd.DataFrame, atm_strike: float) -> Optional[ATMData]:
        """Get data for ATM strike"""
        if atm_strike <= 0:
            return None
        
        atm_row = df[df["STRIKE PRICE"] == atm_strike]
        if atm_row.empty:
            return None
        
        row = atm_row.iloc[0]
        return ATMData(
            strike=atm_strike,
            ce_oi=int(row.get("OI", 0)),
            pe_oi=int(row.get("OI.1", 0)),
            ce_chg_oi=int(row.get("Chg in OI", 0)),
            pe_chg_oi=int(row.get("Chg in OI.1", 0)),
            ce_volume=int(row.get("VOLUME", 0)),
            pe_volume=int(row.get("VOLUME.1", 0)),
            ce_ltp=float(row.get("LTP", 0)),
            pe_ltp=float(row.get("LTP.1", 0)),
            ce_iv=float(row.get("IV", 0)),
            pe_iv=float(row.get("IV.1", 0))
        )
    
    def _determine_bias(self, total_ce_oi: int, total_pe_oi: int, atm_data: Optional[ATMData]) -> str:
        """Determine OI positioning bias"""
        # Check if CE OI is significantly higher than PE OI
        if total_ce_oi > total_pe_oi * 1.5:
            return "BEARISH"
        elif total_pe_oi > total_ce_oi * 1.5:
            return "BULLISH"
        
        # Check ATM structure
        if atm_data:
            if atm_data.pe_oi > atm_data.ce_oi * 1.3:
                return "BULLISH"
            elif atm_data.ce_oi > atm_data.pe_oi * 1.3:
                return "BEARISH"
        
        return "NEUTRAL"