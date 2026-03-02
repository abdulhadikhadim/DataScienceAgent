import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
import re
from langgraph_agents.state import PreprocessingState


def detect_and_cast_types_node(state: PreprocessingState) -> PreprocessingState:
    """
    Data Type Caster Agent - Automatically detects and casts wrong data types.
    Handles type inference and conversion at ingestion layer.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for type casting")
        return state
    
    df_casted = df.copy()
    type_changes = []
    
    for col in df_casted.columns:
        original_dtype = str(df_casted[col].dtype)
        
        if df_casted[col].dtype == 'object':
            casted = False
            
            try:
                numeric_converted = pd.to_numeric(df_casted[col], errors='coerce')
                non_null_count = numeric_converted.notna().sum()
                
                if non_null_count / len(df_casted) > 0.8:
                    if (numeric_converted.dropna() % 1 == 0).all():
                        df_casted[col] = numeric_converted.astype('Int64')
                        type_changes.append(f"{col}: object -> Int64")
                        casted = True
                    else:
                        df_casted[col] = numeric_converted
                        type_changes.append(f"{col}: object -> float64")
                        casted = True
            except:
                pass
            
            if not casted:
                try:
                    date_converted = pd.to_datetime(df_casted[col], errors='coerce')
                    non_null_count = date_converted.notna().sum()
                    
                    if non_null_count / len(df_casted) > 0.8:
                        df_casted[col] = date_converted
                        type_changes.append(f"{col}: object -> datetime64[ns]")
                        casted = True
                except:
                    pass
            
            if not casted:
                unique_count = df_casted[col].nunique()
                if unique_count == 2:
                    unique_vals = df_casted[col].dropna().unique()
                    bool_like = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
                    if all(str(v).lower() in bool_like for v in unique_vals):
                        bool_map = {
                            'true': True, 'false': False,
                            'yes': True, 'no': False,
                            '1': True, '0': False,
                            't': True, 'f': False,
                            'y': True, 'n': False
                        }
                        df_casted[col] = df_casted[col].str.lower().map(bool_map)
                        type_changes.append(f"{col}: object -> bool")
                        casted = True
            
            if not casted and unique_count < len(df_casted) * 0.5:
                df_casted[col] = df_casted[col].astype('category')
                type_changes.append(f"{col}: object -> category")
    
    state["processed_data"] = df_casted
    state["current_agent"] = "data_type_caster"
    state["preprocessing_steps"].append(
        f"Type casting applied to {len(type_changes)} columns"
    )
    
    state["metadata"]["type_changes"] = type_changes
    
    state["feedback_messages"].append({
        "from_agent": "data_type_caster",
        "to_agent": "format_normalizer",
        "message": f"Data types casted for {len(type_changes)} columns",
        "type_changes": type_changes
    })
    
    return state


def normalize_formats_node(state: PreprocessingState) -> PreprocessingState:
    """
    Format Normalizer Agent - Normalizes inconsistent formats (dates, strings).
    Uses regex and parsing rules for standardization.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for format normalization")
        return state
    
    df_normalized = df.copy()
    normalizations = []
    
    for col in df_normalized.columns:
        if df_normalized[col].dtype == 'object':
            df_normalized[col] = df_normalized[col].str.strip()
            normalizations.append(f"{col}: trimmed whitespace")
            
            if df_normalized[col].str.contains(r'^\d{4}-\d{2}-\d{2}', na=False).any():
                try:
                    df_normalized[col] = pd.to_datetime(df_normalized[col], format='%Y-%m-%d', errors='coerce')
                    normalizations.append(f"{col}: normalized date format to YYYY-MM-DD")
                except:
                    pass
            
            elif df_normalized[col].str.contains(r'^\d{2}/\d{2}/\d{4}', na=False).any():
                try:
                    df_normalized[col] = pd.to_datetime(df_normalized[col], format='%m/%d/%Y', errors='coerce')
                    normalizations.append(f"{col}: normalized date format from MM/DD/YYYY")
                except:
                    pass
            
            if df_normalized[col].dtype == 'object':
                email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                if df_normalized[col].str.match(email_pattern, na=False).any():
                    df_normalized[col] = df_normalized[col].str.lower()
                    normalizations.append(f"{col}: normalized email to lowercase")
                
                phone_pattern = r'[\d\(\)\-\s\+]+'
                if df_normalized[col].str.contains(phone_pattern, na=False).any():
                    df_normalized[col] = df_normalized[col].str.replace(r'[^\d]', '', regex=True)
                    normalizations.append(f"{col}: normalized phone numbers (digits only)")
                
                if df_normalized[col].str.isupper().any() or df_normalized[col].str.islower().any():
                    df_normalized[col] = df_normalized[col].str.title()
                    normalizations.append(f"{col}: normalized text to title case")
        
        elif pd.api.types.is_datetime64_any_dtype(df_normalized[col]):
            df_normalized[col] = df_normalized[col].dt.normalize()
            normalizations.append(f"{col}: normalized datetime to date only")
    
    state["processed_data"] = df_normalized
    state["current_agent"] = "format_normalizer"
    state["preprocessing_steps"].append(
        f"Format normalization applied {len(normalizations)} changes"
    )
    
    state["feedback_messages"].append({
        "from_agent": "format_normalizer",
        "to_agent": "encoding_standardizer",
        "message": f"Formats normalized with {len(normalizations)} changes",
        "normalizations": normalizations[:10]
    })
    
    return state
