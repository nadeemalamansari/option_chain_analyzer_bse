"""Option Chain Model"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
import pandas as pd


@dataclass
class OptionChain:
    """Represents an option chain data structure"""
    
    exchange: str = ""
    symbol: str = ""
    expiry: str = ""
    spot_price: Optional[float] = None
    atm_strike: Optional[float] = None
    strike_range: List[float] = field(default_factory=list)
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    
    def to_dict(self) -> Dict:
        return {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "expiry": self.expiry,
            "spot_price": self.spot_price,
            "atm_strike": self.atm_strike,
            "strike_range": self.strike_range,
            "data": self.data.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "OptionChain":
        return cls(
            exchange=data.get("exchange", ""),
            symbol=data.get("symbol", ""),
            expiry=data.get("expiry", ""),
            spot_price=data.get("spot_price"),
            atm_strike=data.get("atm_strike"),
            strike_range=data.get("strike_range", []),
            data=pd.DataFrame(data.get("data", {}))
        )