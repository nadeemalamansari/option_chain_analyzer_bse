"""
Sentiment Analysis Module - Complete Sentiment Analysis
11% Weight - All sentiment factors with final output
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    overall_sentiment: str  # STRONG_BULLISH, BULLISH, WEAK_BULLISH, NEUTRAL, WEAK_BEARISH, BEARISH, STRONG_BEARISH
    sentiment_score: float  # -100 to +100
    oi_sentiment: str
    change_oi_sentiment: str
    price_oi_sentiment: str
    support_resistance_sentiment: str
    pcr_sentiment: str
    volume_sentiment: str
    atm_sentiment: str
    ce_pe_dominance: str
    bullish_signals: int
    bearish_signals: int
    conflicting_signals: int
    factors: Dict[str, float]
    key_drivers: List[str]
    confidence: float


class SentimentAnalyzer:
    """
    Sentiment Analyzer for Option Chain Data.
    Analyzes 8 factors to determine overall market sentiment.
    """
    
    def __init__(self):
        self.result = SentimentResult(
            overall_sentiment="NEUTRAL",
            sentiment_score=0.0,
            oi_sentiment="NEUTRAL",
            change_oi_sentiment="NEUTRAL",
            price_oi_sentiment="NEUTRAL",
            support_resistance_sentiment="NEUTRAL",
            pcr_sentiment="NEUTRAL",
            volume_sentiment="NEUTRAL",
            atm_sentiment="NEUTRAL",
            ce_pe_dominance="NEUTRAL",
            bullish_signals=0,
            bearish_signals=0,
            conflicting_signals=0,
            factors={},
            key_drivers=[],
            confidence=0.0
        )
    
    def analyze(self, result, df: pd.DataFrame) -> SentimentResult:
        """
        Perform comprehensive sentiment analysis.
        
        Args:
            result: AnalysisResult from main analyzer
            df: Original dataframe with option chain data
        
        Returns:
            SentimentResult: Complete sentiment analysis
        """
        logger.info("Starting Sentiment Analysis")
        
        sentiment_scores = {}
        
        # ====================================================================
        # FACTOR 1: OI Sentiment
        # ====================================================================
        oi_sent = self._analyze_oi_sentiment(result)
        sentiment_scores["OI"] = oi_sent
        
        # ====================================================================
        # FACTOR 2: Change OI Sentiment
        # ====================================================================
        change_oi_sent = self._analyze_change_oi_sentiment(result)
        sentiment_scores["Change_OI"] = change_oi_sent
        
        # ====================================================================
        # FACTOR 3: Price + OI Sentiment (Buildup)
        # ====================================================================
        price_oi_sent = self._analyze_buildup_sentiment(result)
        sentiment_scores["Price_OI"] = price_oi_sent
        
        # ====================================================================
        # FACTOR 4: Support/Resistance Sentiment
        # ====================================================================
        sr_sent = self._analyze_support_resistance_sentiment(result)
        sentiment_scores["Support_Resistance"] = sr_sent
        
        # ====================================================================
        # FACTOR 5: PCR Sentiment
        # ====================================================================
        pcr_sent = self._analyze_pcr_sentiment(result)
        sentiment_scores["PCR"] = pcr_sent
        
        # ====================================================================
        # FACTOR 6: Volume Sentiment
        # ====================================================================
        volume_sent = self._analyze_volume_sentiment(result)
        sentiment_scores["Volume"] = volume_sent
        
        # ====================================================================
        # FACTOR 7: ATM Sentiment
        # ====================================================================
        atm_sent = self._analyze_atm_sentiment(result)
        sentiment_scores["ATM"] = atm_sent
        
        # ====================================================================
        # FACTOR 8: CE vs PE Dominance
        # ====================================================================
        ce_pe_sent = self._analyze_ce_pe_dominance(result)
        sentiment_scores["CE_PE_Dominance"] = ce_pe_sent
        
        # ====================================================================
        # CALCULATE OVERALL SENTIMENT
        # ====================================================================
        
        # Calculate overall score
        overall_score = sum(sentiment_scores.values()) / len(sentiment_scores)
        
        # Count signals (Factors 9, 10, 11)
        bullish_count = 0
        bearish_count = 0
        conflicting_count = 0
        
        for score in sentiment_scores.values():
            if score > 20:
                bullish_count += 1
            elif score < -20:
                bearish_count += 1
            else:
                conflicting_count += 1
        
        # Determine overall sentiment (Factor 12)
        if overall_score > 65:
            overall_sentiment = "STRONG_BULLISH"
        elif overall_score > 45:
            overall_sentiment = "BULLISH"
        elif overall_score > 35:
            overall_sentiment = "WEAK_BULLISH"
        elif overall_score < -65:
            overall_sentiment = "STRONG_BEARISH"
        elif overall_score < -45:
            overall_sentiment = "BEARISH"
        elif overall_score < -35:
            overall_sentiment = "WEAK_BEARISH"
        else:
            overall_sentiment = "NEUTRAL"
        
        # Get key drivers
        key_drivers = self._get_key_drivers(sentiment_scores)
        
        # Calculate confidence
        confidence = self._calculate_confidence(sentiment_scores)
        
        self.result = SentimentResult(
            overall_sentiment=overall_sentiment,
            sentiment_score=overall_score,
            oi_sentiment=self._score_to_sentiment(sentiment_scores.get("OI", 0)),
            change_oi_sentiment=self._score_to_sentiment(sentiment_scores.get("Change_OI", 0)),
            price_oi_sentiment=self._score_to_sentiment(sentiment_scores.get("Price_OI", 0)),
            support_resistance_sentiment=self._score_to_sentiment(sentiment_scores.get("Support_Resistance", 0)),
            pcr_sentiment=self._score_to_sentiment(sentiment_scores.get("PCR", 0)),
            volume_sentiment=self._score_to_sentiment(sentiment_scores.get("Volume", 0)),
            atm_sentiment=self._score_to_sentiment(sentiment_scores.get("ATM", 0)),
            ce_pe_dominance=self._score_to_sentiment(sentiment_scores.get("CE_PE_Dominance", 0)),
            bullish_signals=bullish_count,
            bearish_signals=bearish_count,
            conflicting_signals=conflicting_count,
            factors=sentiment_scores,
            key_drivers=key_drivers,
            confidence=confidence
        )
        
        logger.info(f"Sentiment Analysis Complete: {overall_sentiment} (Score: {overall_score:.1f})")
        return self.result
    
    # ========================================================================
    # FACTOR 1: OI Sentiment
    # ========================================================================
    
    def _analyze_oi_sentiment(self, result) -> float:
        """Analyze OI sentiment"""
        if result.total_ce_oi == 0 and result.total_pe_oi == 0:
            return 0
        
        oi_pcr = result.oi_pcr
        
        if oi_pcr > 0.8:
            return -50  # Strong Bearish
        elif oi_pcr > 0.7:
            return -40  # Bearish
        elif oi_pcr > 0.6:
            return -20  # Weak Bearish
        elif oi_pcr < 0.2:
            return 50   # Strong Bullish
        elif oi_pcr < 0.3:
            return 40   # Bullish
        elif oi_pcr < 0.4:
            return 20   # Weak Bullish
        else:
            return 0    # Neutral
    
    # ========================================================================
    # FACTOR 2: Change OI Sentiment
    # ========================================================================
    
    def _analyze_change_oi_sentiment(self, result) -> float:
        """Analyze Change OI sentiment"""
        if result.total_ce_chg_oi == 0 and result.total_pe_chg_oi == 0:
            return 0
        
        change_pcr = result.change_oi_pcr
        
        if change_pcr > 1.2:
            return 40  # Bullish (More PE additions = Hedging)
        elif change_pcr > 0.9:
            return 20  # Weak Bullish
        elif change_pcr < 0.3:
            return -40 # Bearish (More CE additions = Call selling)
        elif change_pcr < 0.5:
            return -20 # Weak Bearish
        else:
            return 0   # Neutral
    
    # ========================================================================
    # FACTOR 3: Price + OI Sentiment (Buildup)
    # ========================================================================
    
    def _analyze_buildup_sentiment(self, result) -> float:
        """Analyze Price + OI sentiment"""
        if not result.call_buildup and not result.put_buildup:
            return 0
        
        call_short = len(result.call_buildup.get("short_buildup", []))
        put_short = len(result.put_buildup.get("short_buildup", []))
        call_long = len(result.call_buildup.get("long_buildup", []))
        put_long = len(result.put_buildup.get("long_buildup", []))
        
        # Bullish signals: Put Short Buildup + Call Long Buildup
        bullish_score = put_short * 2 + call_long * 1.5
        
        # Bearish signals: Call Short Buildup + Put Long Buildup
        bearish_score = call_short * 2 + put_long * 1.5
        
        if bullish_score > bearish_score + 5:
            return min(50, bullish_score)
        elif bearish_score > bullish_score + 5:
            return max(-50, -bearish_score)
        else:
            return 0
    
    # ========================================================================
    # FACTOR 4: Support/Resistance Sentiment
    # ========================================================================
    
    def _analyze_support_resistance_sentiment(self, result) -> float:
        """Analyze Support/Resistance sentiment"""
        if not result.supports and not result.resistances:
            return 0
        
        if not result.supports:
            return -30  # No support = Bearish
        if not result.resistances:
            return 30   # No resistance = Bullish
        
        support_oi = result.supports[0].pe_oi if result.supports else 0
        resistance_oi = result.resistances[0].ce_oi if result.resistances else 0
        
        if support_oi == 0 and resistance_oi == 0:
            return 0
        
        ratio = support_oi / (support_oi + resistance_oi) if (support_oi + resistance_oi) > 0 else 0.5
        score = (ratio - 0.5) * 100
        
        return max(-50, min(50, score))
    
    # ========================================================================
    # FACTOR 5: PCR Sentiment
    # ========================================================================
    
    def _analyze_pcr_sentiment(self, result) -> float:
        """Analyze PCR sentiment"""
        pcr = result.oi_pcr
        
        if pcr > 0.8:
            return -40
        elif pcr > 0.7:
            return -30
        elif pcr > 0.6:
            return -15
        elif pcr < 0.2:
            return 40
        elif pcr < 0.3:
            return 30
        elif pcr < 0.4:
            return 15
        else:
            return 0
    
    # ========================================================================
    # FACTOR 6: Volume Sentiment
    # ========================================================================
    
    def _analyze_volume_sentiment(self, result) -> float:
        """Analyze Volume sentiment"""
        ce_vol = getattr(result, '_ce_volume', 0) or result.atm_ce_volume or 0
        pe_vol = getattr(result, '_pe_volume', 0) or result.atm_pe_volume or 0
        
        if ce_vol == 0 and pe_vol == 0:
            return 0
        
        vol_pcr = pe_vol / ce_vol if ce_vol > 0 else 0
        
        if vol_pcr > 1.5:
            return -30
        elif vol_pcr > 1.2:
            return -20
        elif vol_pcr > 0.9:
            return -10
        elif vol_pcr < 0.4:
            return 30
        elif vol_pcr < 0.5:
            return 20
        elif vol_pcr < 0.7:
            return 10
        else:
            return 0
    
    # ========================================================================
    # FACTOR 7: ATM Sentiment
    # ========================================================================
    
    def _analyze_atm_sentiment(self, result) -> float:
        """Analyze ATM sentiment"""
        if result.atm_ce_oi == 0 and result.atm_pe_oi == 0:
            return 0
        
        # PE OI > CE OI at ATM = Bullish
        if result.atm_pe_oi > result.atm_ce_oi * 1.3:
            atm_score = 25
        elif result.atm_ce_oi > result.atm_pe_oi * 1.3:
            atm_score = -25
        else:
            atm_score = 0
        
        # Check Change OI
        if result.atm_pe_chg_oi > result.atm_ce_chg_oi * 1.5:
            chg_score = 15
        elif result.atm_ce_chg_oi > result.atm_pe_chg_oi * 1.5:
            chg_score = -15
        else:
            chg_score = 0
        
        return (atm_score * 0.7) + (chg_score * 0.3)
    
    # ========================================================================
    # FACTOR 8: CE vs PE Dominance
    # ========================================================================
    
    def _analyze_ce_pe_dominance(self, result) -> float:
        """Analyze CE vs PE dominance"""
        if result.total_ce_oi == 0 and result.total_pe_oi == 0:
            return 0
        
        ratio = result.total_ce_oi / result.total_pe_oi if result.total_pe_oi > 0 else 0
        
        if ratio > 2.0:
            return -50  # CE dominates = Bearish
        elif ratio > 1.5:
            return -30
        elif ratio > 1.2:
            return -15
        elif ratio < 0.5:
            return 50   # PE dominates = Bullish
        elif ratio < 0.7:
            return 30
        elif ratio < 0.9:
            return 15
        else:
            return 0
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _score_to_sentiment(self, score: float) -> str:
        """Convert numeric score to sentiment string"""
        if score > 45:
            return "BULLISH"
        elif score > 20:
            return "WEAK_BULLISH"
        elif score < -45:
            return "BEARISH"
        elif score < -20:
            return "WEAK_BEARISH"
        else:
            return "NEUTRAL"
    
    def _get_key_drivers(self, scores: Dict[str, float]) -> List[str]:
        """Get key drivers contributing to sentiment"""
        sorted_factors = sorted(scores.items(), key=lambda x: abs(x[1]), reverse=True)
        
        drivers = []
        for factor, score in sorted_factors[:3]:
            if abs(score) > 15:
                sentiment = "Bullish" if score > 0 else "Bearish"
                drivers.append(f"{factor}: {sentiment} ({score:+.1f})")
        
        return drivers
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate confidence based on factor agreement"""
        if not scores:
            return 0
        
        bullish = sum(1 for s in scores.values() if s > 15)
        bearish = sum(1 for s in scores.values() if s < -15)
        neutral = sum(1 for s in scores.values() if -15 <= s <= 15)
        
        total = len(scores)
        if total == 0:
            return 0
        
        max_agree = max(bullish, bearish)
        agreement = max_agree / total
        
        confidence = agreement * 100
        
        if max_agree >= 5:
            confidence += 10
        
        if neutral / total > 0.5:
            confidence *= 0.7
        
        return min(100, max(0, confidence))