"""
📉 PCR Analysis - Simple PCR
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_pcr_analysis():
    """Simple PCR Analysis"""
    
    df = st.session_state.get('df')
    result = st.session_state.get('result')
    
    if df is None or result is None:
        st.warning("⚠️ No data available.")
        return
    
    pcr = result.oi_pcr
    
    # ================================================================
    # PCR CONDITIONS
    # ================================================================
    
    if pcr < 0.70:
        bias, score, color, emoji = "BEARISH", 25, "#FF1744", "🔴"
    elif pcr < 0.90:
        bias, score, color, emoji = "WEAK_BEARISH", 40, "#FF8A65", "🟠"
    elif pcr < 1.10:
        bias, score, color, emoji = "NEUTRAL", 50, "#FFD600", "⚪"
    elif pcr < 1.30:
        bias, score, color, emoji = "WEAK_BULLISH", 65, "#66BB6A", "🟢"
    else:
        bias, score, color, emoji = "BULLISH", 80, "#00C853", "🟢"
    
    # ================================================================
    # STORE IN SESSION
    # ================================================================
    
    st.session_state['pcr_decision'] = {
        'bias': bias, 
        'score': score, 
        'confidence': 70
    }
    
    # ================================================================
    # DISPLAY
    # ================================================================
    
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
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header">📉 PCR Analysis</div>', unsafe_allow_html=True)
    
    border = "#FF1744" if bias == "BEARISH" else "#FF8A65" if bias == "WEAK_BEARISH" else "#FFD600" if bias == "NEUTRAL" else "#66BB6A" if bias == "WEAK_BULLISH" else "#00C853"
    
    st.markdown(f"""
    <div class="decision-card" style="border-color:{border};background:linear-gradient(135deg,#1A1A2E,#0E0E1E);">
        <div class="emoji">{emoji}</div>
        <div class="text" style="color:{color};">{bias}</div>
        <div class="subtext">Score: {score}/100 | PCR: {pcr:.2f}</div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.5rem;">10% Weight in Final Decision</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card"><div class="value" style="color:#FFD600;">{pcr:.2f}</div><div class="label">📈 OI PCR</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card"><div class="value" style="color:#00C853;">{result.total_ce_oi:,.0f}</div><div class="label">📊 CE OI</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card"><div class="value" style="color:#FF1744;">{result.total_pe_oi:,.0f}</div><div class="label">📊 PE OI</div></div>', unsafe_allow_html=True)


show_pcr_analysis()