"""
Main Streamlit Application - NSE/BSE Option Chain Analyzer
Auto-analyze on upload - No extra buttons
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os
import traceback
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data_loader import DataLoader
from src.core.data_validator import DataValidator
from src.core.analyzer import Analyzer

# Page configuration
st.set_page_config(
    page_title="NSE/BSE Option Chain Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    
    .report-box {
        background: #0E0E1E;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #1E88E5;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #ccc;
        white-space: pre-wrap;
        max-height: 700px;
        overflow-y: auto;
        line-height: 1.6;
    }
    
    .error-box {
        background: #2E1E1E;
        border: 1px solid #FF1744;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .welcome-box {
        background: linear-gradient(135deg, #1E1E3E, #0E0E1E);
        padding: 3rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 2px dashed #1E88E5;
        margin: 2rem 0;
    }
    .welcome-box .icon { font-size: 4rem; }
    .welcome-box .title { font-size: 2rem; font-weight: 700; color: #1E88E5; margin-top: 1rem; }
    .welcome-box .subtitle { font-size: 1rem; color: #888; margin-top: 0.5rem; }
    
    .divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #1E88E5, transparent);
        margin: 1.5rem 0;
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.5rem;
        margin: 1rem 0;
    }
    @media (max-width: 768px) {
        .metric-grid { grid-template-columns: repeat(3, 1fr); }
    }
    .metric-card {
        background: #1E1E2E;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border-bottom: 3px solid #1E88E5;
    }
    .metric-card .value { font-size: 1.5rem; font-weight: 700; }
    .metric-card .label { font-size: 0.7rem; color: #888; text-transform: uppercase; }
    
    .stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: 600;
        padding: 0.6rem;
    }
    .stButton > button:hover { background-color: #1565C0; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
    st.session_state.result = None
    st.session_state.df = None
    st.session_state.filename = None
    st.session_state.error = None
    st.session_state.validation = None
    st.session_state.analysis = None
    st.session_state.uploaded_file = None


def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<div class="main-header">📊 NSE/BSE Option Chain Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload your Option Chain CSV file for automatic analysis</div>')
    
    # Sidebar - File Upload
    with st.sidebar:
        st.markdown("### 📁 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose an option chain CSV file",
            type=['csv', 'xlsx', 'xls', 'tsv'],
            help="Upload option chain data in NSE/BSE format (21 columns)"
        )
        
        # Auto-analyze when file is uploaded
        if uploaded_file is not None:
            # Check if this is a new file
            if st.session_state.uploaded_file != uploaded_file.name:
                st.session_state.uploaded_file = uploaded_file.name
                st.session_state.analyzed = False
                st.session_state.error = None
                
                with st.spinner("🔄 Analyzing option chain data..."):
                    analyze_file(uploaded_file)
                st.rerun()
            
            if st.session_state.analyzed and st.session_state.result:
                st.success(f"✅ Analyzed: {uploaded_file.name}")
                st.info(f"Size: {uploaded_file.size / 1024:.1f} KB")
            elif st.session_state.error:
                st.error("❌ Analysis failed")
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.markdown("""
        This tool analyzes Option Chain data to provide:
        - Open Interest Analysis
        - Put-Call Ratio (PCR)
        - Support & Resistance Levels
        - Max Pain Calculation
        - Volume Analysis
        - IV Analysis
        - Liquidity Analysis
        - Sentiment Analysis
        """)
        
        st.markdown("### 📁 Supported Format")
        st.markdown("""
        **BSE 21-Column Format:**
        - Columns 0-10: CALLS side
        - Column 11: STRIKE PRICE
        - Columns 12-21: PUTS side
        """)
        
        # Show status if analyzed
        if st.session_state.analyzed and st.session_state.result:
            st.markdown("---")
            st.markdown("### 📈 Current Analysis")
            st.markdown(f"**Symbol:** {st.session_state.result.symbol}")
            st.markdown(f"**Expiry:** {st.session_state.result.expiry}")
            st.markdown(f"**Spot:** ₹{st.session_state.result.spot_price:,.2f}")
            st.markdown(f"**ATM:** {st.session_state.result.atm_strike:,.0f}")
            
            if st.session_state.validation:
                v = st.session_state.validation
                st.markdown(f"**Strikes:** {v.num_strikes}")
                st.markdown(f"**Range:** {v.strike_range[0]:,.0f} - {v.strike_range[1]:,.0f}")
    
    # Main content area
    if st.session_state.error:
        display_error(st.session_state.error)
    elif st.session_state.analyzed and st.session_state.result:
        display_report(st.session_state.result)
    else:
        display_welcome()


def analyze_file(uploaded_file):
    """Analyze uploaded file - Auto-called on upload"""
    
    try:
        # Load data
        loader = DataLoader()
        success, message, df = loader.load_from_file(uploaded_file)
        
        if not success:
            st.session_state.error = f"❌ {message}"
            st.session_state.analyzed = False
            return
        
        # Preprocess
        df = loader.preprocess(df)
        
        # Validate
        validator = DataValidator()
        validator.file_name = uploaded_file.name
        validation = validator.validate(df)
        
        st.session_state.validation = validation
        
        # Check validation result
        if not validation.is_valid:
            error_msg = "⚠️ Validation failed:"
            if hasattr(validation, 'errors') and validation.errors:
                error_msg += "\n" + "\n".join(validation.errors)
            if hasattr(validation, 'warnings') and validation.warnings:
                error_msg += "\n\nWarnings:\n" + "\n".join(validation.warnings)
            st.session_state.error = error_msg
            st.session_state.analyzed = False
            return
        
        # Get option chain
        option_chain = loader.get_option_chain(df, uploaded_file.name)
        
        # Analyze
        analyzer = Analyzer()
        result = analyzer.analyze(option_chain, uploaded_file.name)
        
        # Build analysis for dashboard
        analysis = build_analysis(result, df)
        
        # Store in session
        st.session_state.analyzed = True
        st.session_state.result = result
        st.session_state.df = df
        st.session_state.filename = uploaded_file.name
        st.session_state.analysis = analysis
        st.session_state.error = None
        
    except Exception as e:
        st.session_state.error = f"❌ Error during analysis: {str(e)}"
        st.session_state.analyzed = False


def build_analysis(result, df):
    """Build analysis dictionary from result object"""
    
    def get_score(factor_name):
        for s in result.factor_scores:
            if s.factor_name == factor_name:
                return s.bullish_score
        return 50
    
    def get_bias(factor_name):
        for s in result.factor_scores:
            if s.factor_name == factor_name:
                return s.bias
        return 'Neutral'
    
    # Calculate liquidity
    liquidity_data = calculate_liquidity(df)
    liquidity_score = liquidity_data['score'] if liquidity_data else 50
    liquidity_bias = liquidity_data['bias'] if liquidity_data else 'MODERATE'
    
    # Get scores
    oi_score = get_score('OI Positioning')
    pcr_score = get_score('PCR')
    vol_score = get_score('Volume')
    sr_score = get_score('Support / Resistance')
    maxpain_score = get_score('Max Pain')
    sentiment_score = get_score('IV')
    iv_skew_score = get_score('IV Skew')
    
    # Calculate weighted score
    weighted_score = (
        oi_score * 0.20 +
        sr_score * 0.18 +
        pcr_score * 0.15 +
        vol_score * 0.12 +
        sentiment_score * 0.10 +
        iv_skew_score * 0.08 +
        maxpain_score * 0.07 +
        liquidity_score * 0.05
    )
    final_score = weighted_score
    
    # Count factors
    all_scores = [oi_score, sr_score, pcr_score, vol_score, sentiment_score, iv_skew_score, maxpain_score, liquidity_score]
    bullish_count = sum(1 for s in all_scores if s >= 65)
    bearish_count = sum(1 for s in all_scores if s <= 35)
    neutral_count = sum(1 for s in all_scores if 35 < s < 65)
    
    return {
        'score': final_score,
        'confidence': result.confidence if hasattr(result, 'confidence') else 65,
        'bullish_count': bullish_count,
        'neutral_count': neutral_count,
        'bearish_count': bearish_count,
        'total_factors': len(all_scores),
        'pcr_oi': result.oi_pcr,
        'atm': result.atm_strike,
        'support': result.supports[0].strike if result.supports else 0,
        'resistance': result.resistances[0].strike if result.resistances else 0,
        'max_pain': result.max_pain_strike,
        'atm_ce_oi': result.atm_ce_oi,
        'atm_pe_oi': result.atm_pe_oi,
        'atm_oi_ratio': result.atm_pe_oi / result.atm_ce_oi if result.atm_ce_oi > 0 else 0,
        'atm_ce_ltp': result.atm_ce_ltp,
        'atm_pe_ltp': result.atm_pe_ltp,
        'atm_ce_iv': result.atm_ce_iv,
        'atm_pe_iv': result.atm_pe_iv,
        'atm_bias': get_bias('ATM'),
        'total_ce_oi': result.total_ce_oi,
        'total_pe_oi': result.total_pe_oi,
        'total_ce_volume': result.atm_ce_volume,
        'total_pe_volume': result.atm_pe_volume,
        'total_strikes': len(result.raw_strikes) if result.raw_strikes else 0,
        'oi_score': oi_score,
        'pcr_score': pcr_score,
        'vol_score': vol_score,
        'sr_score': sr_score,
        'maxpain_score': maxpain_score,
        'liquidity_score': liquidity_score,
        'sentiment_score': sentiment_score,
        'iv_skew_score': iv_skew_score,
        'oi_bias': get_bias('OI Positioning'),
        'pcr_bias': get_bias('PCR'),
        'vol_bias': get_bias('Volume'),
        'sr_bias': get_bias('Support / Resistance'),
        'maxpain_bias': get_bias('Max Pain'),
        'liquidity_bias': liquidity_bias,
        'sentiment_bias': get_bias('IV'),
        'iv_skew_bias': get_bias('IV Skew'),
        'key_reasons': [
            f"OI Positioning: {get_bias('OI Positioning')} with CE OI {result.total_ce_oi:,.0f} vs PE OI {result.total_pe_oi:,.0f}",
            f"Support/Resistance: {get_bias('Support / Resistance')}",
            f"PCR Bias: {get_bias('PCR')} (PCR: {result.oi_pcr:.2f})",
            f"IV Bias: {get_bias('IV')} (CE IV: {result.atm_ce_iv:.2f}%, PE IV: {result.atm_pe_iv:.2f}%)",
            f"Strongest Support: {result.supports[0].strike:,.0f}" if result.supports else "No support",
            f"Strongest Resistance: {result.resistances[0].strike:,.0f}" if result.resistances else "No resistance",
            f"Max Pain: {result.max_pain_strike:,.0f}",
        ]
    }


def calculate_liquidity(df):
    """Calculate liquidity metrics"""
    if df is None or df.empty:
        return {'score': 50, 'bias': 'MODERATE'}
    
    total_strikes = len(df)
    ce_active = 0
    pe_active = 0
    
    for _, row in df.iterrows():
        try:
            if float(row.get('OI', 0)) > 0:
                ce_active += 1
            if float(row.get('OI.1', 0)) > 0:
                pe_active += 1
        except:
            pass
    
    active_ratio = (ce_active + pe_active) / (2 * total_strikes) if total_strikes > 0 else 0
    liquidity_score = active_ratio * 100
    
    if liquidity_score >= 70:
        bias = "GOOD"
    elif liquidity_score >= 40:
        bias = "MODERATE"
    else:
        bias = "POOR"
    
    return {'score': round(liquidity_score, 1), 'bias': bias}


def display_error(error_message):
    """Display error message"""
    
    st.markdown(f"""
    <div class="error-box">
        <h3>⚠️ Error</h3>
        <pre style="color:#ff6b6b;white-space:pre-wrap;word-wrap:break-word;">{error_message}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Please check your file format and try again.")
    
    if st.button("🔄 Clear Error and Try Again"):
        st.session_state.error = None
        st.session_state.analyzed = False
        st.session_state.uploaded_file = None
        st.rerun()


