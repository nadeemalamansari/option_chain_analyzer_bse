"""Report Generator"""

from ..models.analysis_result import AnalysisResult


class ReportGenerator:
    """Generate analysis reports"""
    
    def generate_text_report(self, result: AnalysisResult) -> str:
        """Generate a text-based report"""
        
        report = []
        report.append("=" * 80)
        report.append(f"OPTION CHAIN ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"File: {result.file_name}")
        report.append(f"Symbol: {result.symbol}")
        report.append(f"Expiry: {result.expiry}")
        report.append(f"Spot Price: ₹{result.spot_price:,.2f}")
        report.append(f"ATM Strike: {result.atm_strike:,.0f}")
        report.append("")
        report.append("-" * 40)
        report.append("FINAL DECISION")
        report.append("-" * 40)
        report.append(f"Market: {result.final_market}")
        report.append(f"Confidence: {result.confidence:.0f}%")
        report.append(f"Bullish Score: {result.bullish_score:.0f}")
        report.append(f"Bearish Score: {result.bearish_score:.0f}")
        report.append("")
        report.append("-" * 40)
        report.append("OPEN INTEREST")
        report.append("-" * 40)
        report.append(f"Total CE OI: {result.total_ce_oi:,.0f}")
        report.append(f"Total PE OI: {result.total_pe_oi:,.0f}")
        report.append(f"OI PCR: {result.oi_pcr:.2f}")
        report.append(f"OI Positioning: {result.oi_positioning_bias}")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_markdown_report(self, result: AnalysisResult) -> str:
        """Generate a markdown report"""
        
        lines = []
        lines.append("# 📊 Option Chain Analysis Report")
        lines.append("")
        lines.append(f"**File:** `{result.file_name}`")
        lines.append(f"**Symbol:** {result.symbol}")
        lines.append(f"**Expiry:** {result.expiry}")
        lines.append(f"**Spot Price:** ₹{result.spot_price:,.2f}")
        lines.append("")
        lines.append("## 🎯 Final Decision")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| **Market** | **{result.final_market}** |")
        lines.append(f"| **Confidence** | {result.confidence:.0f}% |")
        lines.append(f"| **Bullish Score** | {result.bullish_score:.0f} |")
        lines.append(f"| **Bearish Score** | {result.bearish_score:.0f} |")
        lines.append("")
        
        return "\n".join(lines)