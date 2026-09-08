from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StrikeData:
    """Represents data for a single strike price"""
    
    strike_price: float
    ce_oi: int = 0
    ce_chg_oi: int = 0
    ce_volume: int = 0
    ce_iv: float = 0.0
    ce_ltp: float = 0.0
    ce_chng: float = 0.0
    ce_bid_qty: int = 0
    ce_bid_price: float = 0.0
    ce_ask_price: float = 0.0
    ce_ask_qty: int = 0
    pe_oi: int = 0
    pe_chg_oi: int = 0
    pe_volume: int = 0
    pe_iv: float = 0.0
    pe_ltp: float = 0.0
    pe_chng: float = 0.0
    pe_bid_qty: int = 0
    pe_bid_price: float = 0.0
    pe_ask_price: float = 0.0
    pe_ask_qty: int = 0
    
    @property
    def total_oi(self) -> int:
        return self.ce_oi + self.pe_oi
    
    @property
    def total_volume(self) -> int:
        return self.ce_volume + self.pe_volume
    
    @property
    def pcr(self) -> float:
        if self.ce_oi == 0:
            return 0.0
        return self.pe_oi / self.ce_oi
    
    @property
    def pcr_change(self) -> float:
        if self.ce_chg_oi == 0:
            return 0.0
        return self.pe_chg_oi / self.ce_chg_oi
    
    @property
    def ce_oi_concentration(self) -> float:
        """CE OI as percentage of total OI at this strike"""
        if self.total_oi == 0:
            return 0.0
        return self.ce_oi / self.total_oi * 100
    
    @property
    def pe_oi_concentration(self) -> float:
        """PE OI as percentage of total OI at this strike"""
        if self.total_oi == 0:
            return 0.0
        return self.pe_oi / self.total_oi * 100