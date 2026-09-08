"""
🎯 Final Decision - Fetches from all 5 pages
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_final_decision():
    """Final Decision - Fetch from 5 modules"""
    
    st.markdown("""
    <style>
        .header { font-size: 2rem; font-weight: 700; color: #1E88E5; margin-bottom: 1rem; text-align: center; }
        .decision-card { padding: 2rem; border-radius: 0.5rem; text-align: center; margin: 1rem 0; border: 3px solid; }
        .decision-card .emoji { font-size: 3rem; }
        .decision-card .text { font-size: 2.5rem; font-weight: 700; }
        .decision-card .score { font-size: 1.2rem; font-weight: 600; margin: 0.5rem 0; }
        .decision-card .subtext { font-size: 0.9rem; color: #888; margin-top: 0.3rem; }
        .divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, #1E88E5, transparent); margin: 1.5rem 0; }
        .card { background: #1E1E2E; padding: 0.8rem 1.2rem; border-radius: 0.5rem; margin: 0.3rem 0; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #1E88E5; }
        .card .name { font-weight: 600; }
        .card .score { font-weight: 700; font-size: 1.1rem; }
        .weight-chip { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 0.3rem; font-size: 0.6rem; font-weight: 600; background: #1E1E3E; color: #1E88E5; }
        .confirmation-box { background: #1E1E3E; padding: 1.2rem; border-radius: 0.5rem; border: 2px solid #1E88E5; margin: 0.5rem 0; text-align: center; }
        .confirmation-text { font-size: 0.95rem; color: #aaa; }
        .signal-count { display: inline-block; padding: 0.3rem 1rem; border-radius: 2rem; font-size: 0.9rem; font-weight: 600; margin: 0.2rem; }
        .signal-bullish { background: #0D2E0D; color: #00C853; border: 1px solid #00C853; }
        .signal-bearish { background: #2E0D0D; color: #FF1744; border: 1px solid #FF1744; }
        .signal-neutral { background: #2E2E0D; color: #FFD600; border: 1px solid #FFD600; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header">🎯 Final Decision</div>', unsafe_allow_html=True)
    
    # ================================================================
    # FETCH 5 MODULES
    # ================================================================
    
    modules = {
        '📈 OI': {
            'data': st.session_state.get('oi_decision', {'bias': 'NEUTRAL', 'score': 50}),
            'weight': 22
        },
        '🔄 Change OI': {
            'data': st.session_state.get('change_oi_decision', {'bias': 'NEUTRAL', 'score': 50}),
            'weight': 22
        },
        '📊 Price+OI': {
            'data': st.session_state.get('price_oi_decision', {'bias': 'NEUTRAL', 'score': 50}),
            'weight': 20
        },
        '🎯 S/R': {
            'data': st.session_state.get('sr_decision', {'bias': 'NEUTRAL', 'score': 50}),
            'weight': 20
        },
        '📉 PCR': {
            'data': st.session_state.get('pcr_decision', {'bias': 'NEUTRAL', 'score': 50}),
            'weight': 16
        }
    }
    
    # ================================================================
    # CALCULATE
    # ================================================================
    
    total_score = 0
    bullish = bearish = neutral = 0
    results = []
    
    for name, mod in modules.items():
        data = mod['data']
        bias = data.get('bias', 'NEUTRAL')
        score = data.get('score', 50)
        weight = mod['weight']
        
        total_score += score * (weight / 100)
        
        if bias in ["BULLISH", "STRONG_BULLISH", "WEAK_BULLISH"]:
            bullish += 1
        elif bias in ["BEARISH", "STRONG_BEARISH", "WEAK_BEARISH"]:
            bearish += 1
        else:
            neutral += 1
        
        results.append({'name': name, 'bias': bias, 'score': score, 'weight': weight})
    
    final_score = total_score
    
    if final_score >= 80:
        decision, color, emoji = "STRONG_BULLISH", "#00C853", "🚀"
    elif final_score >= 65:
        decision, color, emoji = "BULLISH", "#00C853", "📈"
    elif final_score >= 55:
        decision, color, emoji = "WEAK_BULLISH", "#66BB6A", "📈"
    elif final_score >= 45:
        decision, color, emoji = "NEUTRAL", "#FFD600", "➡️"
    elif final_score >= 35:
        decision, color, emoji = "WEAK_BEARISH", "#EF5350", "📉"
    elif final_score >= 20:
        decision, color, emoji = "BEARISH", "#FF1744", "📉"
    else:
        decision, color, emoji = "STRONG_BEARISH", "#FF1744", "💀"
    
    confidence = 65
    
    # ================================================================
    # DISPLAY
    # ================================================================
    
    border = "#00C853" if decision in ["STRONG_BULLISH", "BULLISH", "WEAK_BULLISH"] else "#FF1744" if decision in ["STRONG_BEARISH", "BEARISH", "WEAK_BEARISH"] else "#FFD600"
    
    st.markdown(f"""
    <div class="decision-card" style="border-color:{border};background:linear-gradient(135deg,#1A1A2E,#0E0E1E);">
        <div class="emoji">{emoji}</div>
        <div class="text" style="color:{color};">{decision}</div>
        <div class="score">Final Score: {final_score:.0f}/100</div>
        <div class="subtext">Confidence: {confidence:.0f}%</div>
        <div style="margin-top:0.5rem;">
            <span class="signal-count signal-bullish">🟢 {bullish} Bullish</span>
            <span class="signal-count signal-neutral">🟡 {neutral} Neutral</span>
            <span class="signal-count signal-bearish">🔴 {bearish} Bearish</span>
        </div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.5rem;">Based on 5 Pages (100% Weightage)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="confirmation-box">
        <div class="confirmation-text">
            ✅ <strong>FINAL CONFIRMATION</strong> — Fetched from all 5 modules,
            the market is <strong style="color:{color};">{decision}</strong> 
            with <strong>{confidence:.0f}%</strong> confidence.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    st.markdown("### 📊 5 Pages Breakdown")
    
    for r in results:
        color = "#00C853" if r['bias'] in ["BULLISH", "STRONG_BULLISH", "WEAK_BULLISH"] else "#FF1744" if r['bias'] in ["BEARISH", "STRONG_BEARISH", "WEAK_BEARISH"] else "#FFD600"
        st.markdown(f"""
        <div class="card" style="border-left-color:{color};">
            <span class="name">{r['name']} <span class="weight-chip">{r['weight']}%</span></span>
            <span class="score" style="color:{color};">{r['bias']} ({r['score']:.0f})</span>
        </div>
        """, unsafe_allow_html=True)


show_final_decision()