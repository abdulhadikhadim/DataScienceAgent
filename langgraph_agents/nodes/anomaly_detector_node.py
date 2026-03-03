import pandas as pd
import numpy as np
from typing import Dict, Any, List
from state import PreprocessingState


def detect_anomalies_node(state: PreprocessingState) -> PreprocessingState:
    """
    Anomaly Detector Agent - Deterministically detects anomalies in the data.
    Uses statistical methods: IQR, Z-score, and domain-specific rules.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for anomaly detection")
        return state
    
    anomalies = []
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            continue
        
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outlier_indices = df[outlier_mask].index.tolist()
        
        if len(outlier_indices) > 0:
            anomalies.append({
                "column": col,
                "method": "IQR",
                "count": len(outlier_indices),
                "indices": outlier_indices[:100],
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "values": df.loc[outlier_indices[:10], col].tolist()
            })
        
        mean = col_data.mean()
        std = col_data.std()
        
        if std > 0:
            z_scores = np.abs((df[col] - mean) / std)
            z_outlier_mask = z_scores > 3
            z_outlier_indices = df[z_outlier_mask].index.tolist()
            
            if len(z_outlier_indices) > 0:
                anomalies.append({
                    "column": col,
                    "method": "Z-Score",
                    "count": len(z_outlier_indices),
                    "indices": z_outlier_indices[:100],
                    "threshold": 3.0,
                    "values": df.loc[z_outlier_indices[:10], col].tolist()
                })
    
    for col in df.columns:
        if df[col].dtype == 'object':
            value_counts = df[col].value_counts()
            total_count = len(df[col].dropna())
            
            rare_values = value_counts[value_counts / total_count < 0.01]
            
            if len(rare_values) > 0:
                anomalies.append({
                    "column": col,
                    "method": "Rare_Categories",
                    "count": rare_values.sum(),
                    "rare_values": rare_values.to_dict(),
                    "threshold_percentage": 1.0
                })
    
    state["anomalies_detected"] = anomalies
    state["current_agent"] = "anomaly_detector"
    state["preprocessing_steps"].append(f"Detected {len(anomalies)} anomaly patterns")
    
    if len(anomalies) > 0:
        state["feedback_messages"].append({
            "from_agent": "anomaly_detector",
            "to_agent": "anomaly_handler",
            "message": f"Found {len(anomalies)} anomaly patterns requiring handling",
            "anomaly_summary": {
                "total_patterns": len(anomalies),
                "affected_columns": list(set([a["column"] for a in anomalies])),
                "methods_used": list(set([a["method"] for a in anomalies]))
            }
        })
    else:
        state["feedback_messages"].append({
            "from_agent": "anomaly_detector",
            "to_agent": "null_handler",
            "message": "No anomalies detected, proceeding to null value handling"
        })
    
    return state
