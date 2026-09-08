"""Data validation utilities"""

import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import re


@dataclass
class ValidationResult:
    is_valid: bool = False
    exchange: str = "NSE"
    symbol: str = ""
    expiry: str = ""
    atm_strike: float = 0.0
    strike_range: Tuple[float, float] = (0, 0)
    num_strikes: int = 0
    missing_columns: List[str] = field(default_factory=list)
    duplicate_strikes: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    details: Dict = field(default_factory=dict)


class DataValidator:
    """Validates Option Chain data quality and completeness"""
    
    REQUIRED_CE = ['STRIKE PRICE', 'OI', 'VOLUME', 'LTP']
    REQUIRED_PE = ['OI.1', 'VOLUME.1', 'LTP.1']
    
    def __init__(self):
        self.file_name = None
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        result = ValidationResult()
        
        if df is None or df.empty:
            result.errors.append("DataFrame is empty or None")
            result.is_valid = False
            return result
        
        # Check STRIKE PRICE
        if "STRIKE PRICE" not in df.columns:
            result.errors.append("Missing STRIKE PRICE column")
            result.is_valid = False
            return result
        
        # Check required columns
        missing_ce = [c for c in self.REQUIRED_CE if c not in df.columns]
        missing_pe = [c for c in self.REQUIRED_PE if c not in df.columns]
        
        if missing_ce:
            result.errors.append(f"Missing Call columns: {missing_ce}")
        if missing_pe:
            result.errors.append(f"Missing Put columns: {missing_pe}")
        
        # Process strikes
        strikes = df['STRIKE PRICE']
        result.strike_range = (strikes.min(), strikes.max())
        result.num_strikes = len(strikes)
        result.duplicate_strikes = strikes.duplicated().any()
        
        if result.duplicate_strikes:
            result.warnings.append("Duplicate strike prices found")
        
        # Check invalid strikes
        invalid = df[df['STRIKE PRICE'] <= 0]
        if len(invalid) > 0:
            result.errors.append(f"Found {len(invalid)} invalid strike prices")
        
        # Check OI data
        if 'OI' in df.columns and 'OI.1' in df.columns:
            ce_oi = df['OI'].fillna(0).sum()
            pe_oi = df['OI.1'].fillna(0).sum()
            if ce_oi == 0 and pe_oi == 0:
                result.warnings.append("All OI values are zero")
            else:
                result.details['ce_oi_sum'] = int(ce_oi)
                result.details['pe_oi_sum'] = int(pe_oi)
                result.details['oi_pcr'] = pe_oi / ce_oi if ce_oi > 0 else 0
        
        # Find ATM
        result.atm_strike = self._find_atm_strike(df)
        
        # Extract symbol
        if self.file_name:
            if 'SENSEX' in self.file_name.upper():
                result.symbol = 'SENSEX'
                result.exchange = 'BSE'
            elif 'NIFTY' in self.file_name.upper():
                result.symbol = 'NIFTY'
            elif 'BANKNIFTY' in self.file_name.upper():
                result.symbol = 'BANKNIFTY'
            
            # Extract expiry
            match = re.search(r'(\d{2})(\d{2})(\d{2})', self.file_name)
            if match:
                result.expiry = f"20{match.group(3)}-{match.group(2)}-{match.group(1)}"
        
        result.is_valid = len(result.errors) == 0
        return result
    
    def _find_atm_strike(self, df: pd.DataFrame) -> float:
        try:
            ce_oi = df.get('OI', pd.Series([0]*len(df))).fillna(0)
            pe_oi = df.get('OI.1', pd.Series([0]*len(df))).fillna(0)
            total = ce_oi + pe_oi
            if total.sum() == 0:
                return df['STRIKE PRICE'].iloc[len(df)//2]
            return df.loc[total.idxmax(), 'STRIKE PRICE']
        except:
            return df['STRIKE PRICE'].iloc[len(df)//2] if len(df) > 0 else 0