"""Main Streamlit Application - NSE/BSE Option Chain Analyzer"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os
import traceback

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data_loader import DataLoader
from src.core.data_validator import DataValidator
from src.core.analyzer import Analyzer
from src.core.report_generator import ReportGenerator

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
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #FAFAFA;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #1E1E2E;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
    }
    .bullish {
        color: #00C853;
    }
    .bearish {
        color: #FF1744;
    }
    .neutral {
        color: #FFD600;
    }
    .strong-bullish {
        color: #00E676;
    }
    .strong-bearish {
        color: #D50000;
    }
    .stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #1565C0;
    }
    .error-box {
        background-color: #2E1E1E;
        border: 1px solid #FF1744;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #1E2E1E;
        border: 1px solid #00C853;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #2E2E1E;
        border: 1px solid #FFD600;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .data-info {
        background-color: #1E1E3E;
        border: 1px solid #1E88E5;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
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


def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<div class="main-header">📊 NSE/BSE Option Chain Analyzer</div>', unsafe_allow_html=True)
    st.markdown("Upload your Option Chain CSV file for comprehensive analysis")
    
    # Sidebar - File Upload
    with st.sidebar:
        st.markdown("### 📁 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose an option chain CSV file",
            type=['csv', 'xlsx', 'xls', 'tsv'],
            help="Upload option chain data in NSE/BSE format (21 columns)"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File loaded: {uploaded_file.name}")
            st.info(f"Size: {uploaded_file.size / 1024:.1f} KB")
            
            if st.button("🚀 Analyze", type="primary"):
                with st.spinner("Analyzing option chain data..."):
                    analyze_file(uploaded_file)
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.markdown("""
        This tool analyzes Option Chain data to provide:
        - Open Interest Analysis
        - Put-Call Ratio (PCR)
        - Support & Resistance Levels
        - Max Pain Calculation
        - Change in OI Analysis
        - Volume Analysis
        - Liquidity Analysis
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
        display_results(st.session_state.result)
    else:
        display_placeholder()


def analyze_file(uploaded_file):
    """Analyze uploaded file"""
    
    try:
        # Load data
        loader = DataLoader()
        success, message, df = loader.load_from_file(uploaded_file)
        
        if not success:
            st.session_state.error = f"❌ {message}"
            st.session_state.analyzed = False
            st.rerun()
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
            st.rerun()
            return
        
        # Get option chain
        option_chain = loader.get_option_chain(df, uploaded_file.name)
        
        # Analyze
        analyzer = Analyzer()
        result = analyzer.analyze(option_chain, uploaded_file.name)
        
        # Store in session
        st.session_state.analyzed = True
        st.session_state.result = result
        st.session_state.df = df
        st.session_state.filename = uploaded_file.name
        st.session_state.error = None
        
        st.success("✅ Analysis complete!")
        st.rerun()
        
    except Exception as e:
        st.session_state.error = f"❌ Error during analysis: {str(e)}\n\n{traceback.format_exc()}"
        st.session_state.analyzed = False
        st.rerun()


