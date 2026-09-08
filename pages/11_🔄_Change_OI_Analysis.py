"""
🔄 Change OI Analysis - Simple Change OI
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_change_oi_analysis():
    """Simple Change OI Analysis"""
    
    df = st.session_state.get('df')
    result = st.session_state.get('result')
    
    if df is None or result is None:
        st.warning("⚠️ No data available.")
        return
    
    # ================================================================
    # FIND OI COLUMNS
    # ================================================================
    
    ce_oi_col = None
    pe_oi_col = None
    
    for col in df.columns:
        if col.strip() == "OI" or col.strip() == "OI_CE":
            ce_oi_col = col
        if col.strip() == "OI.1" or col.strip() == "OI_PE":
            pe_oi_col = col
    
    if ce_oi_col is None or pe_oi_col is None:
        st.warning("⚠️ OI columns not found.")
        return
    
    # ================================================================
    # CALCULATE CHANGE OI
    # ================================================================
    
    ce_oi = pd.to_numeric(df[ce_oi_col], errors='coerce').fillna(0)
    pe_oi = pd.to_numeric(df[pe_oi_col], errors='coerce').fillna(0)
    
    # Non-zero values
    ce_nonzero = ce_oi[ce_oi > 0]
    pe_nonzero = pe_oi[pe_oi > 0]
    
    if len(ce_nonzero) > 1:
        ce_chg = ce_nonzero.diff().fillna(0)
        ce_additions = ce_chg[ce_chg > 0].sum()
        ce_net = ce_nonzero.iloc[-1] - ce_nonzero.iloc[0]
        ce_first = ce_nonzero.iloc[0]
        ce_last = ce_nonzero.iloc[-1]
        ce_active = len(ce_nonzero)
    else:
        ce_additions = ce_net = ce_first = ce_last = 0
        ce_active = 0
    
    if len(pe_nonzero) > 1:
        pe_chg = pe_nonzero.diff().fillna(0)
        pe_additions = pe_chg[pe_chg > 0].sum()
        pe_net = pe_nonzero.iloc[-1] - pe_nonzero.iloc[0]
        pe_first = pe_nonzero.iloc[0]
        pe_last = pe_nonzero.iloc[-1]
        pe_active = len(pe_nonzero)
    else:
        pe_additions = pe_net = pe_first = pe_last = 0
        pe_active = 0
    
    change_pcr = pe_additions / ce_additions if ce_additions != 0 else 0
    
    # ================================================================
    # DETERMINE BIAS
    # ================================================================
    
    if change_pcr > 0.8:
        bias, score, color, emoji = "BULLISH", 70, "#00C853", "📈"
    elif change_pcr < 0.4:
        bias, score, color, emoji = "BEARISH", 30, "#FF1744", "📉"
    else:
        bias, score, color, emoji = "NEUTRAL", 50, "#FFD600", "➡️"
    
    st.session_state['change_oi_decision'] = {
        'bias': bias, 'score': score, 'confidence': 65
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
        .row { display: flex; justify-content: space-between; padding: 0.2rem 0; border-bottom: 1px solid #1A1A2E; }
        .row .label { color: #888; }
        .row .value { font-weight: 600; }
        .oi-box { background: #1E1E2E; padding: 0.8rem 1rem; border-radius: 0.5rem; }
        .oi-box .title { font-weight: 600; margin-bottom: 0.3rem; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header">🔄 Change OI Analysis</div>', unsafe_allow_html=True)
    
    border = "#00C853" if bias == "BULLISH" else "#FF1744" if bias == "BEARISH" else "#FFD600"
    
    st.markdown(f"""
    <div class="decision-card" style="border-color:{border};background:linear-gradient(135deg,#1A1A2E,#0E0E1E);">
        <div class="emoji">{emoji}</div>
        <div class="text" style="color:{color};">{bias}</div>
        <div class="subtext">Score: {score}/100 | Change PCR: {change_pcr:.2f}</div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.5rem;">22% Weight in Final Decision</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card"><div class="value" style="color:#00C853;">{ce_additions:+,.0f}</div><div class="label">📈 CE Additions</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card"><div class="value" style="color:#FF1744;">{pe_additions:+,.0f}</div><div class="label">📉 PE Additions</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card"><div class="value" style="color:#FFD600;">{change_pcr:.2f}</div><div class="label">🔄 Change PCR</div></div>', unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    # OI Summary
    st.markdown("### 📊 OI Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ce_net_color = "#00C853" if ce_net >= 0 else "#FF1744"
        st.markdown(f"""
        <div class="oi-box">
            <div class="title" style="color:#00C853;">📈 CE OI</div>
            <div class="row"><span class="label">First</span><span class="value">{ce_first:,.0f}</span></div>
            <div class="row"><span class="label">Last</span><span class="value">{ce_last:,.0f}</span></div>
            <div class="row"><span class="label">Net Change</span><span class="value" style="color:{ce_net_color};">{ce_net:+,.0f}</span></div>
            <div class="row"><span class="label">Active</span><span class="value">{ce_active}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pe_net_color = "#00C853" if pe_net >= 0 else "#FF1744"
        st.markdown(f"""
        <div class="oi-box">
            <div class="title" style="color:#FF1744;">📉 PE OI</div>
            <div class="row"><span class="label">First</span><span class="value">{pe_first:,.0f}</span></div>
            <div class="row"><span class="label">Last</span><span class="value">{pe_last:,.0f}</span></div>
            <div class="row"><span class="label">Net Change</span><span class="value" style="color:{pe_net_color};">{pe_net:+,.0f}</span></div>
            <div class="row"><span class="label">Active</span><span class="value">{pe_active}</span></div>
        </div>
        """, unsafe_allow_html=True)


show_change_oi_analysis()