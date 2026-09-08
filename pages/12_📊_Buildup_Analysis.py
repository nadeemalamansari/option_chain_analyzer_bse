"""
📊 Price + OI / Buildup - Simple
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_buildup_analysis():
    """Simple Buildup Analysis"""
    
    df = st.session_state.get('df')
    result = st.session_state.get('result')
    
    if df is None or result is None:
        st.warning("⚠️ No data available.")
        return
    
    # ================================================================
    # FIND COLUMNS
    # ================================================================
    
    strike_col = "STRIKE PRICE" if "STRIKE PRICE" in df.columns else None
    
    ce_oi_col = None
    ce_ltp_col = None
    pe_oi_col = None
    pe_ltp_col = None
    
    for col in df.columns:
        if col.strip() == "OI" or col.strip() == "OI_CE":
            ce_oi_col = col
        if col.strip() == "LTP" or col.strip() == "LTP_CE":
            ce_ltp_col = col
        if col.strip() == "OI.1" or col.strip() == "OI_PE":
            pe_oi_col = col
        if col.strip() == "LTP.1" or col.strip() == "LTP_PE":
            pe_ltp_col = col
    
    if ce_oi_col is None or pe_oi_col is None:
        st.warning("⚠️ OI columns not found.")
        return
    
    # ================================================================
    # CALCULATE BUILDUP
    # ================================================================
    
    strikes = pd.to_numeric(df[strike_col], errors='coerce').fillna(0)
    ce_oi = pd.to_numeric(df[ce_oi_col], errors='coerce').fillna(0)
    pe_oi = pd.to_numeric(df[pe_oi_col], errors='coerce').fillna(0)
    
    if ce_ltp_col:
        ce_ltp = pd.to_numeric(df[ce_ltp_col], errors='coerce').fillna(0)
    else:
        ce_ltp = strikes
    
    if pe_ltp_col:
        pe_ltp = pd.to_numeric(df[pe_ltp_col], errors='coerce').fillna(0)
    else:
        pe_ltp = strikes
    
    ce_chng = ce_ltp.diff().fillna(0)
    pe_chng = pe_ltp.diff().fillna(0)
    
    ce_oi_chg = ce_oi.diff().fillna(0)
    pe_oi_chg = pe_oi.diff().fillna(0)
    
    call_long = call_short = put_long = put_short = 0
    
    for i in range(len(strikes)):
        if ce_oi.iloc[i] > 0 and abs(ce_oi_chg.iloc[i]) > 10:
            if ce_chng.iloc[i] > 0 and ce_oi_chg.iloc[i] > 0:
                call_long += 1
            elif ce_chng.iloc[i] < 0 and ce_oi_chg.iloc[i] > 0:
                call_short += 1
        
        if pe_oi.iloc[i] > 0 and abs(pe_oi_chg.iloc[i]) > 10:
            if pe_chng.iloc[i] < 0 and pe_oi_chg.iloc[i] > 0:
                put_short += 1
            elif pe_chng.iloc[i] > 0 and pe_oi_chg.iloc[i] > 0:
                put_long += 1
    
    bullish_score = put_short * 2 + call_long * 1.5
    bearish_score = call_short * 2 + put_long * 1.5
    
    if bullish_score > bearish_score + 5:
        bias, score, color, emoji = "BULLISH", 70, "#00C853", "📈"
    elif bearish_score > bullish_score + 5:
        bias, score, color, emoji = "BEARISH", 30, "#FF1744", "📉"
    else:
        bias, score, color, emoji = "NEUTRAL", 50, "#FFD600", "➡️"
    
    st.session_state['price_oi_decision'] = {
        'bias': bias, 'score': score, 'confidence': 60
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
        .pattern { background: #1A1A2E; padding: 0.5rem 1rem; border-radius: 0.3rem; margin: 0.2rem 0; display: flex; justify-content: space-between; border-left: 3px solid #1E88E5; }
        .pattern-bullish { border-left-color: #00C853; }
        .pattern-bearish { border-left-color: #FF1744; }
        .pattern .name { font-weight: 600; }
        .pattern .count { font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header">📊 Price + OI / Buildup</div>', unsafe_allow_html=True)
    
    border = "#00C853" if bias == "BULLISH" else "#FF1744" if bias == "BEARISH" else "#FFD600"
    
    st.markdown(f"""
    <div class="decision-card" style="border-color:{border};background:linear-gradient(135deg,#1A1A2E,#0E0E1E);">
        <div class="emoji">{emoji}</div>
        <div class="text" style="color:{color};">{bias}</div>
        <div class="subtext">Score: {score}/100 | Net: {bullish_score - bearish_score:+.0f}</div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.5rem;">15% Weight in Final Decision</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Call Side")
        st.markdown(f'<div class="pattern pattern-bullish"><span class="name">🟢 Long Buildup</span><span class="count">{call_long}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="pattern pattern-bearish"><span class="name">🔴 Short Buildup</span><span class="count">{call_short}</span></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📉 Put Side")
        st.markdown(f'<div class="pattern pattern-bearish"><span class="name">🔴 Long Buildup</span><span class="count">{put_long}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="pattern pattern-bullish"><span class="name">🟢 Short Buildup</span><span class="count">{put_short}</span></div>', unsafe_allow_html=True)


show_buildup_analysis()