"""
📈 OI Analysis - Simple Open Interest Analysis
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_oi_analysis():
    """Simple OI Analysis Page"""
    
    df = st.session_state.get('df')
    result = st.session_state.get('result')
    
    if df is None or result is None:
        st.warning("⚠️ No data available. Please upload and analyze a CSV file.")
        return
    
    # ================================================================
    # CALCULATE OI METRICS
    # ================================================================
    
    total_ce = result.total_ce_oi
    total_pe = result.total_pe_oi
    oi_pcr = result.oi_pcr
    
    # Determine Bias
    if total_ce > total_pe * 1.5:
        bias, score, color, emoji = "BEARISH", 30, "#FF1744", "📉"
    elif total_pe > total_ce * 1.5:
        bias, score, color, emoji = "BULLISH", 70, "#00C853", "📈"
    else:
        bias, score, color, emoji = "NEUTRAL", 50, "#FFD600", "➡️"
    
    # ================================================================
    # STORE IN SESSION FOR FINAL DECISION
    # ================================================================
    
    st.session_state['oi_decision'] = {'bias': bias, 'score': score, 'confidence': 70}
    
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
        .row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #1A1A2E; }
        .row .label { color: #888; }
        .row .value { font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header">📈 Open Interest Analysis</div>', unsafe_allow_html=True)
    
    border = "#FF1744" if bias == "BEARISH" else "#00C853" if bias == "BULLISH" else "#FFD600"
    
    st.markdown(f"""
    <div class="decision-card" style="border-color:{border};background:linear-gradient(135deg,#1A1A2E,#0E0E1E);">
        <div class="emoji">{emoji}</div>
        <div class="text" style="color:{color};">{bias}</div>
        <div class="subtext">Score: {score}/100 | PCR: {oi_pcr:.2f}</div>
        <div style="font-size:0.8rem;color:#666;margin-top:0.5rem;">22% Weight in Final Decision</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card"><div class="value" style="color:#00C853;">{total_ce:,.0f}</div><div class="label">📈 Total CE OI</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card"><div class="value" style="color:#FF1744;">{total_pe:,.0f}</div><div class="label">📉 Total PE OI</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card"><div class="value" style="color:#FFD600;">{oi_pcr:.2f}</div><div class="label">🔄 OI PCR</div></div>', unsafe_allow_html=True)
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    # OI Details
    st.markdown("### 📊 OI Details")
    
    details = [
        ("Highest CE OI", f"₹{result.highest_ce_oi_strike:,.0f}"),
        ("Highest PE OI", f"₹{result.highest_pe_oi_strike:,.0f}"),
        ("ATM CE OI", f"{result.atm_ce_oi:,.0f}"),
        ("ATM PE OI", f"{result.atm_pe_oi:,.0f}"),
        ("OI Positioning", result.oi_positioning_bias)
    ]
    
    for label, value in details:
        st.markdown(f'<div class="row"><span class="label">{label}</span><span class="value">{value}</span></div>', unsafe_allow_html=True)


show_oi_analysis()