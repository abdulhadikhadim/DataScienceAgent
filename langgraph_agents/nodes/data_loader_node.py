from pathlib import Path
import pandas as pd
from typing import Dict, Any
from langgraph_agents.state import PreprocessingState


def load_data_node(state: PreprocessingState) -> PreprocessingState:
    """
    Data Loader Agent - Deterministically loads data from various sources.
    Supports CSV, Excel, JSON, Parquet formats.
    """
    data_source = state.get("data_source")
    
    if not data_source:
        state["workflow_status"] = "error"
        state["validation_errors"].append("No data source provided")
        return state
    
    try:
        file_path = Path(data_source)
        
        if not file_path.exists():
            state["workflow_status"] = "error"
            state["validation_errors"].append(f"File not found: {data_source}")
            return state
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
            state["data_format"] = "csv"
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            state["data_format"] = "excel"
        elif file_extension == '.json':
            df = pd.read_json(file_path)
            state["data_format"] = "json"
        elif file_extension == '.parquet':
            df = pd.read_parquet(file_path)
            state["data_format"] = "parquet"
        else:
            state["workflow_status"] = "error"
            state["validation_errors"].append(f"Unsupported file format: {file_extension}")
            return state
        
        state["raw_data"] = df
        state["processed_data"] = df.copy()
        state["current_agent"] = "data_loader"
        state["workflow_status"] = "data_loaded"
        
        state["preprocessing_steps"].append(f"Loaded data from {data_source}")
        
        state["metadata"] = {
            "original_shape": df.shape,
            "original_columns": list(df.columns),
            "original_dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "file_path": str(file_path),
            "file_format": state["data_format"]
        }
        
        state["feedback_messages"].append({
            "from_agent": "data_loader",
            "to_agent": "anomaly_detector",
            "message": f"Data loaded successfully with shape {df.shape}",
            "data_info": {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2
            }
        })
        
    except Exception as e:
        state["workflow_status"] = "error"
        state["validation_errors"].append(f"Error loading data: {str(e)}")
    
    return state
