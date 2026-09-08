"""
🎯 Support & Resistance - Simple
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_sr_analysis():
    """Simple S/R Analysis"""
    
    df = st.session_state.get('df')
    result = st.session_state.get('result')
    
    if df is None or result is None:
        st.warning("⚠️ No data available.")
        return
    
    supports = result.supports
    resistances = result.resistances
    
    if not supports and not resistances:
        bias, score, color, emoji = "NEUTRAL", 50, "#FFD600", "➡️"
    elif not supports:
        bias, score, color, emoji = "BEARISH", 25, "#FF1744", "📉"
    elif not resistances:
        bias, score, color, emoji = "BULLISH", 75, "#00C853", "📈"
    else:
        s_oi = supports[0].pe_oi
        r_oi = resistances[0].ce_oi
        if s_oi > r_oi * 1.2:
            bias, score, color, emoji = "BULLISH", 70, "#00C853", "📈"
        elif r_oi > s_oi * 1.2:
            bias, score, color, emoji = "BEARISH", 30, "#FF1744", "📉"
        else:
            bias, score, color, emoji = "NEUTRAL", 50, "#FFD600", "➡️"
    
    st.session_state['sr_decision'] = {'bias': bias, 'score': score, 'confidence': 65}
    
    st.markdown("""
    <style>
        .header { font-size: 1.8rem; font-weight: 700; color: #1E88E5; margin-bottom: 1rem; text-align: center; }
        .card { background: #1E1E2E; padding: 1.2rem; border-radius: 0.5rem; text-align: center; margin: 0.3rem 0; border-bottom: 3px solid #1E88E5; }
        .card .value { font-size: 1.8rem; font-weight: 700; }
        .card .label { font-size: 0.7rem; color: #888; text-transform: uppercase; }
        .decision-card { padding: 1.5rem; border-radius: 0.5rem; text-align: center; margin: 1rem 0; border: 3px solid; }
        .decision-card .emoji { font-size: 2.5rem; }
        .decision-card .text { font-size: 2rem; font-weight: 700; }
        .decision-card .subtext { font-size: 0.85rem; color: #888; margin-top: 0.3rem; }
        .divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, #1E88E5, transparent); margin: 1.5rem 0; }
        .sr-card { background: #1E1E2E; padding: 0.5rem 1rem; border-radius: 0.3rem; margin: 0.2rem 0; display: flex; justify-content: space-between; border-left: 3px solid #1E88E5; }
        .sr-support { border-left-color: #4ECDC4; }
        .sr-resistance { border-left-color: #FF6B6B; }
        .sr-card .strike { font-weight: 700; }
        .sr-card .oi { font-size: 0.8rem; color: #888; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header">🎯 Support & Resistance</div>', unsafe_allow_html=True)
    
    border = "#00C853" if bias == "BULLISH" else "#FF1744" if bias == "BEARISH" else "#FFD600"
    
    st.markdown(f"""
    <div class="decision-card" style="border-color:{border};background:linear-gradient(135deg,#1A1A2E,#0E0E1E);">
        <div class="emoji">{emoji}</div>
        <div class="text" style="color:{color};">{bias}</div>
        <div class="subtext">Score: {score}/100</div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.5rem;">15% Weight in Final Decision</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🟢 Supports")
        if supports:
            for s in supports[:3]:
                st.markdown(f'<div class="sr-card sr-support"><span class="strike">₹{s.strike:,.0f}</span><span class="oi">PE: {s.pe_oi:,.0f}</span></div>', unsafe_allow_html=True)
        else:
            st.write("No supports")
    
    with col2:
        st.markdown("#### 🔴 Resistances")
        if resistances:
            for r in resistances[:3]:
                st.markdown(f'<div class="sr-card sr-resistance"><span class="strike">₹{r.strike:,.0f}</span><span class="oi">CE: {r.ce_oi:,.0f}</span></div>', unsafe_allow_html=True)
        else:
            st.write("No resistances")


show_sr_analysis()