"""
Final Decision - Fetches from all 5 pages
100% Weightage Distribution
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FinalDecisionMaker:
    """
    Fetches results from all pages stored in session_state
    and combines them into final decision
    """
    
    # 5 Pages - 100% Weight Distribution
    PAGE_WEIGHTS = {
        'OI': 22,
        'Change_OI': 22,
        'Price_OI': 20,
        'Support_Resistance': 20,
        'PCR': 16
    }
    
    PAGE_NAMES = {
        'OI': '📈 OI Analysis',
        'Change_OI': '🔄 Change OI',
        'Price_OI': '📊 Price+OI',
        'Support_Resistance': '🎯 S/R',
        'PCR': '📉 PCR'
    }
    
    PAGE_ICONS = {
        'OI': '📈',
        'Change_OI': '🔄',
        'Price_OI': '📊',
        'Support_Resistance': '🎯',
        'PCR': '📉'
    }
    
    # Session keys for each page
    SESSION_KEYS = {
        'OI': 'oi_decision',
        'Change_OI': 'change_oi_decision',
        'Price_OI': 'price_oi_decision',
        'Support_Resistance': 'sr_decision',
        'PCR': 'pcr_decision'
    }
    
    def __init__(self):
        self.results = []
        self.final_decision = None
    
    def make_decision(self, result=None, df=None) -> dict:
        """
        Fetch from session_state and make final decision
        """
        logger.info("Making final decision from all pages...")
        
        # Fetch from session_state
        session_state = st.session_state
        
        modules = []
        
        for key, session_key in self.SESSION_KEYS.items():
            data = session_state.get(session_key, {'bias': 'NEUTRAL', 'score': 50, 'confidence': 50})
            weight = self.PAGE_WEIGHTS.get(key, 0)
            
            modules.append({
                'name': self.PAGE_NAMES.get(key, key),
                'icon': self.PAGE_ICONS.get(key, '📊'),
                'bias': data.get('bias', 'NEUTRAL'),
                'score': data.get('score', 50),
                'weight': weight,
                'confidence': data.get('confidence', 50)
            })
        
        self.results = modules
        
        # Calculate final decision
        final = self._calculate_final_decision(modules)
        self.final_decision = final
        
        return final
    
    def _calculate_final_decision(self, modules: List[dict]) -> dict:
        """Calculate final decision from all modules"""
        
        total_score = 0
        total_weight = 0
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for m in modules:
            weight = m['weight']
            score = m['score']
            
            total_weight += weight
            total_score += score * (weight / 100)
            
            if m['bias'] in ["BULLISH", "STRONG_BULLISH", "WEAK_BULLISH"]:
                bullish_count += 1
            elif m['bias'] in ["BEARISH", "STRONG_BEARISH", "WEAK_BEARISH"]:
                bearish_count += 1
            else:
                neutral_count += 1
        
        final_score = total_score
        
        # Determine final decision
        if final_score >= 80:
            overall_bias = "STRONG_BULLISH"
            emoji = "🚀"
            color = "#00C853"
        elif final_score >= 65:
            overall_bias = "BULLISH"
            emoji = "📈"
            color = "#00C853"
        elif final_score >= 55:
            overall_bias = "WEAK_BULLISH"
            emoji = "📈"
            color = "#66BB6A"
        elif final_score >= 45:
            overall_bias = "NEUTRAL"
            emoji = "➡️"
            color = "#FFD600"
        elif final_score >= 35:
            overall_bias = "WEAK_BEARISH"
            emoji = "📉"
            color = "#EF5350"
        elif final_score >= 20:
            overall_bias = "BEARISH"
            emoji = "📉"
            color = "#FF1744"
        else:
            overall_bias = "STRONG_BEARISH"
            emoji = "💀"
            color = "#FF1744"
        
        # Calculate confidence
        avg_confidence = sum(m['confidence'] for m in modules) / len(modules)
        agreement = max(bullish_count, bearish_count) / len(modules) if modules else 0
        confidence = (avg_confidence * 0.6) + (agreement * 100 * 0.4)
        confidence = min(100, confidence)
        
        return {
            'overall_bias': overall_bias,
            'overall_score': final_score,
            'confidence': confidence,
            'modules': modules,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'emoji': emoji,
            'color': color
        }
    
    def get_key_reasons(self) -> List[str]:
        """Generate key reasons for the final decision"""
        if not self.final_decision:
            return ["No analysis available"]
        
        reasons = []
        modules = self.final_decision.get('modules', [])
        
        # Sort by score deviation
        sorted_modules = sorted(modules, key=lambda x: abs(x['score'] - 50), reverse=True)
        
        for m in sorted_modules[:3]:
            if m['bias'] != "NEUTRAL":
                reasons.append(f"{m['name']}: {m['bias']} ({m['score']:.0f})")
        
        if not reasons:
            reasons.append("All modules are neutral - No clear direction")
        
        return reasons


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def get_final_decision(result=None, df=None) -> dict:
    """Convenience function to get final decision"""
    maker = FinalDecisionMaker()
    return maker.make_decision(result, df)


def get_key_reasons() -> List[str]:
    """Get key reasons for final decision"""
    maker = FinalDecisionMaker()
    return maker.get_key_reasons()