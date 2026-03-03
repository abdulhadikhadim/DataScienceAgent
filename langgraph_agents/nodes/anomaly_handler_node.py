import pandas as pd
import numpy as np
from typing import Dict, Any
from state import PreprocessingState


def handle_anomalies_node(state: PreprocessingState) -> PreprocessingState:
    """
    Anomaly Handler Agent - Deterministically handles detected anomalies.
    Strategies: cap, remove, transform, flag
    """
    df = state.get("processed_data")
    anomalies = state.get("anomalies_detected", [])
    strategy = state.get("anomaly_handling_strategy", "cap")
    
    if df is None:
        state["validation_errors"].append("No data available for anomaly handling")
        return state
    
    if len(anomalies) == 0:
        state["preprocessing_steps"].append("No anomalies to handle")
        state["current_agent"] = "anomaly_handler"
        return state
    
    df_processed = df.copy()
    handled_count = 0
    
    for anomaly in anomalies:
        column = anomaly["column"]
        method = anomaly["method"]
        
        if column not in df_processed.columns:
            continue
        
        if method in ["IQR", "Z-Score"]:
            if strategy == "cap":
                if "lower_bound" in anomaly and "upper_bound" in anomaly:
                    lower = anomaly["lower_bound"]
                    upper = anomaly["upper_bound"]
                    df_processed[column] = df_processed[column].clip(lower=lower, upper=upper)
                    handled_count += 1
            
            elif strategy == "remove":
                indices = anomaly.get("indices", [])
                df_processed = df_processed.drop(index=indices, errors='ignore')
                handled_count += 1
            
            elif strategy == "transform":
                if df_processed[column].dtype in [np.float64, np.int64]:
                    df_processed[column] = np.log1p(df_processed[column].clip(lower=0))
                    handled_count += 1
            
            elif strategy == "flag":
                flag_col = f"{column}_anomaly_flag"
                df_processed[flag_col] = False
                indices = anomaly.get("indices", [])
                df_processed.loc[indices, flag_col] = True
                handled_count += 1
        
        elif method == "Rare_Categories":
            if strategy == "group":
                rare_values = list(anomaly.get("rare_values", {}).keys())
                df_processed.loc[df_processed[column].isin(rare_values), column] = "Other"
                handled_count += 1
            elif strategy == "remove":
                rare_values = list(anomaly.get("rare_values", {}).keys())
                df_processed = df_processed[~df_processed[column].isin(rare_values)]
                handled_count += 1
    
    state["processed_data"] = df_processed
    state["current_agent"] = "anomaly_handler"
    state["preprocessing_steps"].append(
        f"Handled {handled_count} anomaly patterns using '{strategy}' strategy"
    )
    
    state["feedback_messages"].append({
        "from_agent": "anomaly_handler",
        "to_agent": "null_handler",
        "message": f"Anomalies handled using {strategy} strategy",
        "handling_summary": {
            "strategy_used": strategy,
            "patterns_handled": handled_count,
            "new_shape": df_processed.shape,
            "rows_removed": df.shape[0] - df_processed.shape[0] if strategy == "remove" else 0
        }
    })
    
    return state
