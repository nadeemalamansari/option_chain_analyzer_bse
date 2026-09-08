"""Helper functions for the option chain analyzer"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import re


def clean_numeric(value: any) -> float:
    """Convert a value to float, handling None, strings, and missing values"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove commas and clean
        value = value.replace(",", "").strip()
        if value == "-" or value == "":
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def clean_integer(value: any) -> int:
    """Convert a value to int, handling None, strings, and missing values"""
    return int(clean_numeric(value))


def is_valid_strike(strike: float) -> bool:
    """Check if a strike price is valid"""
    return strike > 0 and not np.isnan(strike)


def find_atm_strike(df: pd.DataFrame, spot_price: float) -> float:
    """Find the ATM strike price closest to spot"""
    if df.empty or spot_price <= 0:
        return 0.0
    
    strikes = df["STRIKE PRICE"].dropna().unique()
    if len(strikes) == 0:
        return 0.0
    
    # Find strike closest to spot
    closest = min(strikes, key=lambda x: abs(x - spot_price))
    return closest


def calculate_pcr(pe_oi: float, ce_oi: float) -> float:
    """Calculate Put-Call Ratio"""
    if ce_oi == 0:
        return 0.0
    return pe_oi / ce_oi


def calculate_max_pain(strikes_data: List[Dict]) -> float:
    """
    Calculate the Max Pain strike price.
    Max Pain is the strike where the total option value (CE + PE) is minimized.
    """
    if not strikes_data:
        return 0.0
    
    # Group by strike price
    strike_groups = {}
    for data in strikes_data:
        strike = data.get("strike_price", 0)
        if strike not in strike_groups:
            strike_groups[strike] = []
        strike_groups[strike].append(data)
    
    # Calculate total pain for each strike
    pain_scores = {}
    for strike, options in strike_groups.items():
        total_pain = 0
        for opt in options:
            ce_oi = opt.get("ce_oi", 0)
            pe_oi = opt.get("pe_oi", 0)
            ce_ltp = opt.get("ce_ltp", 0)
            pe_ltp = opt.get("pe_ltp", 0)
            
            # Pain = (strike - spot) * OI for each option
            # Simplified: weighted by OI
            total_pain += ce_oi * abs(strike - ce_ltp) + pe_oi * abs(strike - pe_ltp)
        
        pain_scores[strike] = total_pain
    
    # Find strike with minimum pain
    if not pain_scores:
        return 0.0
    
    max_pain_strike = min(pain_scores, key=pain_scores.get)
    return max_pain_strike


def detect_buildup(price_change: float, oi_change: float) -> str:
    """
    Detect option buildup pattern based on price and OI change
    
    Returns:
        - "Long Buildup": Price up, OI up
        - "Short Buildup": Price down, OI up
        - "Long Unwinding": Price down, OI down
        - "Short Covering": Price up, OI down
        - "Neutral": No clear pattern
    """
    if abs(price_change) < 0.1 or abs(oi_change) < 1:
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


def format_currency(value: float) -> str:
    """Format a number as Indian currency"""
    if value >= 10000000:  # 1 Crore
        return f"₹{value/10000000:.2f}Cr"
    elif value >= 100000:  # 1 Lakh
        return f"₹{value/100000:.2f}L"
    elif value >= 1000:
        return f"₹{value:,.0f}"
    else:
        return f"₹{value:,.2f}"


def extract_expiry_from_filename(filename: str) -> str:
    """Extract expiry date from filename"""
    # Look for pattern like YYMMDD or DDMMYY
    patterns = [
        r'(\d{2})(\d{2})(\d{2})',  # YYMMDD
        r'(\d{2})(\d{2})(\d{4})',  # DDMMYYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            # Try to parse as date
            try:
                if len(match.group(3)) == 2:  # YYMMDD
                    year = 2000 + int(match.group(3))
                    month = int(match.group(2))
                    day = int(match.group(1))
                else:  # DDMMYYYY
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))
                return f"{year}-{month:02d}-{day:02d}"
            except:
                pass
    
    return "Unknown"


def extract_symbol_from_filename(filename: str) -> str:
    """Extract symbol from filename"""
    if "SENSEX" in filename.upper():
        return "SENSEX"
    elif "BANKNIFTY" in filename.upper():
        return "BANKNIFTY"
    elif "NIFTY" in filename.upper():
        return "NIFTY"
    return "Unknown"


def get_bias_from_score(bullish_score: float, bearish_score: float) -> str:
    """Determine bias from bullish and bearish scores"""
    diff = bullish_score - bearish_score
    
    if diff > 30:
        return "STRONG_BULLISH"
    elif diff > 15:
        return "BULLISH"
    elif diff > 5:
        return "WEAK_BULLISH"
    elif diff < -30:
        return "STRONG_BEARISH"
    elif diff < -15:
        return "BEARISH"
    elif diff < -5:
        return "WEAK_BEARISH"
    else:
        return "NEUTRAL"