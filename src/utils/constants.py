"""Constants used throughout the application"""

# Column names in the option chain CSV
COL_CE_CHG_OI = "Chg in OI"
COL_CE_OI = "OI"
COL_CE_VOLUME = "VOLUME"
COL_CE_IV = "IV"
COL_CE_LTP = "LTP"
COL_CE_CHNG = "CHNG"
COL_CE_BID_QTY = "BID QTY"
COL_CE_BID_PRICE = "BID PRICE"
COL_CE_ASK_PRICE = "ASK PRICE"
COL_CE_ASK_QTY = "ASK QTY"
COL_STRIKE = "STRIKE PRICE"
COL_PE_BID_QTY = "BID QTY.1"
COL_PE_BID_PRICE = "BID PRICE.1"
COL_PE_ASK_PRICE = "ASK PRICE.1"
COL_PE_ASK_QTY = "ASK QTY.1"
COL_PE_CHNG = "CHNG.1"
COL_PE_LTP = "LTP.1"
COL_PE_IV = "IV.1"
COL_PE_VOLUME = "VOLUME.1"
COL_PE_OI = "OI.1"
COL_PE_CHG_OI = "Chg in OI.1"

# BSE format column mapping (for the specific CSV format)
BSE_COL_MAP = {
    "CE_Chg_in_OI": COL_CE_CHG_OI,
    "CE_OI": COL_CE_OI,
    "CE_VOLUME": COL_CE_VOLUME,
    "CE_IV": COL_CE_IV,
    "CE_LTP": COL_CE_LTP,
    "CE_CHNG": COL_CE_CHNG,
    "CE_BID_QTY": COL_CE_BID_QTY,
    "CE_BID_PRICE": COL_CE_BID_PRICE,
    "CE_ASK_PRICE": COL_CE_ASK_PRICE,
    "CE_ASK_QTY": COL_CE_ASK_QTY,
    "STRIKE": COL_STRIKE,
    "PE_BID_QTY": COL_PE_BID_QTY,
    "PE_BID_PRICE": COL_PE_BID_PRICE,
    "PE_ASK_PRICE": COL_PE_ASK_PRICE,
    "PE_ASK_QTY": COL_PE_ASK_QTY,
    "PE_CHNG": COL_PE_CHNG,
    "PE_LTP": COL_PE_LTP,
    "PE_IV": COL_PE_IV,
    "PE_VOLUME": COL_PE_VOLUME,
    "PE_OI": COL_PE_OI,
    "PE_Chg_in_OI": COL_PE_CHG_OI,
}

# Factor weights (sum to 100%)
FACTOR_WEIGHTS = {
    "OI Positioning": 18,
    "Change in OI": 18,
    "Price + OI / Buildup": 15,
    "Support / Resistance": 15,
    "PCR": 10,
    "Volume": 8,
    "IV": 5,
    "IV Skew": 3,
    "Max Pain": 3,
    "Expected Move": 3,
    "Liquidity": 2,
}

# Market classification thresholds
CLASSIFICATION = {
    "STRONG_BULLISH": {"min_score": 80, "min_agreement": 6},
    "BULLISH": {"min_score": 65, "min_agreement": 5},
    "WEAK_BULLISH": {"min_score": 50, "min_agreement": 4},
    "NEUTRAL": {"min_score": 35, "min_agreement": 3},
    "WEAK_BEARISH": {"min_score": 20, "min_agreement": 4},
    "BEARISH": {"min_score": 10, "min_agreement": 5},
    "STRONG_BEARISH": {"min_score": 0, "min_agreement": 6},
}

# Confidence levels
CONFIDENCE_LEVELS = {
    "EXTREMELY_HIGH": (90, 100),
    "VERY_HIGH": (80, 89),
    "HIGH": (70, 79),
    "MODERATE": (60, 69),
    "LOW": (50, 59),
    "VERY_LOW": (0, 49),
}