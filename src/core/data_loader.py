"""Data loader for option chain CSV files - Fixed for BSE Format"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, List
import io
import re
import logging

from ..utils.helpers import clean_numeric, clean_integer, extract_expiry_from_filename, extract_symbol_from_filename
from ..models.option_chain import OptionChain

# Set up logging
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and preprocess option chain data for BSE format"""
    
    def __init__(self):
        self.df = None
        self.option_chain = None
        self.file_name = None
    
    def load_from_file(self, file) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Load option chain data from uploaded file"""
        try:
            self.file_name = file.name
            
            if file.name.endswith('.csv'):
                content = file.read().decode('utf-8-sig')
                lines = content.split('\n')
                
                # Find the actual header row (contains "Chg in OI" and "STRIKE PRICE")
                header_row_index = 0
                for i, line in enumerate(lines):
                    if 'Chg in OI' in line and 'STRIKE PRICE' in line:
                        header_row_index = i
                        break
                
                # Skip rows before the header
                if header_row_index > 0:
                    lines = lines[header_row_index:]
                
                cleaned_content = '\n'.join(lines)
                csv_buffer = io.StringIO(cleaned_content)
                df = pd.read_csv(csv_buffer, encoding='utf-8-sig')
                
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file, header=1)
            else:
                return False, "Unsupported file format", None
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            # Fix the format
            df = self._fix_bse_format(df)
            
            self.df = df
            return True, "File loaded successfully", df
            
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            return False, f"Error loading file: {str(e)}", None
    
    def _fix_bse_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix BSE format - 21 columns with CALLS before STRIKE, PUTS after"""
        
        # Check if we already have the right format
        if "OI" in df.columns and "OI.1" in df.columns:
            return df
        
        cols = df.columns.tolist()
        
        # If we have 21 columns, map by position
        if len(cols) == 21:
            new_df = pd.DataFrame()
            
            # CE columns - positions 0-9
            ce_cols = ["Chg in OI", "OI", "VOLUME", "IV", "LTP", "CHNG", "BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY"]
            
            # PE columns - positions 11-20
            pe_cols = ["BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY", "CHNG", "LTP", "IV", "VOLUME", "OI", "Chg in OI"]
            
            # STRIKE PRICE is at position 10
            new_df["STRIKE PRICE"] = df.iloc[:, 10]
            
            # Map CE columns
            for i, col_name in enumerate(ce_cols):
                new_df[col_name] = df.iloc[:, i]
            
            # Map PE columns (with .1 suffix)
            for i, col_name in enumerate(pe_cols):
                pe_idx = 11 + i
                new_df[f"{col_name}.1"] = df.iloc[:, pe_idx]
            
            return new_df
        
        # If we have 20 columns (no label row), try alternate
        if len(cols) == 20:
            new_df = pd.DataFrame()
            
            # CE columns - positions 0-9
            ce_cols = ["Chg in OI", "OI", "VOLUME", "IV", "LTP", "CHNG", "BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY"]
            
            # PE columns - positions 10-19
            pe_cols = ["BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY", "CHNG", "LTP", "IV", "VOLUME", "OI", "Chg in OI"]
            
            # Map CE columns
            for i, col_name in enumerate(ce_cols):
                new_df[col_name] = df.iloc[:, i]
            
            # Map PE columns (with .1 suffix)
            for i, col_name in enumerate(pe_cols):
                pe_idx = 10 + i
                new_df[f"{col_name}.1"] = df.iloc[:, pe_idx]
            
            return new_df
        
        # Try to find strike column by name
        strike_col = None
        for col in cols:
            if "STRIKE" in col.upper() or "PRICE" in col.upper():
                strike_col = col
                break
        
        if strike_col:
            new_df = pd.DataFrame()
            new_df["STRIKE PRICE"] = df[strike_col]
            
            # Find CE columns
            ce_cols = ["Chg in OI", "OI", "VOLUME", "IV", "LTP", "CHNG", "BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY"]
            for col in ce_cols:
                if col in df.columns:
                    new_df[col] = df[col]
                else:
                    new_df[col] = 0
            
            # Find PE columns
            pe_cols = ["BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY", "CHNG", "LTP", "IV", "VOLUME", "OI", "Chg in OI"]
            for col in pe_cols:
                if f"{col}.1" in df.columns:
                    new_df[f"{col}.1"] = df[f"{col}.1"]
                elif col in df.columns:
                    # Check if there's a duplicate
                    if list(df.columns).count(col) >= 2:
                        # Find the second occurrence
                        col_indices = [i for i, c in enumerate(df.columns) if c == col]
                        if len(col_indices) >= 2:
                            # Use iloc to get the second column
                            new_df[f"{col}.1"] = df.iloc[:, col_indices[1]]
                        else:
                            new_df[f"{col}.1"] = 0
                    else:
                        new_df[f"{col}.1"] = 0
                else:
                    new_df[f"{col}.1"] = 0
            
            return new_df
        
        return df
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the option chain data - Fixed for chained assignment warnings"""
        if df is None or df.empty:
            return df
        
        # Make a copy to avoid chained assignment warnings
        processed = df.copy()
        
        # Clean numeric columns using loc to avoid chained assignment warnings
        numeric_columns = [
            "OI", "VOLUME", "IV", "LTP", "CHNG", "BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY",
            "OI.1", "VOLUME.1", "IV.1", "LTP.1", "CHNG.1", "BID QTY.1", "BID PRICE.1", "ASK PRICE.1", "ASK QTY.1"
        ]
        
        for col in numeric_columns:
            if col in processed.columns:
                # Use loc to avoid chained assignment warnings
                processed.loc[:, col] = processed[col].apply(clean_numeric)
        
        # Clean strike price
        if "STRIKE PRICE" in processed.columns:
            processed.loc[:, "STRIKE PRICE"] = processed["STRIKE PRICE"].apply(clean_numeric)
        
        # Remove rows with invalid strike prices
        processed = processed[processed["STRIKE PRICE"] > 0]
        
        # Fill missing values with 0
        processed = processed.fillna(0)
        
        return processed
    
    def get_option_chain(self, df: pd.DataFrame, filename: str) -> OptionChain:
        """Create OptionChain object from dataframe - Fixed for chained assignment warnings"""
        option_chain = OptionChain()
        
        option_chain.exchange = "NSE"
        option_chain.symbol = extract_symbol_from_filename(filename)
        option_chain.expiry = extract_expiry_from_filename(filename)
        option_chain.data = df
        
        if "STRIKE PRICE" in df.columns:
            strikes = df["STRIKE PRICE"].dropna().unique()
            strikes = sorted([s for s in strikes if s > 0])
            option_chain.strike_range = strikes
        
        # Estimate spot price using ATM strike - Fixed to avoid chained assignment
        if strikes:
            # Create a copy to avoid chained assignment
            df_copy = df.copy()
            
            # Find strike with highest total OI
            if "OI" in df_copy.columns and "OI.1" in df_copy.columns:
                # Use .loc to avoid chained assignment warnings
                df_copy.loc[:, "total_oi"] = df_copy["OI"] + df_copy["OI.1"]
            elif "OI" in df_copy.columns:
                df_copy.loc[:, "total_oi"] = df_copy["OI"]
            else:
                df_copy.loc[:, "total_oi"] = 0
            
            if not df_copy.empty and df_copy["total_oi"].max() > 0:
                max_oi_idx = df_copy["total_oi"].idxmax()
                option_chain.atm_strike = df_copy.loc[max_oi_idx, "STRIKE PRICE"]
                option_chain.spot_price = option_chain.atm_strike
            else:
                # Use middle strike
                mid_idx = len(strikes) // 2
                option_chain.atm_strike = strikes[mid_idx] if strikes else 0
                option_chain.spot_price = option_chain.atm_strike
        
        self.option_chain = option_chain
        return option_chain