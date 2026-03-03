import pandas as pd
import numpy as np
from typing import Dict, Any
from state import PreprocessingState


def validate_data_node(state: PreprocessingState) -> PreprocessingState:
    """
    Validator Agent - Validates the processed data for ML readiness.
    Checks for:
    - No null values
    - No infinite values
    - Proper data types
    - Sufficient data volume
    - Feature variance
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for validation")
        state["validation_passed"] = False
        return state
    
    validation_errors = []
    validation_warnings = []
    
    null_count = df.isnull().sum().sum()
    if null_count > 0:
        validation_errors.append(f"Data contains {null_count} null values")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        inf_count = np.isinf(df[col]).sum()
        if inf_count > 0:
            validation_errors.append(f"Column '{col}' contains {inf_count} infinite values")
    
    if df.shape[0] < 10:
        validation_errors.append(f"Insufficient data: only {df.shape[0]} rows (minimum 10 required)")
    elif df.shape[0] < 100:
        validation_warnings.append(f"Low data volume: {df.shape[0]} rows (recommended: 100+)")
    
    if df.shape[1] < 1:
        validation_errors.append("No features available after processing")
    
    for col in numeric_cols:
        if df[col].std() == 0:
            validation_warnings.append(f"Column '{col}' has zero variance")
    
    for col in df.columns:
        if df[col].dtype == 'object':
            validation_warnings.append(f"Column '{col}' is still object type (may need encoding)")
    
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        validation_warnings.append(f"Data contains {duplicate_count} duplicate rows")
    
    state["validation_passed"] = len(validation_errors) == 0
    state["validation_errors"] = validation_errors
    state["current_agent"] = "validator"
    
    if state["validation_passed"]:
        state["workflow_status"] = "completed"
        state["preprocessing_steps"].append(
            f"Validation passed with {len(validation_warnings)} warnings"
        )
        
        state["feedback_messages"].append({
            "from_agent": "validator",
            "to_agent": "orchestrator",
            "message": "Data validation passed - ready for ML training",
            "validation_summary": {
                "passed": True,
                "warnings": validation_warnings,
                "final_shape": df.shape,
                "numeric_features": len(numeric_cols),
                "total_features": df.shape[1]
            }
        })
    else:
        state["workflow_status"] = "validation_failed"
        state["preprocessing_steps"].append(
            f"Validation failed with {len(validation_errors)} errors"
        )
        
        state["feedback_messages"].append({
            "from_agent": "validator",
            "to_agent": "orchestrator",
            "message": "Data validation failed - requires reprocessing",
            "validation_summary": {
                "passed": False,
                "errors": validation_errors,
                "warnings": validation_warnings
            }
        })
    
    return state


def should_retry_node(state: PreprocessingState) -> PreprocessingState:
    """
    Retry Decision Agent - Determines if preprocessing should be retried with different strategies.
    """
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    validation_passed = state.get("validation_passed", False)
    
    if validation_passed:
        state["workflow_status"] = "completed"
        return state
    
    if iteration_count >= max_iterations:
        state["workflow_status"] = "max_iterations_reached"
        state["validation_errors"].append(
            f"Maximum iterations ({max_iterations}) reached without successful validation"
        )
        return state
    
    state["iteration_count"] = iteration_count + 1
    state["workflow_status"] = "retrying"
    
    if state.get("anomaly_handling_strategy") == "cap":
        state["anomaly_handling_strategy"] = "flag"
    elif state.get("null_handling_strategy") == "smart":
        state["null_handling_strategy"] = "median"
    
    state["feedback_messages"].append({
        "from_agent": "retry_decision",
        "to_agent": "anomaly_detector",
        "message": f"Retrying preprocessing (iteration {iteration_count + 1}/{max_iterations})",
        "retry_info": {
            "iteration": iteration_count + 1,
            "new_anomaly_strategy": state.get("anomaly_handling_strategy"),
            "new_null_strategy": state.get("null_handling_strategy")
        }
    })
    
    return state
