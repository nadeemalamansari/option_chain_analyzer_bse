"""File handling utilities"""

import os
import pandas as pd
from typing import Optional, Tuple
import streamlit as st


class FileHandler:
    """Handle file operations for option chain data"""
    
    @staticmethod
    def load_option_chain(file) -> Optional[pd.DataFrame]:
        """
        Load option chain data from uploaded file
        Supports CSV, Excel, and TSV formats
        """
        try:
            file_extension = os.path.splitext(file.name)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file, encoding='utf-8')
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file)
            elif file_extension == '.tsv':
                df = pd.read_csv(file, sep='\t', encoding='utf-8')
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return None
            
            return df
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None
    
    @staticmethod
    def validate_option_chain(df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate option chain data structure
        Returns (is_valid, message)
        """
        required_columns = [
            "STRIKE PRICE",
            "Chg in OI", "OI", "VOLUME", "IV", "LTP", "CHNG",
            "BID QTY", "BID PRICE", "ASK PRICE", "ASK QTY"
        ]
        
        # Check for call side columns
        ce_columns = [col for col in required_columns if col in df.columns]
        if len(ce_columns) < 5:
            return False, "Missing required Call side columns"
        
        # Check for put side columns
        pe_columns = [col for col in df.columns if col.endswith('.1')]
        if len(pe_columns) < 5:
            return False, "Missing required Put side columns (columns should end with .1)"
        
        # Check for strike price
        if "STRIKE PRICE" not in df.columns:
            return False, "Missing STRIKE PRICE column"
        
        return True, "Valid option chain data"
    
    @staticmethod
    def get_file_info(file) -> dict:
        """Get information about the uploaded file"""
        return {
            "name": file.name,
            "size": file.size,
            "type": file.type,
            "extension": os.path.splitext(file.name)[1].lower()
        }