def display_welcome():
    """Display welcome screen"""
    
    st.markdown("""
    <div class="welcome-box">
        <div class="icon">📊</div>
        <div class="title">Welcome to Option Chain Analyzer</div>
        <div class="subtitle">Upload your Option Chain CSV file using the sidebar to get started</div>
        <div style="margin-top: 1.5rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: #1E1E2E; padding: 1rem; border-radius: 0.5rem; width: 180px;">
                <div style="font-size: 2rem;">📈</div>
                <div style="font-weight: 600;">OI Analysis</div>
                <div style="font-size: 0.8rem; color: #666;">Open Interest metrics</div>
            </div>
            <div style="background: #1E1E2E; padding: 1rem; border-radius: 0.5rem; width: 180px;">
                <div style="font-size: 2rem;">📉</div>
                <div style="font-weight: 600;">PCR Analysis</div>
                <div style="font-size: 0.8rem; color: #666;">Put-Call Ratio</div>
            </div>
            <div style="background: #1E1E2E; padding: 1rem; border-radius: 0.5rem; width: 180px;">
                <div style="font-size: 2rem;">🎯</div>
                <div style="font-weight: 600;">S/R & Max Pain</div>
                <div style="font-size: 0.8rem; color: #666;">Key levels</div>
            </div>
            <div style="background: #1E1E2E; padding: 1rem; border-radius: 0.5rem; width: 180px;">
                <div style="font-size: 2rem;">🌐</div>
                <div style="font-weight: 600;">IV Analysis</div>
                <div style="font-size: 0.8rem; color: #666;">Volatility analysis</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_report(result):
    """Display only the report - NO Decision Card"""
    
    if result is None:
        st.warning("No analysis results available.")
        return
    
    analysis = st.session_state.get('analysis', {})
    
    # Get decision
    score = analysis.get('score', 50)
    confidence = analysis.get('confidence', 65)
    bullish_count = analysis.get('bullish_count', 0)
    neutral_count = analysis.get('neutral_count', 0)
    bearish_count = analysis.get('bearish_count', 0)
    total_factors = analysis.get('total_factors', 8)
    
    if score >= 65:
        decision = "BULLISH"
        decision_color = "#00C853"
        emoji = "📈"
    elif score <= 35:
        decision = "BEARISH"
        decision_color = "#FF1744"
        emoji = "📉"
    else:
        decision = "NEUTRAL"
        decision_color = "#FFD600"
        emoji = "➡️"
    
    # ========================================================================
    # KEY METRICS (Compact)
    # ========================================================================
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📈 PCR", f"{result.oi_pcr:.2f}")
    
    with col2:
        support = result.supports[0].strike if result.supports else 0
        st.metric("🟢 Support", f"₹{support:,.0f}")
    
    with col3:
        st.metric("⚡ ATM", f"₹{result.atm_strike:,.0f}")
    
    with col4:
        resistance = result.resistances[0].strike if result.resistances else 0
        st.metric("🔴 Resistance", f"₹{resistance:,.0f}")
    
    with col5:
        st.metric("🎯 Max Pain", f"₹{result.max_pain_strike:,.0f}")
    
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    
    # ========================================================================
    # DETAILED REPORT (WITH FINAL DECISION INSIDE)
    # ========================================================================
    
    st.markdown("### 📄 Complete Analysis Report")
    
    # Generate report
    report_text = generate_report(result, analysis)
    
    # Display report
    st.markdown(f"""
    <div class="report-box">
        {report_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Download buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.download_button(
            label="📥 Download Report (TXT)",
            data=report_text,
            file_name=f"option_chain_report_{result.symbol}_{result.expiry}.txt",
            mime="text/plain"
        )
    
    with col2:
        html_report = generate_html_report(result, analysis)
        st.download_button(
            label="📥 Download Report (HTML)",
            data=html_report,
            file_name=f"option_chain_report_{result.symbol}_{result.expiry}.html",
            mime="text/html"
        )


def generate_report(result, analysis):
    """Generate text report with Final Decision inside"""
    
    # Get decision
    score = analysis.get('score', 50)
    confidence = analysis.get('confidence', 65)
    bullish_count = analysis.get('bullish_count', 0)
    neutral_count = analysis.get('neutral_count', 0)
    bearish_count = analysis.get('bearish_count', 0)
    
    if score >= 65:
        decision = "BULLISH"
    elif score <= 35:
        decision = "BEARISH"
    else:
        decision = "NEUTRAL"
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    lines = []
    lines.append("╔" + "═" * 78 + "╗")
    lines.append("║" + " " * 20 + "📊 OPTION CHAIN ANALYSIS REPORT" + " " * 21 + "║")
    lines.append("╚" + "═" * 78 + "╝")
    lines.append("")
    lines.append("┌" + "─" * 78 + "┐")
    lines.append(f"│ {'FILE':<12} : {result.file_name:<60}" + "│")
    lines.append(f"│ {'SYMBOL':<12} : {result.symbol:<60}" + "│")
    lines.append(f"│ {'EXPIRY':<12} : {result.expiry:<60}" + "│")
    lines.append(f"│ {'SPOT PRICE':<12} : ₹{result.spot_price:>13,.2f} {' ' * 38}" + "│")
    lines.append(f"│ {'ATM STRIKE':<12} : {result.atm_strike:>14,.0f} {' ' * 40}" + "│")
    lines.append(f"│ {'TOTAL STRIKES':<12} : {len(result.raw_strikes) if result.raw_strikes else 0:<60}" + "│")
    lines.append(f"│ {'GENERATED':<12} : {timestamp:<60}" + "│")
    lines.append("└" + "─" * 78 + "┘")
    lines.append("")
    
    # Final Decision (Inside Report)
    lines.append("╔" + "═" * 78 + "╗")
    lines.append("║" + " " * 25 + "🎯 FINAL DECISION" + " " * 28 + "║")
    lines.append("╠" + "═" * 78 + "╣")
    lines.append(f"║  {'DECISION':<20} : {decision:<55} ║")
    lines.append(f"║  {'SCORE':<20} : {score:>5.0f}/100{' ' * 50} ║")
    lines.append(f"║  {'CONFIDENCE':<20} : {confidence:>5.0f}%{' ' * 53} ║")
    lines.append(f"║  {'BULLISH':<20} : {bullish_count:>5} factors{' ' * 50} ║")
    lines.append(f"║  {'NEUTRAL':<20} : {neutral_count:>5} factors{' ' * 50} ║")
    lines.append(f"║  {'BEARISH':<20} : {bearish_count:>5} factors{' ' * 50} ║")
    lines.append("╚" + "═" * 78 + "╝")
    lines.append("")
    
    # OI Summary
    lines.append("┌" + "─" * 78 + "┐")
    lines.append("│" + " " * 28 + "📈 OPEN INTEREST SUMMARY" + " " * 29 + "│")
    lines.append("├" + "─" * 78 + "┤")
    lines.append(f"│  {'Total CE OI':<20} : {result.total_ce_oi:>15,} {' ' * 38} │")
    lines.append(f"│  {'Total PE OI':<20} : {result.total_pe_oi:>15,} {' ' * 38} │")
    lines.append(f"│  {'OI PCR':<20} : {result.oi_pcr:>15.2f} {' ' * 38} │")
    lines.append(f"│  {'OI Positioning':<20} : {result.oi_positioning_bias:>15} {' ' * 38} │")
    lines.append(f"│  {'Highest CE OI':<20} : {result.highest_ce_oi_strike:>15,.0f} {' ' * 38} │")
    lines.append(f"│  {'Highest PE OI':<20} : {result.highest_pe_oi_strike:>15,.0f} {' ' * 38} │")
    lines.append("└" + "─" * 78 + "┘")
    lines.append("")
    
    # ATM Structure
    lines.append("┌" + "─" * 78 + "┐")
    lines.append("│" + " " * 28 + "🏧 ATM STRUCTURE" + " " * 29 + "│")
    lines.append("├" + "─" * 78 + "┤")
    lines.append(f"│  {'ATM Strike':<20} : {result.atm_strike:>15,.0f} {' ' * 38} │")
    lines.append(f"│  {'CE OI':<20} : {result.atm_ce_oi:>15,} {' ' * 38} │")
    lines.append(f"│  {'PE OI':<20} : {result.atm_pe_oi:>15,} {' ' * 38} │")
    lines.append(f"│  {'CE Volume':<20} : {result.atm_ce_volume:>15,} {' ' * 38} │")
    lines.append(f"│  {'PE Volume':<20} : {result.atm_pe_volume:>15,} {' ' * 38} │")
    lines.append(f"│  {'CE LTP':<20} : ₹{result.atm_ce_ltp:>13.2f} {' ' * 38} │")
    lines.append(f"│  {'PE LTP':<20} : ₹{result.atm_pe_ltp:>13.2f} {' ' * 38} │")
    lines.append(f"│  {'CE IV':<20} : {result.atm_ce_iv:>14.2f}% {' ' * 38} │")
    lines.append(f"│  {'PE IV':<20} : {result.atm_pe_iv:>14.2f}% {' ' * 38} │")
    lines.append(f"│  {'ATM Bias':<20} : {result.atm_bias:>15} {' ' * 38} │")
    lines.append("└" + "─" * 78 + "┘")
    lines.append("")
    
    # Support & Resistance
    lines.append("┌" + "─" * 78 + "┐")
    lines.append("│" + " " * 27 + "🎯 SUPPORT & RESISTANCE" + " " * 28 + "│")
    lines.append("├" + "─" * 78 + "┤")
    if result.supports:
        lines.append(f"│  {'SUPPORTS':<20} : {' ' * 54} │")
        for s in result.supports[:3]:
            lines.append(f"│    #{s.strength}: ₹{s.strike:>8,.0f} (PE OI: {s.pe_oi:>10,}) - {s.status:<12} │")
    else:
        lines.append("│  No clear support levels".ljust(79) + "│")
    
    if result.resistances:
        lines.append(f"│  {'RESISTANCES':<20} : {' ' * 54} │")
        for r in result.resistances[:3]:
            lines.append(f"│    #{r.strength}: ₹{r.strike:>8,.0f} (CE OI: {r.ce_oi:>10,}) - {r.status:<12} │")
    else:
        lines.append("│  No clear resistance levels".ljust(79) + "│")
    lines.append(f"│  {'S/R Bias':<20} : {result.support_resistance_bias:>15} {' ' * 38} │")
    lines.append("└" + "─" * 78 + "┘")
    lines.append("")
    
    # Other Analysis
    lines.append("┌" + "─" * 78 + "┐")
    lines.append("│" + " " * 25 + "📊 OTHER ANALYSIS" + " " * 30 + "│")
    lines.append("├" + "─" * 78 + "┤")
    lines.append(f"│  {'PCR Bias':<20} : {result.pcr_bias:>15} {' ' * 38} │")
    
    ce_vol = getattr(result, '_ce_volume', 0) or result.atm_ce_volume or 0
    pe_vol = getattr(result, '_pe_volume', 0) or result.atm_pe_volume or 0
    lines.append(f"│  {'Volume Bias':<20} : {result.volume_bias:>15} {' ' * 38} │")
    
    iv_bias = getattr(result, 'iv_bias', 'NEUTRAL')
    lines.append(f"│  {'IV Bias':<20} : {iv_bias:>15} {' ' * 38} │")
    
    iv_skew_bias = getattr(result, 'iv_skew_bias', 'NEUTRAL')
    lines.append(f"│  {'IV Skew Bias':<20} : {iv_skew_bias:>15} {' ' * 38} │")
    
    lines.append(f"│  {'Max Pain':<20} : {result.max_pain_strike:>15,.0f} {' ' * 38} │")
    lines.append(f"│  {'Max Pain Bias':<20} : {result.max_pain_bias:>15} {' ' * 38} │")
    
    liquidity_bias = analysis.get('liquidity_bias', 'MODERATE')
    liquidity_score = analysis.get('liquidity_score', 50)
    lines.append(f"│  {'Liquidity':<20} : {liquidity_bias} ({liquidity_score:.0f}/100){' ' * 38} │")
    lines.append("└" + "─" * 78 + "┘")
    lines.append("")
    
    # Key Reasons
    lines.append("┌" + "─" * 78 + "┐")
    lines.append("│" + " " * 28 + "🔑 KEY REASONS" + " " * 31 + "│")
    lines.append("├" + "─" * 78 + "┤")
    reasons = analysis.get('key_reasons', [])
    if reasons:
        for i, reason in enumerate(reasons[:5], 1):
            if len(reason) > 75:
                reason = reason[:72] + "..."
            lines.append(f"│  {i}. {reason:<74} │")
    else:
        lines.append("│  No key reasons available".ljust(79) + "│")
    lines.append("└" + "─" * 78 + "┘")
    lines.append("")
    
    # Footer
    lines.append("╔" + "═" * 78 + "╗")
    lines.append("║" + " " * 28 + "📅 END OF REPORT" + " " * 31 + "║")
    lines.append("╚" + "═" * 78 + "╝")
    
    return "\n".join(lines)


def generate_html_report(result, analysis):
    """Generate HTML report with proper styling"""
    
    score = analysis.get('score', 50)
    confidence = analysis.get('confidence', 65)
    bullish_count = analysis.get('bullish_count', 0)
    neutral_count = analysis.get('neutral_count', 0)
    bearish_count = analysis.get('bearish_count', 0)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if score >= 65:
        decision = "BULLISH"
        color = "#00C853"
        emoji = "📈"
    elif score <= 35:
        decision = "BEARISH"
        color = "#FF1744"
        emoji = "📉"
    else:
        decision = "NEUTRAL"
        color = "#FFD600"
        emoji = "➡️"
    
    support_str = f"₹{result.supports[0].strike:,.0f}" if result.supports else "None"
    resistance_str = f"₹{result.resistances[0].strike:,.0f}" if result.resistances else "None"
    
    iv_bias = getattr(result, 'iv_bias', 'NEUTRAL')
    iv_skew_bias = getattr(result, 'iv_skew_bias', 'NEUTRAL')
    
    reasons = analysis.get('key_reasons', [])
    reasons_html = ""
    if reasons:
        for reason in reasons[:5]:
            reasons_html += f'<li>{reason}</li>'
    else:
        reasons_html = '<li>No key reasons available</li>'
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Option Chain Analysis Report</title>
<style>
    body {{ font-family: 'Courier New', monospace; background: #0E0E1E; color: #ccc; padding: 2rem; }}
    .container {{ max-width: 900px; margin: 0 auto; background: #1A1A2E; padding: 2rem; border-radius: 0.5rem; border: 1px solid #1E88E5; }}
    .header {{ text-align: center; border-bottom: 2px solid #1E88E5; padding-bottom: 1rem; margin-bottom: 2rem; }}
    .header h1 {{ color: #1E88E5; font-size: 2rem; margin: 0; }}
    .header p {{ color: #888; margin: 0.5rem 0 0; }}
    
    .decision {{ text-align: center; padding: 2rem; border-radius: 0.5rem; margin: 1.5rem 0; border: 3px solid ''' + color + '''; background: linear-gradient(135deg, #1A1A2E, #0E0E1E); }}
    .decision .emoji {{ font-size: 3rem; }}
    .decision .text {{ font-size: 2.5rem; font-weight: 700; color: ''' + color + '''; }}
    .decision .score {{ font-size: 1.2rem; margin: 0.5rem 0; color: #aaa; }}
    
    .section {{ border: 1px solid #1E88E5; border-radius: 0.3rem; margin: 1rem 0; overflow: hidden; }}
    .section-title {{ background: #1E1E3E; padding: 0.5rem 1rem; font-weight: 700; color: #1E88E5; border-bottom: 1px solid #1E88E5; }}
    .section-body {{ padding: 0.5rem 1rem; }}
    .section-body .row {{ display: flex; padding: 0.2rem 0; border-bottom: 1px solid #1A1A2E; }}
    .section-body .label {{ width: 200px; color: #888; }}
    .section-body .value {{ flex: 1; color: #eee; }}
    
    .footer {{ text-align: center; color: #666; font-size: 0.8rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #1E1E3E; }}
    
    .reasons {{ padding: 0.5rem 1rem; }}
    .reasons li {{ margin: 0.3rem 0; color: #aaa; }}
    
    .badge {{ display: inline-block; padding: 0.2rem 0.8rem; border-radius: 1rem; font-size: 0.7rem; font-weight: 600; }}
    .badge-bullish {{ background: #1B5E20; color: #00C853; }}
    .badge-bearish {{ background: #B71C1C; color: #FF1744; }}
    .badge-neutral {{ background: #F57F17; color: #FFD600; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📊 Option Chain Analysis Report</h1>
        <p>''' + result.symbol + ''' | Expiry: ''' + result.expiry + ''' | Generated: ''' + timestamp + '''</p>
    </div>
    
    <div class="decision">
        <div class="emoji">''' + emoji + '''</div>
        <div class="text">''' + decision + '''</div>
        <div class="score">Score: ''' + f"{score:.0f}" + '''/100 | Confidence: ''' + f"{confidence:.0f}" + '''%</div>
        <div style="margin-top:0.5rem;">
            <span class="badge badge-bullish">🟢 ''' + str(bullish_count) + ''' Bullish</span>
            <span class="badge badge-neutral">🟡 ''' + str(neutral_count) + ''' Neutral</span>
            <span class="badge badge-bearish">🔴 ''' + str(bearish_count) + ''' Bearish</span>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">📈 Open Interest Summary</div>
        <div class="section-body">
            <div class="row"><span class="label">Total CE OI</span><span class="value">''' + f"{result.total_ce_oi:,.0f}" + '''</span></div>
            <div class="row"><span class="label">Total PE OI</span><span class="value">''' + f"{result.total_pe_oi:,.0f}" + '''</span></div>
            <div class="row"><span class="label">OI PCR</span><span class="value">''' + f"{result.oi_pcr:.2f}" + '''</span></div>
            <div class="row"><span class="label">OI Positioning</span><span class="value">''' + result.oi_positioning_bias + '''</span></div>
            <div class="row"><span class="label">Highest CE OI</span><span class="value">₹''' + f"{result.highest_ce_oi_strike:,.0f}" + '''</span></div>
            <div class="row"><span class="label">Highest PE OI</span><span class="value">₹''' + f"{result.highest_pe_oi_strike:,.0f}" + '''</span></div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">🏧 ATM Structure</div>
        <div class="section-body">
            <div class="row"><span class="label">ATM Strike</span><span class="value">₹''' + f"{result.atm_strike:,.0f}" + '''</span></div>
            <div class="row"><span class="label">CE OI</span><span class="value">''' + f"{result.atm_ce_oi:,.0f}" + '''</span></div>
            <div class="row"><span class="label">PE OI</span><span class="value">''' + f"{result.atm_pe_oi:,.0f}" + '''</span></div>
            <div class="row"><span class="label">CE IV</span><span class="value">''' + f"{result.atm_ce_iv:.2f}%" + '''</span></div>
            <div class="row"><span class="label">PE IV</span><span class="value">''' + f"{result.atm_pe_iv:.2f}%" + '''</span></div>
            <div class="row"><span class="label">ATM Bias</span><span class="value">''' + result.atm_bias + '''</span></div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">🎯 Support & Resistance</div>
        <div class="section-body">
            <div class="row"><span class="label">Strongest Support</span><span class="value">''' + support_str + '''</span></div>
            <div class="row"><span class="label">Strongest Resistance</span><span class="value">''' + resistance_str + '''</span></div>
            <div class="row"><span class="label">S/R Bias</span><span class="value">''' + result.support_resistance_bias + '''</span></div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">📊 Other Analysis</div>
        <div class="section-body">
            <div class="row"><span class="label">PCR Bias</span><span class="value">''' + result.pcr_bias + '''</span></div>
            <div class="row"><span class="label">Volume Bias</span><span class="value">''' + result.volume_bias + '''</span></div>
            <div class="row"><span class="label">IV Bias</span><span class="value">''' + iv_bias + '''</span></div>
            <div class="row"><span class="label">IV Skew Bias</span><span class="value">''' + iv_skew_bias + '''</span></div>
            <div class="row"><span class="label">Max Pain</span><span class="value">₹''' + f"{result.max_pain_strike:,.0f}" + '''</span></div>
            <div class="row"><span class="label">Max Pain Bias</span><span class="value">''' + result.max_pain_bias + '''</span></div>
            <div class="row"><span class="label">Liquidity</span><span class="value">''' + str(analysis.get('liquidity_bias', 'MODERATE')) + ''' (''' + f"{analysis.get('liquidity_score', 50):.0f}" + '''/100)</span></div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">🔑 Key Reasons</div>
        <div class="reasons">
            <ul>
                ''' + reasons_html + '''
            </ul>
        </div>
    </div>
    
    <div class="footer">
        📅 End of Report | Generated by NSE/BSE Option Chain Analyzer
    </div>
</div>
</body>
</html>'''
    
    return html


if __name__ == "__main__":
    main()