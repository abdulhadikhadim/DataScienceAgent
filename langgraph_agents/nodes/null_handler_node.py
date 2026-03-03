import pandas as pd
import numpy as np
from typing import Dict, Any
from state import PreprocessingState


def detect_null_values_node(state: PreprocessingState) -> PreprocessingState:
    """
    Null Value Detector Agent - Detects and analyzes null values in the data.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for null detection")
        return state
    
    null_info = {}
    total_nulls = 0
    
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            null_percentage = (null_count / len(df)) * 100
            null_info[col] = {
                "count": int(null_count),
                "percentage": float(null_percentage),
                "dtype": str(df[col].dtype)
            }
            total_nulls += null_count
    
    state["null_values_info"] = null_info
    state["current_agent"] = "null_detector"
    state["preprocessing_steps"].append(
        f"Detected null values in {len(null_info)} columns (total: {total_nulls})"
    )
    
    if len(null_info) > 0:
        state["feedback_messages"].append({
            "from_agent": "null_detector",
            "to_agent": "null_handler",
            "message": f"Found null values in {len(null_info)} columns",
            "null_summary": {
                "affected_columns": list(null_info.keys()),
                "total_null_count": total_nulls,
                "null_percentage": (total_nulls / (df.shape[0] * df.shape[1])) * 100
            }
        })
    else:
        state["feedback_messages"].append({
            "from_agent": "null_detector",
            "to_agent": "feature_processor",
            "message": "No null values detected"
        })
    
    return state


def handle_null_values_node(state: PreprocessingState) -> PreprocessingState:
    """
    Null Value Handler Agent - Deterministically handles null values.
    Strategies: drop, mean, median, mode, forward_fill, backward_fill, constant
    """
    df = state.get("processed_data")
    null_info = state.get("null_values_info", {})
    strategy = state.get("null_handling_strategy", "smart")
    
    if df is None:
        state["validation_errors"].append("No data available for null handling")
        return state
    
    if len(null_info) == 0:
        state["preprocessing_steps"].append("No null values to handle")
        state["current_agent"] = "null_handler"
        return state
    
    df_processed = df.copy()
    handled_columns = []
    
    for col, info in null_info.items():
        if col not in df_processed.columns:
            continue
        
        null_percentage = info["percentage"]
        dtype = info["dtype"]
        
        if strategy == "smart":
            if null_percentage > 50:
                df_processed = df_processed.drop(columns=[col])
                handled_columns.append(f"{col} (dropped - >50% null)")
            
            elif "int" in dtype or "float" in dtype:
                if df_processed[col].skew() > 1:
                    df_processed[col] = df_processed[col].fillna(df_processed[col].median())
                    handled_columns.append(f"{col} (median)")
                else:
                    df_processed[col] = df_processed[col].fillna(df_processed[col].mean())
                    handled_columns.append(f"{col} (mean)")
            
            elif "object" in dtype or "category" in dtype:
                mode_value = df_processed[col].mode()
                if len(mode_value) > 0:
                    df_processed[col] = df_processed[col].fillna(mode_value[0])
                    handled_columns.append(f"{col} (mode)")
                else:
                    df_processed[col] = df_processed[col].fillna("Unknown")
                    handled_columns.append(f"{col} (constant)")
        
        elif strategy == "drop_rows":
            df_processed = df_processed.dropna(subset=[col])
            handled_columns.append(f"{col} (rows dropped)")
        
        elif strategy == "drop_columns":
            df_processed = df_processed.drop(columns=[col])
            handled_columns.append(f"{col} (column dropped)")
        
        elif strategy == "mean":
            if "int" in dtype or "float" in dtype:
                df_processed[col] = df_processed[col].fillna(df_processed[col].mean())
                handled_columns.append(f"{col} (mean)")
        
        elif strategy == "median":
            if "int" in dtype or "float" in dtype:
                df_processed[col] = df_processed[col].fillna(df_processed[col].median())
                handled_columns.append(f"{col} (median)")
        
        elif strategy == "mode":
            mode_value = df_processed[col].mode()
            if len(mode_value) > 0:
                df_processed[col] = df_processed[col].fillna(mode_value[0])
                handled_columns.append(f"{col} (mode)")
        
        elif strategy == "forward_fill":
            df_processed[col] = df_processed[col].ffill()
            handled_columns.append(f"{col} (forward fill)")
        
        elif strategy == "backward_fill":
            df_processed[col] = df_processed[col].bfill()
            handled_columns.append(f"{col} (backward fill)")
    
    state["processed_data"] = df_processed
    state["current_agent"] = "null_handler"
    state["preprocessing_steps"].append(
        f"Handled null values in {len(handled_columns)} columns using '{strategy}' strategy"
    )
    
    state["feedback_messages"].append({
        "from_agent": "null_handler",
        "to_agent": "feature_processor",
        "message": f"Null values handled using {strategy} strategy",
        "handling_summary": {
            "strategy_used": strategy,
            "columns_handled": len(handled_columns),
            "new_shape": df_processed.shape,
            "remaining_nulls": int(df_processed.isnull().sum().sum())
        }
    })
    
    return state