def display_error(error_message):
    """Display error message"""
    
    st.markdown(f"""
    <div class="error-box">
        <h3>⚠️ Error</h3>
        <pre>{error_message}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Please check your file format and try again. The expected format is:")
    st.code("""
    Row 1: ,,,,CALLS,,,,,,STRIKE PRICE,,,,,PUTS,,,,,,,
    Row 2: Chg in OI,OI,VOLUME,IV,LTP,CHNG,BID QTY,BID PRICE,ASK PRICE,ASK QTY,STRIKE PRICE,BID QTY,BID PRICE,ASK PRICE,ASK QTY,CHNG,LTP,IV,VOLUME,OI,Chg in OI
    Row 3+: Data rows with 21 columns
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Clear Error and Try Again"):
            st.session_state.error = None
            st.rerun()
    
    with col2:
        if st.button("📋 Show Sample Format"):
            st.session_state.show_sample = True
            st.rerun()
    
    if st.session_state.get('show_sample', False):
        st.markdown("### 📋 Sample Data Structure")
        sample_data = {
            "Column": list(range(21)),
            "Side": ["CALLS"]*11 + ["STRIKE"] + ["PUTS"]*10,
            "Name": [
                "Empty", "OI", "Chg in OI", "VOLUME", "IV", "LTP", "CHNG", 
                "BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY",
                "STRIKE PRICE",
                "BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY", "CHNG", "LTP", "IV", "VOLUME", "OI", "Chg in OI"
            ]
        }
        st.dataframe(pd.DataFrame(sample_data), use_container_width=True, hide_index=True)


def display_results(result):
    """Display analysis results"""
    
    if result is None:
        st.warning("No analysis results available. Please upload and analyze a file.")
        return
    
    # Show data summary
    if st.session_state.validation:
        v = st.session_state.validation
        st.markdown(f"""
        <div class="data-info">
            <b>📊 Data Summary:</b> {v.symbol} | Expiry: {v.expiry} | 
            {v.num_strikes} strikes | Range: {v.strike_range[0]:,.0f} - {v.strike_range[1]:,.0f} | 
            ATM: {v.atm_strike:,.0f} | OI PCR: {v.details.get('oi_pcr', 0):.2f}
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs
    tabs = st.tabs([
        "📊 Dashboard",
        "📈 OI Analysis",
        "📉 PCR Analysis",
        "🔄 Change OI",
        "🎯 Support/Resistance",
        "💉 Max Pain",
        "📄 Report"
    ])
    
    with tabs[0]:
        display_dashboard(result)
    
    with tabs[1]:
        display_oi_analysis(result)
    
    with tabs[2]:
        display_pcr_analysis(result)
    
    with tabs[3]:
        display_change_oi(result)
    
    with tabs[4]:
        display_support_resistance(result)
    
    with tabs[5]:
        display_max_pain(result)
    
    with tabs[6]:
        display_report(result)


def display_dashboard(result):
    """Display dashboard"""
    
    st.markdown('<div class="sub-header">🎯 Final Decision</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Determine color for market
    market_color = {
        "STRONG_BULLISH": "strong-bullish",
        "BULLISH": "bullish",
        "WEAK_BULLISH": "bullish",
        "NEUTRAL": "neutral",
        "WEAK_BEARISH": "bearish",
        "BEARISH": "bearish",
        "STRONG_BEARISH": "strong-bearish"
    }.get(result.final_market, "neutral")
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market</div>
            <div class="metric-value {market_color}">{result.final_market}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Confidence</div>
            <div class="metric-value">{result.confidence:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Bullish Score</div>
            <div class="metric-value bullish">{result.bullish_score:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Bearish Score</div>
            <div class="metric-value bearish">{result.bearish_score:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown('<div class="sub-header">📊 Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("OI PCR", f"{result.oi_pcr:.2f}")
        st.metric("Change OI PCR", f"{result.change_oi_pcr:.2f}")
    
    with col2:
        st.metric("Total CE OI", f"{result.total_ce_oi:,.0f}")
        st.metric("Total PE OI", f"{result.total_pe_oi:,.0f}")
    
    with col3:
        st.metric("ATM CE OI", f"{result.atm_ce_oi:,.0f}")
        st.metric("ATM PE OI", f"{result.atm_pe_oi:,.0f}")
    
    with col4:
        st.metric("Max Pain", f"{result.max_pain_strike:,.0f}")
        st.metric("Spot Price", f"₹{result.spot_price:,.2f}")
    
    # Key Reasons
    st.markdown('<div class="sub-header">🔑 Key Reasons</div>', unsafe_allow_html=True)
    
    if result.key_reasons:
        for i, reason in enumerate(result.key_reasons, 1):
            st.info(f"{i}. {reason}")
    else:
        st.info("No key reasons available.")
    
    # Factor Scores
    st.markdown('<div class="sub-header">📈 Factor Scores</div>', unsafe_allow_html=True)
    
    if result.factor_scores:
        factor_data = []
        for score in result.factor_scores:
            factor_data.append({
                "Factor": score.factor_name,
                "Bias": score.bias,
                "Bullish": f"{score.bullish_score:.0f}%",
                "Bearish": f"{score.bearish_score:.0f}%",
                "Weight": f"{score.weight}%"
            })
        
        st.dataframe(pd.DataFrame(factor_data), use_container_width=True, hide_index=True)
    else:
        st.info("No factor scores available.")


def display_oi_analysis(result):
    """Display OI Analysis"""
    
    st.markdown('<div class="sub-header">📈 Open Interest Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Total OI")
        st.metric("Total CE OI", f"{result.total_ce_oi:,.0f}")
        st.metric("Total PE OI", f"{result.total_pe_oi:,.0f}")
        st.metric("OI PCR", f"{result.oi_pcr:.2f}")
        st.metric("OI Positioning", result.oi_positioning_bias)
    
    with col2:
        st.markdown("### Highest OI Strikes")
        st.metric("Highest CE OI", f"{result.highest_ce_oi_strike:,.0f}")
        st.metric("Highest PE OI", f"{result.highest_pe_oi_strike:,.0f}")
    
    st.markdown("---")
    st.markdown("### ATM Structure")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("ATM CE OI", f"{result.atm_ce_oi:,.0f}")
        st.metric("ATM CE Change OI", f"{result.atm_ce_chg_oi:,.0f}")
        st.metric("ATM CE Volume", f"{result.atm_ce_volume:,.0f}")
        st.metric("ATM CE LTP", f"₹{result.atm_ce_ltp:.2f}")
        st.metric("ATM CE IV", f"{result.atm_ce_iv:.2f}%")
    
    with col2:
        st.metric("ATM PE OI", f"{result.atm_pe_oi:,.0f}")
        st.metric("ATM PE Change OI", f"{result.atm_pe_chg_oi:,.0f}")
        st.metric("ATM PE Volume", f"{result.atm_pe_volume:,.0f}")
        st.metric("ATM PE LTP", f"₹{result.atm_pe_ltp:.2f}")
        st.metric("ATM PE IV", f"{result.atm_pe_iv:.2f}%")
    
    st.markdown(f"**ATM Bias:** {result.atm_bias}")


def display_pcr_analysis(result):
    """Display PCR Analysis"""
    
    st.markdown('<div class="sub-header">📉 Put-Call Ratio Analysis</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("OI PCR", f"{result.oi_pcr:.2f}")
    
    with col2:
        st.metric("Change OI PCR", f"{result.change_oi_pcr:.2f}")
    
    with col3:
        st.metric("PCR Bias", result.pcr_bias)
    
    # PCR Interpretation
    st.markdown("### 📖 PCR Interpretation")
    
    pcr = result.oi_pcr
    if pcr > 0.7:
        st.warning(f"⚠️ PCR at {pcr:.2f} - High put protection. Market may be oversold or bearish.")
    elif pcr < 0.4:
        st.info(f"ℹ️ PCR at {pcr:.2f} - Low put protection. Market may be overbought or bullish.")
    else:
        st.success(f"✅ PCR at {pcr:.2f} - Neutral zone. Market is balanced.")


def display_change_oi(result):
    """Display Change OI Analysis"""
    
    st.markdown('<div class="sub-header">🔄 Change in OI Analysis</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total CE Change OI", f"{result.total_ce_chg_oi:,.0f}")
    
    with col2:
        st.metric("Total PE Change OI", f"{result.total_pe_chg_oi:,.0f}")
    
    with col3:
        st.metric("Change OI PCR", f"{result.change_oi_pcr:.2f}")
    
    st.metric("Change OI Bias", result.change_oi_bias)
    
    # Buildup Analysis
    st.markdown("### 📈 Buildup Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Call Side")
        cb = result.call_buildup
        st.write(f"Long Buildup: {len(cb.get('long_buildup', []))} strikes")
        st.write(f"Short Buildup: {len(cb.get('short_buildup', []))} strikes")
        st.write(f"Long Unwinding: {len(cb.get('long_unwinding', []))} strikes")
        st.write(f"Short Covering: {len(cb.get('short_covering', []))} strikes")
    
    with col2:
        st.markdown("#### Put Side")
        pb = result.put_buildup
        st.write(f"Long Buildup: {len(pb.get('long_buildup', []))} strikes")
        st.write(f"Short Buildup: {len(pb.get('short_buildup', []))} strikes")
        st.write(f"Long Unwinding: {len(pb.get('long_unwinding', []))} strikes")
        st.write(f"Short Covering: {len(pb.get('short_covering', []))} strikes")
    
    st.metric("Buildup Bias", result.buildup_bias)


def display_support_resistance(result):
    """Display Support and Resistance"""
    
    st.markdown('<div class="sub-header">🎯 Support & Resistance Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Support Levels")
        if result.supports:
            data = []
            for s in result.supports:
                data.append({
                    "Rank": s.strength,
                    "Strike": f"{s.strike:,.0f}",
                    "PE OI": s.pe_oi,
                    "Change OI": s.pe_chg_oi,
                    "Volume": s.pe_volume,
                    "Status": s.status
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("No clear support levels identified")
    
    with col2:
        st.markdown("### 🔴 Resistance Levels")
        if result.resistances:
            data = []
            for r in result.resistances:
                data.append({
                    "Rank": r.strength,
                    "Strike": f"{r.strike:,.0f}",
                    "CE OI": r.ce_oi,
                    "Change OI": r.ce_chg_oi,
                    "Volume": r.ce_volume,
                    "Status": r.status
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("No clear resistance levels identified")
    
    st.metric("Support/Resistance Bias", result.support_resistance_bias)


def display_max_pain(result):
    """Display Max Pain Analysis"""
    
    st.markdown('<div class="sub-header">💉 Max Pain Analysis</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Max Pain Strike", f"{result.max_pain_strike:,.0f}")
    
    with col2:
        st.metric("Spot Price", f"₹{result.spot_price:,.2f}")
    
    with col3:
        diff = result.spot_price - result.max_pain_strike
        st.metric("Spot - Max Pain", f"{diff:+,.2f}")
    
    # Interpretation
    st.markdown("### 📖 Interpretation")
    
    if result.max_pain_strike > 0:
        diff = result.spot_price - result.max_pain_strike
        if abs(diff) < 50:
            st.success(f"✅ Max Pain ({result.max_pain_strike:,.0f}) is close to Spot ({result.spot_price:,.2f}). Market is balanced.")
        elif diff > 50:
            st.warning(f"⚠️ Spot is above Max Pain. Market may move down towards {result.max_pain_strike:,.0f}.")
        else:
            st.warning(f"⚠️ Spot is below Max Pain. Market may move up towards {result.max_pain_strike:,.0f}.")
    
    st.metric("Max Pain Bias", result.max_pain_bias)


def display_report(result):
    """Display Full Report"""
    
    st.markdown('<div class="sub-header">📄 Full Report</div>', unsafe_allow_html=True)
    
    # Generate report
    generator = ReportGenerator()
    
    # Text report
    with st.expander("📄 View Full Report", expanded=True):
        report_text = generator.generate_text_report(result)
        st.code(report_text, language="text")
    
    # Markdown report
    with st.expander("📝 View Markdown Report"):
        markdown_text = generator.generate_markdown_report(result)
        st.markdown(markdown_text)
    
    # Download buttons
    col1, col2 = st.columns(2)
    
    with col1:
        text_report = generator.generate_text_report(result)
        st.download_button(
            label="📥 Download Text Report",
            data=text_report,
            file_name=f"option_chain_analysis_{result.symbol}_{result.expiry}.txt",
            mime="text/plain"
        )
    
    with col2:
        markdown_report = generator.generate_markdown_report(result)
        st.download_button(
            label="📥 Download Markdown Report",
            data=markdown_report,
            file_name=f"option_chain_analysis_{result.symbol}_{result.expiry}.md",
            mime="text/markdown"
        )


def display_placeholder():
    """Display placeholder when no data is loaded"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h2>📊 Welcome to Option Chain Analyzer</h2>
        <p style="color: #888; font-size: 1.1rem;">
            Upload an option chain CSV file from the sidebar to begin analysis.
        </p>
        <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: #1E1E2E; padding: 1.5rem; border-radius: 0.5rem; width: 200px;">
                <div style="font-size: 2rem;">📈</div>
                <div style="font-weight: 600;">OI Analysis</div>
                <div style="font-size: 0.8rem; color: #888;">Open Interest metrics</div>
            </div>
            <div style="background: #1E1E2E; padding: 1.5rem; border-radius: 0.5rem; width: 200px;">
                <div style="font-size: 2rem;">📉</div>
                <div style="font-weight: 600;">PCR Analysis</div>
                <div style="font-size: 0.8rem; color: #888;">Put-Call Ratio</div>
            </div>
            <div style="background: #1E1E2E; padding: 1.5rem; border-radius: 0.5rem; width: 200px;">
                <div style="font-size: 2rem;">🎯</div>
                <div style="font-weight: 600;">Support/Resistance</div>
                <div style="font-size: 0.8rem; color: #888;">Key levels</div>
            </div>
            <div style="background: #1E1E2E; padding: 1.5rem; border-radius: 0.5rem; width: 200px;">
                <div style="font-size: 2rem;">💉</div>
                <div style="font-weight: 600;">Max Pain</div>
                <div style="font-size: 0.8rem; color: #888;">Option pain point</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()