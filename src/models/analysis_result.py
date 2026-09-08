"""Analysis Result Models"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class FactorScore:
    factor_name: str
    bullish_score: float
    bearish_score: float
    weight: float
    bias: str
    reasoning: str = ""


@dataclass
class SupportLevel:
    strike: float
    strength: int
    pe_oi: int
    pe_chg_oi: int
    pe_volume: int
    status: str
    reasoning: str = ""


@dataclass
class ResistanceLevel:
    strike: float
    strength: int
    ce_oi: int
    ce_chg_oi: int
    ce_volume: int
    status: str
    reasoning: str = ""


@dataclass
class AnalysisResult:
    timestamp: datetime = field(default_factory=datetime.now)
    file_name: str = ""
    exchange: str = ""
    symbol: str = ""
    expiry: str = ""
    spot_price: float = 0.0
    atm_strike: float = 0.0
    
    # OI
    total_ce_oi: int = 0
    total_pe_oi: int = 0
    oi_pcr: float = 0.0
    highest_ce_oi_strike: float = 0.0
    highest_pe_oi_strike: float = 0.0
    oi_positioning_bias: str = "NEUTRAL"
    
    # ATM
    atm_ce_oi: int = 0
    atm_pe_oi: int = 0
    atm_ce_chg_oi: int = 0
    atm_pe_chg_oi: int = 0
    atm_ce_volume: int = 0
    atm_pe_volume: int = 0
    atm_ce_ltp: float = 0.0
    atm_pe_ltp: float = 0.0
    atm_ce_iv: float = 0.0
    atm_pe_iv: float = 0.0
    atm_bias: str = "NEUTRAL"
    
    # IV (NEW)
    iv_bias: str = "NEUTRAL"
    iv_skew_bias: str = "NEUTRAL"
    iv_skew_value: float = 0.0
    
    # S/R
    supports: List[SupportLevel] = field(default_factory=list)
    resistances: List[ResistanceLevel] = field(default_factory=list)
    support_resistance_bias: str = "NEUTRAL"
    
    # Max Pain
    max_pain_strike: float = 0.0
    max_pain_bias: str = "NEUTRAL"
    
    # Other biases
    pcr_bias: str = "NEUTRAL"
    volume_bias: str = "NEUTRAL"
    buildup_bias: str = "NEUTRAL"  # Not used in BSE
    
    # Factor scores
    factor_scores: List[FactorScore] = field(default_factory=list)
    
    # Final
    final_market: str = "NEUTRAL"
    confidence: float = 0.0
    bullish_score: float = 0.0
    bearish_score: float = 0.0
    
    # Reasons and data
    key_reasons: List[str] = field(default_factory=list)
    raw_strikes: List[Dict] = field(default_factory=list)
    
    # Internal
    _ce_volume: int = 0
    _pe_volume: int = 0
    _vol_pcr: float = 0.0
    _pain_values: Dict = field(default_factory=dict)