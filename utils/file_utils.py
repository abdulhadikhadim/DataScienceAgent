import pandas as pd
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import mimetypes
import chardet

from config.settings import Config


def detect_file_type(file_path: Path) -> str:
    """
    Detect the file type based on extension and content.
    Returns a string representing the file type.
    """
    # Get the file extension
    ext = file_path.suffix.lower()
    
    # Map extensions to file types
    ext_to_type = {
        '.csv': 'csv',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.json': 'json',
        '.parquet': 'parquet',
        '.txt': 'text',
        '.tsv': 'tsv'
    }
    
    # Return mapped type or unknown
    return ext_to_type.get(ext, 'unknown')


def scan_for_data_files(search_dirs: List[Path]) -> List[Dict[str, any]]:
    """
    Scan directories for data files and return a list of file information.
    """
    found_files = []
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for file_path in search_dir.rglob('*'):
            if file_path.is_file():
                # Check if file extension is supported
                if file_path.suffix.lower() in Config.SUPPORTED_EXTENSIONS:
                    # Check file size
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    if file_size_mb <= Config.MAX_FILE_SIZE_MB:
                        file_info = {
                            'path': file_path,
                            'name': file_path.name,
                            'size_mb': round(file_size_mb, 2),
                            'type': detect_file_type(file_path),
                            'extension': file_path.suffix
                        }
                        found_files.append(file_info)
    
    return found_files


def detect_encoding(file_path: Path) -> str:
    """
    Detect the encoding of a text file.
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Read first 10KB to detect encoding
        result = chardet.detect(raw_data)
        return result['encoding'] or Config.DEFAULT_ENCODING


def find_header_row(df_sample: pd.DataFrame, columns_list: List[str]) -> int:
    """
    Find the row that contains headers by checking common column names.
    """
    # Common column names that might appear in datasets
    common_columns = {
        'name', 'id', 'date', 'time', 'timestamp', 'value', 'amount', 
        'count', 'type', 'category', 'description', 'index', 'row', 'col',
        'first_name', 'last_name', 'email', 'phone', 'address', 'city',
        'state', 'country', 'product', 'price', 'quantity', 'total'
    }
    
    # Check each row to see if it contains likely header names
    for idx in range(min(len(df_sample), Config.HEADER_DETECTION_ROWS)):
        row_values = df_sample.iloc[idx].astype(str).str.lower()
        matched_cols = [col for col in row_values if col.replace('_', '').replace(' ', '') in common_columns]
        
        # If we find a significant number of potential header names, consider this the header row
        if len(matched_cols) >= max(1, len(df_sample.columns) * 0.5):  # At least 50% of columns match
            return idx
    
    return 0  # Default to first row


def load_data_with_fallback(file_path: Path, file_type: str) -> pd.DataFrame:
    """
    Load data file with fallback mechanisms for header detection.
    """
    df = None
    
    try:
        if file_type == 'csv':
            # Try to detect the proper starting row by examining the file content
            # Read the file line by line to find where the actual data begins
            with open(file_path, 'r', encoding=Config.DEFAULT_ENCODING) as f:
                lines = f.readlines()
            
            # Find the first line that has multiple comma-separated values
            header_row_idx = 0
            for i, line in enumerate(lines):
                parts = line.strip().split(',')
                if len(parts) > 1:  # Found a line with multiple columns
                    header_row_idx = i
                    break
            
            # Now read the CSV starting from the detected header row
            df = pd.read_csv(file_path, encoding=Config.DEFAULT_ENCODING, skiprows=header_row_idx, header=0)
            
        elif file_type in ['excel', 'xlsx', 'xls']:
            # Excel files
            df = pd.read_excel(file_path, header=0)
            
            # If first row seems to be data rather than headers, try to detect headers
            if not _looks_like_headers(df):
                df_temp = pd.read_excel(file_path, header=None)
                header_row = find_header_row(df_temp.head(10), list(df_temp.columns))
                df = pd.read_excel(file_path, header=header_row)
                
        elif file_type == 'json':
            df = pd.read_json(file_path)
            
        elif file_type == 'parquet':
            df = pd.read_parquet(file_path)
            
        elif file_type in ['text', 'txt']:
            # Detect encoding for text files
            encoding = detect_encoding(file_path)
            
            # Try to detect the delimiter and header row
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # Find the first line that has multiple separated values
            header_row_idx = 0
            delimiter = ','  # Default assumption
            for i, line in enumerate(lines):
                # Try common delimiters
                for delim in [',', '\t', ';', '|']:
                    parts = line.strip().split(delim)
                    if len(parts) > 1:  # Found a line with multiple columns
                        delimiter = delim
                        header_row_idx = i
                        break
                else:
                    continue
                break
            
            df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, skiprows=header_row_idx, header=0)
            
            if not _looks_like_headers(df):
                df_temp = pd.read_csv(file_path, encoding=encoding, sep=delimiter, header=None)
                header_row = find_header_row(df_temp.head(10), list(df_temp.columns))
                df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, header=header_row)
                
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        raise
    
    return df


def _looks_like_headers(df: pd.DataFrame) -> bool:
    """
    Heuristic to determine if the first row looks like headers.
    """
    if df.empty:
        return False
    
    first_row = df.iloc[0]
    
    # Check if first row values look like headers (strings, not numbers)
    header_likelihood = 0
    for val in first_row:
        val_str = str(val).strip().lower()
        
        # If it's numeric, probably not a header
        try:
            float(val_str)
            continue  # Skip numeric values
        except ValueError:
            pass
        
        # If it contains common header indicators
        if any(indicator in val_str for indicator in ['_', ' ', 'id', 'name', 'date', 'time']):
            header_likelihood += 1
    
    # If at least half of non-numeric values look like headers
    non_numeric_count = sum(1 for val in first_row if not pd.api.types.is_numeric_dtype(type(val)) and not str(val).strip().isdigit())
    return header_likelihood >= max(1, non_numeric_count * 0.5)