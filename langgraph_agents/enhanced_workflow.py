from typing import Literal
from langgraph.graph import StateGraph, END
from enhanced_state import EnhancedPreprocessingState
from nodes.data_loader_node import load_data_node
from nodes.schema_validator_node import validate_schema_node, enforce_schema_node
from nodes.data_type_caster_node import detect_and_cast_types_node, normalize_formats_node
from nodes.encoding_standardizer_node import standardize_encoding_node, check_referential_integrity_node
from nodes.anomaly_detector_node import detect_anomalies_node
from nodes.anomaly_handler_node import handle_anomalies_node
from nodes.null_handler_node import detect_null_values_node, handle_null_values_node
from nodes.data_quality_rules_node import apply_data_quality_rules_node, deduplicate_records_node
from nodes.feature_processor_node import process_features_node
from nodes.validator_node import validate_data_node, should_retry_node


def route_after_schema_validation(state: EnhancedPreprocessingState) -> Literal["enforce_schema", "cast_types"]:
    """Route based on schema validation result"""
    schema_result = state.get("schema_validation_result")
    
    if schema_result and not schema_result.get("valid", True):
        return "enforce_schema"
    else:
        return "cast_types"


def route_after_anomaly_detection(state: EnhancedPreprocessingState) -> Literal["handle_anomalies", "detect_nulls"]:
    """Route based on anomalies detected"""
    anomalies = state.get("anomalies_detected", [])
    return "handle_anomalies" if len(anomalies) > 0 else "detect_nulls"


def route_after_null_detection(state: EnhancedPreprocessingState) -> Literal["handle_nulls", "apply_quality_rules"]:
    """Route based on null values detected"""
    null_info = state.get("null_values_info", {})
    return "handle_nulls" if len(null_info) > 0 else "apply_quality_rules"


def route_after_validation(state: EnhancedPreprocessingState) -> Literal["retry", "end"]:
    """Route based on validation result"""
    validation_passed = state.get("validation_passed", False)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if validation_passed:
        return "end"
    elif iteration_count < max_iterations:
        return "retry"
    else:
        return "end"


def create_enhanced_preprocessing_workflow() -> StateGraph:
    """
    Creates enhanced LangGraph workflow with all data quality features.
    
    Workflow includes:
    1. Data Loading
    2. Schema Validation & Enforcement
    3. Data Type Casting
    4. Format Normalization
    5. Encoding Standardization
    6. Referential Integrity Checks
    7. Anomaly Detection & Handling
    8. Null Value Detection & Handling
    9. Data Quality Rules
    10. Deduplication
    11. Feature Processing
    12. Final Validation
    13. Retry Logic
    """
    workflow = StateGraph(EnhancedPreprocessingState)
    
    workflow.add_node("load_data", load_data_node)
    workflow.add_node("validate_schema", validate_schema_node)
    workflow.add_node("enforce_schema", enforce_schema_node)
    workflow.add_node("cast_types", detect_and_cast_types_node)
    workflow.add_node("normalize_formats", normalize_formats_node)
    workflow.add_node("standardize_encoding", standardize_encoding_node)
    workflow.add_node("check_referential_integrity", check_referential_integrity_node)
    workflow.add_node("detect_anomalies", detect_anomalies_node)
    workflow.add_node("handle_anomalies", handle_anomalies_node)
    workflow.add_node("detect_nulls", detect_null_values_node)
    workflow.add_node("handle_nulls", handle_null_values_node)
    workflow.add_node("apply_quality_rules", apply_data_quality_rules_node)
    workflow.add_node("deduplicate", deduplicate_records_node)
    workflow.add_node("process_features", process_features_node)
    workflow.add_node("validate", validate_data_node)
    workflow.add_node("retry_decision", should_retry_node)
    
    workflow.set_entry_point("load_data")
    
    workflow.add_edge("load_data", "validate_schema")
    
    workflow.add_conditional_edges(
        "validate_schema",
        route_after_schema_validation,
        {
            "enforce_schema": "enforce_schema",
            "cast_types": "cast_types"
        }
    )
    
    workflow.add_edge("enforce_schema", "cast_types")
    
    workflow.add_edge("cast_types", "normalize_formats")
    
    workflow.add_edge("normalize_formats", "standardize_encoding")
    
    workflow.add_edge("standardize_encoding", "check_referential_integrity")
    
    workflow.add_edge("check_referential_integrity", "detect_anomalies")
    
    workflow.add_conditional_edges(
        "detect_anomalies",
        route_after_anomaly_detection,
        {
            "handle_anomalies": "handle_anomalies",
            "detect_nulls": "detect_nulls"
        }
    )
    
    workflow.add_edge("handle_anomalies", "detect_nulls")
    
    workflow.add_conditional_edges(
        "detect_nulls",
        route_after_null_detection,
        {
            "handle_nulls": "handle_nulls",
            "apply_quality_rules": "apply_quality_rules"
        }
    )
    
    workflow.add_edge("handle_nulls", "apply_quality_rules")
    
    workflow.add_edge("apply_quality_rules", "deduplicate")
    
    workflow.add_edge("deduplicate", "process_features")
    
    workflow.add_edge("process_features", "validate")
    
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "retry": "retry_decision",
            "end": END
        }
    )
    
    workflow.add_edge("retry_decision", "detect_anomalies")
    
    return workflow.compile()
