# 📊 NSE Option Chain Analyzer

A comprehensive Streamlit application for analyzing NSE option chain data.

## 🚀 Features

- **Complete Option Chain Analysis**: Upload CSV files and get comprehensive analysis
- **Open Interest Analysis**: Track CE/PE OI, PCR, and positioning
- **Change OI Analysis**: Monitor OI changes and buildup patterns
- **Support & Resistance**: Identify key levels from OI concentration
- **Max Pain Calculation**: Calculate the strike with maximum pain
- **Interactive Dashboard**: Visualize all metrics in one place
- **Report Generation**: Download text and markdown reports

## 📁 Supported File Format

The application supports NSE option chain CSV files in the following format:

```csv
,,,,CALLS,,,,,,STRIKE PRICE,,,,,PUTS,,,,,,,
Chg in OI,OI,VOLUME,IV,LTP,CHNG,BID QTY,BID PRICE,ASK PRICE,ASK QTY,STRIKE PRICE,BID QTY,BID PRICE,ASK PRICE,ASK QTY,CHNG,LTP,IV,VOLUME,OI,Chg in OI