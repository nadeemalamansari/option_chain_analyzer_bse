"""Support and Resistance Analysis - Fixed for BSE Format with proper column detection"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Level:
    """Level data structure"""
    strike: float
    strength: int
    oi: int
    chg_oi: int
    volume: int
    status: str
    reasoning: str = ""


@dataclass
class SupportResistanceResult:
    """Support and Resistance result"""
    supports: List[Level] = field(default_factory=list)
    resistances: List[Level] = field(default_factory=list)
    bias: str = "NEUTRAL"


class SupportResistanceAnalyzer:
    """Analyze Support and Resistance levels - Fixed for BSE format"""
    
    def analyze(self, df: pd.DataFrame, atm_strike: float) -> SupportResistanceResult:
        """Perform Support and Resistance analysis"""
        
        if df is None or df.empty:
            print("S/R: DataFrame is empty")
            return SupportResistanceResult()
        
        print("=" * 70)
        print("S/R ANALYSIS STARTED")
        print(f"ATM Strike: {atm_strike}")
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print("=" * 70)
        
        # If ATM strike is not set, find it
        if atm_strike <= 0:
            if "STRIKE PRICE" in df.columns:
                # Find strike with highest total OI
                ce_oi = df.get("OI", pd.Series([0]*len(df))).fillna(0)
                pe_oi = df.get("OI.1", pd.Series([0]*len(df))).fillna(0)
                total_oi = ce_oi + pe_oi
                if total_oi.sum() > 0:
                    max_idx = total_oi.idxmax()
                    atm_strike = df.loc[max_idx, "STRIKE PRICE"]
                    print(f"ATM found by highest OI: {atm_strike}")
                else:
                    # Use middle strike
                    mid_idx = len(df) // 2
                    atm_strike = df.iloc[mid_idx]["STRIKE PRICE"]
                    print(f"ATM set to middle strike: {atm_strike}")
        
        # ================================================================
        # FIND COLUMNS - BSE format specific
        # ================================================================
        
        # CE OI - BSE format uses "OI" (first occurrence)
        ce_oi_col = None
        # PE OI - BSE format uses "OI" (second occurrence) or "OI.1"
        pe_oi_col = None
        
        # List all columns and identify by position
        cols = df.columns.tolist()
        
        # Find STRIKE PRICE position
        strike_idx = -1
        for i, col in enumerate(cols):
            if "STRIKE" in col.upper() or "PRICE" in col.upper():
                strike_idx = i
                break
        
        print(f"STRIKE PRICE index: {strike_idx}")
        
        # CE columns are BEFORE STRIKE PRICE
        ce_cols = cols[:strike_idx] if strike_idx > 0 else []
        # PE columns are AFTER STRIKE PRICE
        pe_cols = cols[strike_idx + 1:] if strike_idx >= 0 else []
        
        print(f"CE columns: {ce_cols}")
        print(f"PE columns: {pe_cols}")
        
        # Find CE OI
        for col in ce_cols:
            if "OI" in col.upper() and "OI" == col:
                ce_oi_col = col
                break
        if ce_oi_col is None:
            for col in ce_cols:
                if "OI" in col.upper():
                    ce_oi_col = col
                    break
        
        # Find PE OI
        for col in pe_cols:
            if "OI" in col.upper():
                pe_oi_col = col
                break
        if pe_oi_col is None:
            # Try looking for "OI.1"
            for col in cols:
                if col == "OI.1" or col == "OI_Y":
                    pe_oi_col = col
                    break
            # Try looking for second occurrence of "OI"
            if pe_oi_col is None:
                oi_cols = [c for c in cols if c == "OI"]
                if len(oi_cols) >= 2:
                    # Use the second OI column
                    if "OI.1" in cols:
                        pe_oi_col = "OI.1"
        
        # Find CE Change OI
        ce_chg_col = None
        for col in ce_cols:
            if "CHG" in col.upper() or "Chg" in col:
                ce_chg_col = col
                break
        if ce_chg_col is None:
            if "Chg in OI" in cols:
                ce_chg_col = "Chg in OI"
            elif "CHNG_IN_OI" in cols:
                ce_chg_col = "CHNG_IN_OI"
        
        # Find PE Change OI
        pe_chg_col = None
        for col in pe_cols:
            if "CHG" in col.upper() or "Chg" in col:
                pe_chg_col = col
                break
        if pe_chg_col is None:
            if "Chg in OI.1" in cols:
                pe_chg_col = "Chg in OI.1"
            elif "CHNG_IN_OI.1" in cols:
                pe_chg_col = "CHNG_IN_OI.1"
        
        # Find CE Volume
        ce_vol_col = None
        for col in ce_cols:
            if "VOL" in col.upper():
                ce_vol_col = col
                break
        if ce_vol_col is None:
            if "VOLUME" in cols:
                ce_vol_col = "VOLUME"
        
        # Find PE Volume
        pe_vol_col = None
        for col in pe_cols:
            if "VOL" in col.upper():
                pe_vol_col = col
                break
        if pe_vol_col is None:
            if "VOLUME.1" in cols:
                pe_vol_col = "VOLUME.1"
        
        print(f"CE OI: {ce_oi_col}, PE OI: {pe_oi_col}")
        print(f"CE Chg: {ce_chg_col}, PE Chg: {pe_chg_col}")
        print(f"CE Vol: {ce_vol_col}, PE Vol: {pe_vol_col}")
        
        # ================================================================
        # FIND SUPPORT LEVELS (PE OI below ATM)
        # ================================================================
        
        supports = []
        if pe_oi_col and "STRIKE PRICE" in df.columns:
            below_atm = df[df["STRIKE PRICE"] < atm_strike].copy()
            print(f"Below ATM: {len(below_atm)} strikes")
            
            if not below_atm.empty:
                # Sort by PE OI descending
                below_atm = below_atm.sort_values(pe_oi_col, ascending=False)
                top_pe = below_atm.head(5)
                
                for i, (_, row) in enumerate(top_pe.iterrows(), 1):
                    pe_oi = row.get(pe_oi_col, 0)
                    print(f"Support candidate {i}: Strike={row['STRIKE PRICE']}, PE OI={pe_oi}")
                    
                    if pe_oi > 0:
                        pe_chg = row.get(pe_chg_col, 0) if pe_chg_col else 0
                        pe_vol = row.get(pe_vol_col, 0) if pe_vol_col else 0
                        status = self._determine_level_status(pe_chg)
                        supports.append(Level(
                            strike=float(row["STRIKE PRICE"]),
                            strength=i,
                            oi=int(pe_oi),
                            chg_oi=int(pe_chg),
                            volume=int(pe_vol),
                            status=status,
                            reasoning=f"PE OI: {pe_oi:,.0f} contracts"
                        ))
        
        # ================================================================
        # FIND RESISTANCE LEVELS (CE OI above ATM)
        # ================================================================
        
        resistances = []
        if ce_oi_col and "STRIKE PRICE" in df.columns:
            above_atm = df[df["STRIKE PRICE"] > atm_strike].copy()
            print(f"Above ATM: {len(above_atm)} strikes")
            
            if not above_atm.empty:
                # Sort by CE OI descending
                above_atm = above_atm.sort_values(ce_oi_col, ascending=False)
                top_ce = above_atm.head(5)
                
                for i, (_, row) in enumerate(top_ce.iterrows(), 1):
                    ce_oi = row.get(ce_oi_col, 0)
                    print(f"Resistance candidate {i}: Strike={row['STRIKE PRICE']}, CE OI={ce_oi}")
                    
                    if ce_oi > 0:
                        ce_chg = row.get(ce_chg_col, 0) if ce_chg_col else 0
                        ce_vol = row.get(ce_vol_col, 0) if ce_vol_col else 0
                        status = self._determine_level_status(ce_chg)
                        resistances.append(Level(
                            strike=float(row["STRIKE PRICE"]),
                            strength=i,
                            oi=int(ce_oi),
                            chg_oi=int(ce_chg),
                            volume=int(ce_vol),
                            status=status,
                            reasoning=f"CE OI: {ce_oi:,.0f} contracts"
                        ))
        
        # ================================================================
        # FALLBACK: Use Total OI if no levels found
        # ================================================================
        
        if not supports and not resistances:
            print("No S/R levels found with individual OI columns, using total OI...")
            
            # Calculate total OI
            ce_oi = df.get("OI", pd.Series([0]*len(df))).fillna(0)
            pe_oi = df.get("OI.1", pd.Series([0]*len(df))).fillna(0)
            df_copy = df.copy()
            df_copy["total_oi"] = ce_oi + pe_oi
            
            if "STRIKE PRICE" in df_copy.columns:
                # Support: highest total OI below ATM
                below_atm = df_copy[df_copy["STRIKE PRICE"] < atm_strike].copy()
                if not below_atm.empty:
                    below_atm = below_atm.sort_values("total_oi", ascending=False)
                    for i, (_, row) in enumerate(below_atm.head(5).iterrows(), 1):
                        if row["total_oi"] > 0:
                            supports.append(Level(
                                strike=float(row["STRIKE PRICE"]),
                                strength=i,
                                oi=int(row["total_oi"]),
                                chg_oi=0,
                                volume=0,
                                status="Stable",
                                reasoning=f"Total OI: {row['total_oi']:,.0f} contracts"
                            ))
                
                # Resistance: highest total OI above ATM
                above_atm = df_copy[df_copy["STRIKE PRICE"] > atm_strike].copy()
                if not above_atm.empty:
                    above_atm = above_atm.sort_values("total_oi", ascending=False)
                    for i, (_, row) in enumerate(above_atm.head(5).iterrows(), 1):
                        if row["total_oi"] > 0:
                            resistances.append(Level(
                                strike=float(row["STRIKE PRICE"]),
                                strength=i,
                                oi=int(row["total_oi"]),
                                chg_oi=0,
                                volume=0,
                                status="Stable",
                                reasoning=f"Total OI: {row['total_oi']:,.0f} contracts"
                            ))
        
        # ================================================================
        # DETERMINE BIAS
        # ================================================================
        
        bias = self._determine_bias(supports, resistances)
        
        print(f"Found {len(supports)} supports, {len(resistances)} resistances")
        print(f"Bias: {bias}")
        print("=" * 70)
        
        return SupportResistanceResult(
            supports=supports,
            resistances=resistances,
            bias=bias
        )
    
    def _determine_level_status(self, chg_oi: float) -> str:
        """Determine if a level is strengthening or weakening"""
        if chg_oi > 100:
            return "Strengthening"
        elif chg_oi < -100:
            return "Weakening"
        else:
            return "Stable"
    
    def _determine_bias(self, supports: List[Level], resistances: List[Level]) -> str:
        """Determine Support/Resistance bias"""
        if not supports and not resistances:
            return "NEUTRAL"
        
        if not supports:
            return "BEARISH"
        if not resistances:
            return "BULLISH"
        
        # Check status
        support_status = supports[0].status if supports else "Stable"
        resistance_status = resistances[0].status if resistances else "Stable"
        
        # Check OI strength
        support_oi = supports[0].oi if supports else 0
        resistance_oi = resistances[0].oi if resistances else 0
        
        if support_status == "Strengthening" and resistance_status == "Weakening":
            return "BULLISH"
        elif support_status == "Weakening" and resistance_status == "Strengthening":
            return "BEARISH"
        elif support_oi > resistance_oi * 1.2:
            return "BULLISH"
        elif resistance_oi > support_oi * 1.2:
            return "BEARISH"
        else:
            return "NEUTRAL"