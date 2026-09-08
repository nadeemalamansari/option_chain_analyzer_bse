# -*- coding: utf-8 -*-
"""
Analyzer Module - Complete Working Version
Optimized for BSE Option Chain Format (21 columns)
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import logging

# Import models
from ..models.analysis_result import AnalysisResult, FactorScore, SupportLevel, ResistanceLevel
from ..models.option_chain import OptionChain

# Set up logger
logger = logging.getLogger(__name__)


# ============================================================================
# MAIN ANALYZER CLASS
# ============================================================================

class Analyzer:
    """
    Main analyzer orchestrating all sub-analyzers.
    Performs comprehensive option chain analysis for BSE format.
    """
    
    def __init__(self):
        """Initialize the analyzer with default values."""
        self.result = AnalysisResult()
        self.df = None
        logger.info("Analyzer initialized")
    
    def analyze(self, option_chain: OptionChain, filename: str) -> AnalysisResult:
        """
        Perform complete analysis of the option chain.
        
        Args:
            option_chain: OptionChain object containing the data
            filename: Name of the source file
            
        Returns:
            AnalysisResult: Complete analysis results
        """
        logger.info(f"Starting analysis for: {filename}")
        
        # Initialize result
        self.result = AnalysisResult()
        self.result.file_name = filename
        self.result.exchange = option_chain.exchange or "NSE"
        self.result.symbol = option_chain.symbol or "UNKNOWN"
        self.result.expiry = option_chain.expiry or ""
        self.result.spot_price = option_chain.spot_price or 0
        self.result.atm_strike = option_chain.atm_strike or 0
        self.result.timestamp = datetime.now()
        
        # Get the dataframe
        self.df = option_chain.data
        if self.df is None or self.df.empty:
            logger.warning("DataFrame is empty")
            self.result.key_reasons = ["No data available for analysis"]
            return self.result
        
        # Debug: Print columns
        logger.info(f"DataFrame columns: {self.df.columns.tolist()}")
        logger.info(f"DataFrame shape: {self.df.shape}")
        logger.info(f"ATM Strike: {self.result.atm_strike}")
        
        # ================================================================
        # STORE RAW STRIKES DATA - FIXED
        # ================================================================
        try:
            raw_strikes = []
            for _, row in self.df.iterrows():
                try:
                    # Safe value extraction
                    def safe_float(val):
                        try:
                            if val in [None, '-', '--', '---', '']:
                                return 0.0
                            return float(val)
                        except (ValueError, TypeError):
                            return 0.0
                    
                    def safe_int(val):
                        try:
                            if val in [None, '-', '--', '---', '']:
                                return 0
                            return int(float(val))
                        except (ValueError, TypeError):
                            return 0
                    
                    strike_data = {
                        "strike_price": safe_float(row.get("STRIKE PRICE", 0)),
                        "ce_oi": safe_int(row.get("OI", 0)),
                        "pe_oi": safe_int(row.get("OI.1", 0)),
                        "ce_chg_oi": safe_int(row.get("Chg in OI", 0)),
                        "pe_chg_oi": safe_int(row.get("Chg in OI.1", 0)),
                        "ce_volume": safe_int(row.get("VOLUME", 0)),
                        "pe_volume": safe_int(row.get("VOLUME.1", 0)),
                        "ce_ltp": safe_float(row.get("LTP", 0)),
                        "pe_ltp": safe_float(row.get("LTP.1", 0)),
                        "ce_iv": safe_float(row.get("IV", 0)),
                        "pe_iv": safe_float(row.get("IV.1", 0)),
                        "ce_chng": safe_float(row.get("CHNG", 0)),
                        "pe_chng": safe_float(row.get("CHNG.1", 0)),
                        "ce_bid_qty": safe_int(row.get("BID QTY", 0)),
                        "ce_bid_price": safe_float(row.get("BID PRICE", 0)),
                        "ce_ask_price": safe_float(row.get("ASK PRICE", 0)),
                        "ce_ask_qty": safe_int(row.get("ASK QTY", 0)),
                        "pe_bid_qty": safe_int(row.get("BID QTY.1", 0)),
                        "pe_bid_price": safe_float(row.get("BID PRICE.1", 0)),
                        "pe_ask_price": safe_float(row.get("ASK PRICE.1", 0)),
                        "pe_ask_qty": safe_int(row.get("ASK QTY.1", 0))
                    }
                    raw_strikes.append(strike_data)
                except Exception as e:
                    # Skip rows with errors
                    continue
            
            self.result.raw_strikes = raw_strikes
            logger.info(f"Stored {len(raw_strikes)} raw strikes data")
            
        except Exception as e:
            logger.error(f"Error storing raw strikes: {e}")
            self.result.raw_strikes = []
        
        # Perform all analyses
        try:
            self._analyze_open_interest()
            self._analyze_pcr()
            self._analyze_atm_structure()
            self._analyze_volume()
            self._analyze_change_oi()
            self._analyze_support_resistance()
            self._analyze_max_pain()
            
            # Calculate final results
            self._calculate_factor_scores()
            self._calculate_final_decision()
            self.result.key_reasons = self._generate_key_reasons()
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            self.result.key_reasons = [f"Analysis completed with errors: {str(e)}"]
        
        logger.info("Analysis complete")
        return self.result
    
    # ========================================================================
    # SAFE VALUE EXTRACTION HELPERS
    # ========================================================================
    
    def _safe_float(self, val) -> float:
        """Safely convert value to float"""
        try:
            if val in [None, '-', '--', '---', '']:
                return 0.0
            return float(val)
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, val) -> int:
        """Safely convert value to int"""
        try:
            if val in [None, '-', '--', '---', '']:
                return 0
            return int(float(val))
        except (ValueError, TypeError):
            return 0
    
    def _safe_sum(self, series) -> float:
        """Safely sum a series with error handling"""
        total = 0.0
        for val in series:
            try:
                if val not in [None, '-', '--', '---', '']:
                    total += float(val)
            except (ValueError, TypeError):
                continue
        return total
    
    # ========================================================================
    # 1. OPEN INTEREST ANALYSIS
    # ========================================================================
    
    def _analyze_open_interest(self):
        """Analyze Open Interest data."""
        try:
            df = self.df
            
            # Find CE OI column
            ce_oi_col = self._find_column(df, ["OI", "OI_X", "CE_OI", "OI_CE", "CALLS_OI"])
            
            # Find PE OI column
            pe_oi_col = self._find_column(df, ["OI.1", "OI_Y", "PE_OI", "OI_PE", "PUTS_OI"])
            
            # If PE OI not found, check for duplicate OI columns
            if pe_oi_col is None:
                oi_cols = [c for c in df.columns if c == "OI"]
                if len(oi_cols) >= 2:
                    if "OI.1" in df.columns:
                        pe_oi_col = "OI.1"
            
            # Calculate totals with safe sum
            ce_oi_sum = self._safe_sum(df[ce_oi_col]) if ce_oi_col else 0
            pe_oi_sum = self._safe_sum(df[pe_oi_col]) if pe_oi_col else 0
            
            self.result.total_ce_oi = int(ce_oi_sum)
            self.result.total_pe_oi = int(pe_oi_sum)
            
            # Calculate PCR
            self.result.oi_pcr = pe_oi_sum / ce_oi_sum if ce_oi_sum > 0 else 0
            
            # Find highest OI strikes
            if ce_oi_col and "STRIKE PRICE" in df.columns:
                try:
                    max_idx = df[ce_oi_col].idxmax()
                    self.result.highest_ce_oi_strike = df.loc[max_idx, "STRIKE PRICE"]
                except:
                    pass
            
            if pe_oi_col and "STRIKE PRICE" in df.columns:
                try:
                    max_idx = df[pe_oi_col].idxmax()
                    self.result.highest_pe_oi_strike = df.loc[max_idx, "STRIKE PRICE"]
                except:
                    pass
            
            # Determine bias
            if self.result.total_ce_oi > self.result.total_pe_oi * 1.5:
                self.result.oi_positioning_bias = "BEARISH"
            elif self.result.total_pe_oi > self.result.total_ce_oi * 1.5:
                self.result.oi_positioning_bias = "BULLISH"
            else:
                self.result.oi_positioning_bias = "NEUTRAL"
            
            logger.info(f"OI Analysis: CE={self.result.total_ce_oi}, PE={self.result.total_pe_oi}, PCR={self.result.oi_pcr:.2f}")
            
        except Exception as e:
            logger.error(f"Error in OI analysis: {e}")
            self.result.oi_positioning_bias = "NEUTRAL"
    
    # ========================================================================
    # 2. PCR ANALYSIS
    # ========================================================================
    
    def _analyze_pcr(self):
        """Analyze Put-Call Ratio."""
        try:
            df = self.df
            
            # Find OI columns
            ce_oi_col = self._find_column(df, ["OI", "OI_X", "CE_OI", "OI_CE"])
            pe_oi_col = self._find_column(df, ["OI.1", "OI_Y", "PE_OI", "OI_PE"])
            
            # Calculate OI totals with safe sum
            ce_oi_sum = self._safe_sum(df[ce_oi_col]) if ce_oi_col else 0
            pe_oi_sum = self._safe_sum(df[pe_oi_col]) if pe_oi_col else 0
            
            # Find Change OI columns
            ce_chg_col = self._find_column(df, ["Chg in OI", "CHNG_IN_OI", "CHG_OI"])
            pe_chg_col = self._find_column(df, ["Chg in OI.1", "CHNG_IN_OI.1", "CHG_OI.1"])
            
            # Calculate Change OI totals with safe sum
            ce_chg_sum = self._safe_sum(df[ce_chg_col]) if ce_chg_col else 0
            pe_chg_sum = self._safe_sum(df[pe_chg_col]) if pe_chg_col else 0
            
            self.result.total_ce_chg_oi = int(ce_chg_sum)
            self.result.total_pe_chg_oi = int(pe_chg_sum)
            
            # Calculate PCR
            self.result.oi_pcr = pe_oi_sum / ce_oi_sum if ce_oi_sum > 0 else 0
            self.result.change_oi_pcr = pe_chg_sum / ce_chg_sum if ce_chg_sum != 0 else 0
            
            # Determine PCR bias
            if self.result.oi_pcr > 0.7:
                self.result.pcr_bias = "BEARISH"
            elif self.result.oi_pcr < 0.4:
                self.result.pcr_bias = "BULLISH"
            else:
                self.result.pcr_bias = "NEUTRAL"
            
            # Determine Change OI bias
            if self.result.change_oi_pcr < 0.4:
                self.result.change_oi_bias = "BEARISH"
            elif self.result.change_oi_pcr > 0.8:
                self.result.change_oi_bias = "BULLISH"
            else:
                self.result.change_oi_bias = "NEUTRAL"
            
            logger.info(f"PCR Analysis: OI PCR={self.result.oi_pcr:.2f}, Change OI PCR={self.result.change_oi_pcr:.2f}")
            
        except Exception as e:
            logger.error(f"Error in PCR analysis: {e}")
            self.result.pcr_bias = "NEUTRAL"
            self.result.change_oi_bias = "NEUTRAL"
    
    # ========================================================================
    # 3. ATM STRUCTURE ANALYSIS
    # ========================================================================
    
    def _analyze_atm_structure(self):
        """Analyze ATM structure."""
        try:
            atm_strike = self.result.atm_strike
            if atm_strike <= 0:
                logger.warning("ATM strike not available")
                return
            
            df = self.df
            atm_row = df[df["STRIKE PRICE"] == atm_strike]
            if atm_row.empty:
                # Find closest strike
                closest_idx = (df["STRIKE PRICE"] - atm_strike).abs().idxmin()
                atm_row = df.loc[closest_idx:closest_idx]
                self.result.atm_strike = df.loc[closest_idx, "STRIKE PRICE"]
            
            if atm_row.empty:
                return
            
            row = atm_row.iloc[0]
            
            # Get values safely
            self.result.atm_ce_oi = self._safe_int(row.get("OI", 0))
            self.result.atm_pe_oi = self._safe_int(row.get("OI.1", 0))
            self.result.atm_ce_chg_oi = self._safe_int(row.get("Chg in OI", 0))
            self.result.atm_pe_chg_oi = self._safe_int(row.get("Chg in OI.1", 0))
            self.result.atm_ce_volume = self._safe_int(row.get("VOLUME", 0))
            self.result.atm_pe_volume = self._safe_int(row.get("VOLUME.1", 0))
            self.result.atm_ce_ltp = self._safe_float(row.get("LTP", 0))
            self.result.atm_pe_ltp = self._safe_float(row.get("LTP.1", 0))
            self.result.atm_ce_iv = self._safe_float(row.get("IV", 0))
            self.result.atm_pe_iv = self._safe_float(row.get("IV.1", 0))
            
            # Determine ATM bias
            if self.result.atm_ce_chg_oi > self.result.atm_pe_chg_oi * 1.5:
                self.result.atm_bias = "BEARISH"
            elif self.result.atm_pe_chg_oi > self.result.atm_ce_chg_oi * 1.5:
                self.result.atm_bias = "BULLISH"
            else:
                self.result.atm_bias = "NEUTRAL"
            
            logger.info(f"ATM Analysis: Strike={self.result.atm_strike}, CE OI={self.result.atm_ce_oi}, PE OI={self.result.atm_pe_oi}")
            
        except Exception as e:
            logger.error(f"Error in ATM analysis: {e}")
            self.result.atm_bias = "NEUTRAL"
    
    # ========================================================================
    # 4. VOLUME ANALYSIS
    # ========================================================================
    
    def _analyze_volume(self):
        """Analyze Volume."""
        try:
            df = self.df
            
            # Find volume columns
            ce_vol_col = self._find_column(df, ["VOLUME", "VOLUME_X", "CE_VOLUME"])
            pe_vol_col = self._find_column(df, ["VOLUME.1", "VOLUME_Y", "PE_VOLUME"])
            
            # Calculate volumes with safe sum
            ce_vol = self._safe_sum(df[ce_vol_col]) if ce_vol_col else self.result.atm_ce_volume
            pe_vol = self._safe_sum(df[pe_vol_col]) if pe_vol_col else self.result.atm_pe_volume
            
            # Store volumes
            self.result._ce_volume = int(ce_vol)
            self.result._pe_volume = int(pe_vol)
            
            # Calculate volume PCR
            vol_pcr = pe_vol / ce_vol if ce_vol > 0 else 0
            self.result._vol_pcr = vol_pcr
            
            # Determine bias
            if vol_pcr > 1.2:
                self.result.volume_bias = "BEARISH"
            elif vol_pcr < 0.7:
                self.result.volume_bias = "BULLISH"
            else:
                self.result.volume_bias = "NEUTRAL"
            
            logger.info(f"Volume Analysis: CE={ce_vol}, PE={pe_vol}, PCR={vol_pcr:.2f}")
            
        except Exception as e:
            logger.error(f"Error in Volume analysis: {e}")
            self.result.volume_bias = "NEUTRAL"
    
    # ========================================================================
    # 5. CHANGE IN OI ANALYSIS
    # ========================================================================
    
    def _analyze_change_oi(self):
        """Analyze Change in OI and Buildup Patterns."""
        try:
            df = self.df
            
            # Find columns
            ce_chg_col = self._find_column(df, ["Chg in OI", "CHNG_IN_OI", "CHG_OI"])
            pe_chg_col = self._find_column(df, ["Chg in OI.1", "CHNG_IN_OI.1", "CHG_OI.1"])
            ce_ltp_col = self._find_column(df, ["LTP", "LTP_X", "CE_LTP"])
            pe_ltp_col = self._find_column(df, ["LTP.1", "LTP_Y", "PE_LTP"])
            ce_oi_col = self._find_column(df, ["OI", "OI_X", "CE_OI"])
            pe_oi_col = self._find_column(df, ["OI.1", "OI_Y", "PE_OI"])
            
            # Detect buildup patterns
            call_buildup = {
                "long_buildup": [],
                "short_buildup": [],
                "long_unwinding": [],
                "short_covering": []
            }
            
            put_buildup = {
                "long_buildup": [],
                "short_buildup": [],
                "long_unwinding": [],
                "short_covering": []
            }
            
            # Only if we have all required columns
            if ce_chg_col and ce_ltp_col and ce_oi_col and pe_chg_col and pe_ltp_col and pe_oi_col:
                for _, row in df.iterrows():
                    # Call side
                    ce_chg = self._safe_float(row.get(ce_chg_col, 0))
                    ce_ltp = self._safe_float(row.get(ce_ltp_col, 0))
                    ce_oi = self._safe_float(row.get(ce_oi_col, 0))
                    
                    # Calculate price change (using CHNG column if available)
                    ce_price_change = self._safe_float(row.get("CHNG", 0))
                    
                    if ce_oi > 0 and ce_chg != 0:
                        pattern = self._detect_buildup(ce_price_change, ce_chg)
                        if pattern == "Long Buildup":
                            call_buildup["long_buildup"].append(self._safe_float(row["STRIKE PRICE"]))
                        elif pattern == "Short Buildup":
                            call_buildup["short_buildup"].append(self._safe_float(row["STRIKE PRICE"]))
                        elif pattern == "Long Unwinding":
                            call_buildup["long_unwinding"].append(self._safe_float(row["STRIKE PRICE"]))
                        elif pattern == "Short Covering":
                            call_buildup["short_covering"].append(self._safe_float(row["STRIKE PRICE"]))
                    
                    # Put side
                    pe_chg = self._safe_float(row.get(pe_chg_col, 0))
                    pe_ltp = self._safe_float(row.get(pe_ltp_col, 0))
                    pe_oi = self._safe_float(row.get(pe_oi_col, 0))
                    
                    # Calculate price change (using CHNG.1 column if available)
                    pe_price_change = self._safe_float(row.get("CHNG.1", 0))
                    
                    if pe_oi > 0 and pe_chg != 0:
                        pattern = self._detect_buildup(pe_price_change, pe_chg)
                        if pattern == "Long Buildup":
                            put_buildup["long_buildup"].append(self._safe_float(row["STRIKE PRICE"]))
                        elif pattern == "Short Buildup":
                            put_buildup["short_buildup"].append(self._safe_float(row["STRIKE PRICE"]))
                        elif pattern == "Long Unwinding":
                            put_buildup["long_unwinding"].append(self._safe_float(row["STRIKE PRICE"]))
                        elif pattern == "Short Covering":
                            put_buildup["short_covering"].append(self._safe_float(row["STRIKE PRICE"]))
            
            self.result.call_buildup = call_buildup
            self.result.put_buildup = put_buildup
            
            # Determine buildup bias
            call_short = len(call_buildup.get("short_buildup", []))
            put_short = len(put_buildup.get("short_buildup", []))
            call_long = len(call_buildup.get("long_buildup", []))
            put_long = len(put_buildup.get("long_buildup", []))
            
            if call_short > put_short + 3:
                self.result.buildup_bias = "BEARISH"
            elif put_short > call_short + 3:
                self.result.buildup_bias = "BULLISH"
            elif call_long > put_long + 3:
                self.result.buildup_bias = "BULLISH"
            elif put_long > call_long + 3:
                self.result.buildup_bias = "BEARISH"
            else:
                self.result.buildup_bias = "NEUTRAL"
            
            logger.info(f"Buildup Analysis: Call Short={call_short}, Put Short={put_short}")
            
        except Exception as e:
            logger.error(f"Error in Change OI analysis: {e}")
            self.result.buildup_bias = "NEUTRAL"
    
    def _detect_buildup(self, price_change: float, oi_change: float) -> str:
        """Detect buildup pattern based on price and OI change."""
        if abs(price_change) < 0.5 or abs(oi_change) < 10:
            return "Neutral"
        
        if price_change > 0 and oi_change > 0:
            return "Long Buildup"
        elif price_change < 0 and oi_change > 0:
            return "Short Buildup"
        elif price_change < 0 and oi_change < 0:
            return "Long Unwinding"
        elif price_change > 0 and oi_change < 0:
            return "Short Covering"
        return "Neutral"
    
    # ========================================================================
    # 6. SUPPORT & RESISTANCE ANALYSIS
    # ========================================================================
    
    def _analyze_support_resistance(self):
        """Analyze Support and Resistance levels."""
        try:
            atm = self.result.atm_strike
            if atm <= 0:
                logger.warning("ATM strike not available for S/R")
                return
            
            df = self.df
            
            # Find OI columns
            ce_oi_col = self._find_column(df, ["OI", "OI_X", "CE_OI"])
            pe_oi_col = self._find_column(df, ["OI.1", "OI_Y", "PE_OI"])
            
            # Find Change OI columns
            ce_chg_col = self._find_column(df, ["Chg in OI", "CHNG_IN_OI", "CHG_OI"])
            pe_chg_col = self._find_column(df, ["Chg in OI.1", "CHNG_IN_OI.1", "CHG_OI.1"])
            
            # Find Volume columns
            ce_vol_col = self._find_column(df, ["VOLUME", "VOLUME_X", "CE_VOLUME"])
            pe_vol_col = self._find_column(df, ["VOLUME.1", "VOLUME_Y", "PE_VOLUME"])
            
            # Clear previous S/R
            self.result.supports = []
            self.result.resistances = []
            
            # Support levels (PE OI below ATM)
            if pe_oi_col and "STRIKE PRICE" in df.columns:
                below_atm = df[df["STRIKE PRICE"] < atm].copy()
                if not below_atm.empty:
                    # Sort by PE OI descending
                    below_atm = below_atm.sort_values(pe_oi_col, ascending=False)
                    top_pe = below_atm.head(5)
                    
                    for i, (_, row) in enumerate(top_pe.iterrows(), 1):
                        pe_oi = self._safe_float(row.get(pe_oi_col, 0))
                        if pe_oi > 0:
                            pe_chg = self._safe_float(row.get(pe_chg_col, 0)) if pe_chg_col else 0
                            pe_vol = self._safe_float(row.get(pe_vol_col, 0)) if pe_vol_col else 0
                            status = self._determine_level_status(pe_chg)
                            support = SupportLevel(
                                strike=self._safe_float(row["STRIKE PRICE"]),
                                strength=i,
                                pe_oi=int(pe_oi),
                                pe_chg_oi=int(pe_chg),
                                pe_volume=int(pe_vol),
                                status=status,
                                reasoning=f"PE OI: {pe_oi:,.0f}"
                            )
                            self.result.supports.append(support)
            
            # Resistance levels (CE OI above ATM)
            if ce_oi_col and "STRIKE PRICE" in df.columns:
                above_atm = df[df["STRIKE PRICE"] > atm].copy()
                if not above_atm.empty:
                    # Sort by CE OI descending
                    above_atm = above_atm.sort_values(ce_oi_col, ascending=False)
                    top_ce = above_atm.head(5)
                    
                    for i, (_, row) in enumerate(top_ce.iterrows(), 1):
                        ce_oi = self._safe_float(row.get(ce_oi_col, 0))
                        if ce_oi > 0:
                            ce_chg = self._safe_float(row.get(ce_chg_col, 0)) if ce_chg_col else 0
                            ce_vol = self._safe_float(row.get(ce_vol_col, 0)) if ce_vol_col else 0
                            status = self._determine_level_status(ce_chg)
                            resistance = ResistanceLevel(
                                strike=self._safe_float(row["STRIKE PRICE"]),
                                strength=i,
                                ce_oi=int(ce_oi),
                                ce_chg_oi=int(ce_chg),
                                ce_volume=int(ce_vol),
                                status=status,
                                reasoning=f"CE OI: {ce_oi:,.0f}"
                            )
                            self.result.resistances.append(resistance)
            
            # Fallback: Use total OI if no levels found
            if not self.result.supports and not self.result.resistances:
                logger.info("No S/R levels found, using total OI fallback")
                self._find_levels_with_total_oi(df, atm)
            
            # Determine S/R bias
            if self.result.supports and self.result.resistances:
                support_oi = self.result.supports[0].pe_oi
                resistance_oi = self.result.resistances[0].ce_oi
                
                if support_oi > resistance_oi * 1.2:
                    self.result.support_resistance_bias = "BULLISH"
                elif resistance_oi > support_oi * 1.2:
                    self.result.support_resistance_bias = "BEARISH"
                else:
                    self.result.support_resistance_bias = "NEUTRAL"
            else:
                self.result.support_resistance_bias = "NEUTRAL"
            
            logger.info(f"S/R Analysis: {len(self.result.supports)} supports, {len(self.result.resistances)} resistances")
            
        except Exception as e:
            logger.error(f"Error in Support/Resistance analysis: {e}")
            self.result.support_resistance_bias = "NEUTRAL"
    
    def _find_levels_with_total_oi(self, df: pd.DataFrame, atm_strike: float):
        """Find levels using total OI (CE + PE) as fallback"""
        try:
            # Calculate total OI safely
            df_copy = df.copy()
            ce_oi = df_copy.get("OI", pd.Series([0]*len(df_copy))).fillna(0)
            pe_oi = df_copy.get("OI.1", pd.Series([0]*len(df_copy))).fillna(0)
            df_copy["total_oi"] = ce_oi + pe_oi
            
            if "STRIKE PRICE" in df_copy.columns:
                # Support: highest total OI below ATM
                below_atm = df_copy[df_copy["STRIKE PRICE"] < atm_strike].copy()
                if not below_atm.empty:
                    below_atm = below_atm.sort_values("total_oi", ascending=False)
                    for i, (_, row) in enumerate(below_atm.head(5).iterrows(), 1):
                        if row["total_oi"] > 0:
                            support = SupportLevel(
                                strike=self._safe_float(row["STRIKE PRICE"]),
                                strength=i,
                                pe_oi=int(row["total_oi"]),
                                pe_chg_oi=0,
                                pe_volume=0,
                                status="Stable",
                                reasoning=f"Total OI: {row['total_oi']:,.0f}"
                            )
                            self.result.supports.append(support)
                
                # Resistance: highest total OI above ATM
                above_atm = df_copy[df_copy["STRIKE PRICE"] > atm_strike].copy()
                if not above_atm.empty:
                    above_atm = above_atm.sort_values("total_oi", ascending=False)
                    for i, (_, row) in enumerate(above_atm.head(5).iterrows(), 1):
                        if row["total_oi"] > 0:
                            resistance = ResistanceLevel(
                                strike=self._safe_float(row["STRIKE PRICE"]),
                                strength=i,
                                ce_oi=int(row["total_oi"]),
                                ce_chg_oi=0,
                                ce_volume=0,
                                status="Stable",
                                reasoning=f"Total OI: {row['total_oi']:,.0f}"
                            )
                            self.result.resistances.append(resistance)
        except Exception as e:
            logger.error(f"Error in total OI fallback: {e}")
    
    def _determine_level_status(self, chg_oi: float) -> str:
        """Determine if a level is strengthening or weakening."""
        if chg_oi > 100:
            return "Strengthening"
        elif chg_oi < -100:
            return "Weakening"
        else:
            return "Stable"
    
    # ========================================================================
    # 7. MAX PAIN ANALYSIS
    # ========================================================================
    
    def _analyze_max_pain(self):
        """Analyze Max Pain."""
        try:
            df = self.df
            strikes = df["STRIKE PRICE"].unique()
            if len(strikes) < 2:
                return
            
            # Find OI columns
            ce_oi_col = self._find_column(df, ["OI", "OI_X", "CE_OI"])
            pe_oi_col = self._find_column(df, ["OI.1", "OI_Y", "PE_OI"])
            
            if not ce_oi_col or not pe_oi_col:
                return
            
            min_pain = float('inf')
            max_pain_strike = strikes[0]
            
            for strike in strikes:
                pain = self._calculate_pain(df, strike, ce_oi_col, pe_oi_col)
                if pain < min_pain:
                    min_pain = pain
                    max_pain_strike = strike
            
            self.result.max_pain_strike = max_pain_strike
            
            # Determine bias
            spot = self.result.spot_price
            if spot > 0:
                diff = spot - max_pain_strike
                if abs(diff) < 50:
                    self.result.max_pain_bias = "NEUTRAL"
                elif diff > 50:
                    self.result.max_pain_bias = "BEARISH"
                else:
                    self.result.max_pain_bias = "BULLISH"
            else:
                self.result.max_pain_bias = "NEUTRAL"
            
            logger.info(f"Max Pain: {max_pain_strike}")
            
        except Exception as e:
            logger.error(f"Error in Max Pain analysis: {e}")
            self.result.max_pain_bias = "NEUTRAL"
    
    def _calculate_pain(self, df: pd.DataFrame, target_strike: float, ce_oi_col: str, pe_oi_col: str) -> float:
        """Calculate total pain at a given strike."""
        total_pain = 0
        
        for _, row in df.iterrows():
            strike = self._safe_float(row["STRIKE PRICE"])
            ce_oi = self._safe_float(row.get(ce_oi_col, 0))
            pe_oi = self._safe_float(row.get(pe_oi_col, 0))
            
            if strike < target_strike:
                total_pain += ce_oi * (target_strike - strike)
            elif strike > target_strike:
                total_pain += pe_oi * (strike - target_strike)
        
        return total_pain
    
    # ========================================================================
    # 8. FACTOR SCORING
    # ========================================================================
    
    def _calculate_factor_scores(self):
        """Calculate individual factor scores."""
        
        factors = [
            ("OI Positioning", self.result.oi_positioning_bias, 18),
            ("Change in OI", self.result.change_oi_bias, 18),
            ("Price + OI / Buildup", self.result.buildup_bias, 15),
            ("Support / Resistance", self.result.support_resistance_bias, 15),
            ("PCR", self.result.pcr_bias, 10),
            ("Volume", self.result.volume_bias, 8),
            ("IV", self.result.iv_bias or "NEUTRAL", 5),
            ("IV Skew", "NEUTRAL", 3),
            ("Max Pain", self.result.max_pain_bias, 3),
            ("Expected Move", "NEUTRAL", 3),
            ("Liquidity", "NEUTRAL", 2),
        ]
        
        for name, bias, weight in factors:
            bullish, bearish = self._get_bias_scores(bias)
            score = FactorScore(
                factor_name=name,
                bullish_score=bullish,
                bearish_score=bearish,
                weight=weight,
                bias=bias,
                reasoning=f"{name} bias: {bias}"
            )
            self.result.factor_scores.append(score)
    
    def _get_bias_scores(self, bias: str) -> Tuple[float, float]:
        """Get bullish and bearish scores for a bias."""
        mapping = {
            "STRONG_BULLISH": (95, 5),
            "BULLISH": (80, 20),
            "WEAK_BULLISH": (65, 35),
            "NEUTRAL": (50, 50),
            "WEAK_BEARISH": (35, 65),
            "BEARISH": (20, 80),
            "STRONG_BEARISH": (5, 95),
        }
        return mapping.get(bias, (50, 50))
    
    # ========================================================================
    # 9. FINAL DECISION
    # ========================================================================
    
    def _calculate_final_decision(self):
        """Calculate final market decision."""
        total_bullish = 0
        total_bearish = 0
        
        for score in self.result.factor_scores:
            weight = score.weight / 100
            total_bullish += score.bullish_score * weight
            total_bearish += score.bearish_score * weight
        
        self.result.bullish_score = total_bullish
        self.result.bearish_score = total_bearish
        
        # Determine final classification
        diff = total_bullish - total_bearish
        
        if diff > 30:
            self.result.final_market = "STRONG_BULLISH"
        elif diff > 15:
            self.result.final_market = "BULLISH"
        elif diff > 5:
            self.result.final_market = "WEAK_BULLISH"
        elif diff < -30:
            self.result.final_market = "STRONG_BEARISH"
        elif diff < -15:
            self.result.final_market = "BEARISH"
        elif diff < -5:
            self.result.final_market = "WEAK_BEARISH"
        else:
            self.result.final_market = "NEUTRAL"
        
        # Calculate confidence
        self.result.confidence = self._calculate_confidence()
        
        logger.info(f"Final Decision: {self.result.final_market} (Bullish={total_bullish:.0f}, Bearish={total_bearish:.0f})")
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score."""
        bearish_count = 0
        bullish_count = 0
        neutral_count = 0
        
        for score in self.result.factor_scores:
            if score.bias in ["STRONG_BULLISH", "BULLISH", "WEAK_BULLISH"]:
                bullish_count += 1
            elif score.bias in ["STRONG_BEARISH", "BEARISH", "WEAK_BEARISH"]:
                bearish_count += 1
            else:
                neutral_count += 1
        
        total = bullish_count + bearish_count + neutral_count
        if total == 0:
            return 50
        
        max_count = max(bullish_count, bearish_count)
        agreement = max_count / total
        
        base_confidence = 50 + (agreement * 30)
        
        if self.result.total_ce_oi > 0 and self.result.total_pe_oi > 0:
            base_confidence += 10
        
        return min(100, base_confidence)
    
    def _generate_key_reasons(self) -> List[str]:
        """Generate key reasons for the final decision."""
        reasons = []
        
        if self.result.oi_positioning_bias != "NEUTRAL":
            reasons.append(f"OI Positioning: {self.result.oi_positioning_bias} with CE OI {self.result.total_ce_oi:,.0f} vs PE OI {self.result.total_pe_oi:,.0f}")
        
        if self.result.atm_bias != "NEUTRAL":
            reasons.append(f"ATM Structure: {self.result.atm_bias} with PE OI {self.result.atm_pe_oi:,.0f} vs CE OI {self.result.atm_ce_oi:,.0f}")
        
        if self.result.pcr_bias != "NEUTRAL":
            reasons.append(f"PCR Bias: {self.result.pcr_bias} (OI PCR: {self.result.oi_pcr:.2f})")
        
        if self.result.change_oi_bias != "NEUTRAL":
            reasons.append(f"Change OI PCR: {self.result.change_oi_pcr:.2f} - {self.result.change_oi_bias}")
        
        if self.result.volume_bias != "NEUTRAL":
            reasons.append(f"Volume Bias: {self.result.volume_bias}")
        
        if self.result.buildup_bias != "NEUTRAL":
            reasons.append(f"Buildup Bias: {self.result.buildup_bias}")
        
        if self.result.supports:
            reasons.append(f"Strongest Support: {self.result.supports[0].strike:,.0f}")
        
        if self.result.resistances:
            reasons.append(f"Strongest Resistance: {self.result.resistances[0].strike:,.0f}")
        
        if self.result.max_pain_strike > 0:
            reasons.append(f"Max Pain: {self.result.max_pain_strike:,.0f}")
        
        if not reasons:
            reasons.append("Analysis completed with basic metrics")
        
        return reasons[:5]
    
    # ========================================================================
    # 10. UTILITY METHODS
    # ========================================================================
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by trying multiple possible names."""
        for name in possible_names:
            if name in df.columns:
                return name
        return None


# ============================================================================
# END OF CLASS
# ============================================================================