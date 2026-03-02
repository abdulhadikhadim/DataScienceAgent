from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph_agents.state import PreprocessingState
from langgraph_agents.nodes.data_loader_node import load_data_node
from langgraph_agents.nodes.anomaly_detector_node import detect_anomalies_node
from langgraph_agents.nodes.anomaly_handler_node import handle_anomalies_node
from langgraph_agents.nodes.null_handler_node import detect_null_values_node, handle_null_values_node
from langgraph_agents.nodes.feature_processor_node import process_features_node
from langgraph_agents.nodes.validator_node import validate_data_node, should_retry_node


def route_after_anomaly_detection(state: PreprocessingState) -> Literal["handle_anomalies", "detect_nulls"]:
    """
    Conditional edge: Route based on whether anomalies were detected.
    """
    anomalies = state.get("anomalies_detected", [])
    if len(anomalies) > 0:
        return "handle_anomalies"
    else:
        return "detect_nulls"


def route_after_null_detection(state: PreprocessingState) -> Literal["handle_nulls", "process_features"]:
    """
    Conditional edge: Route based on whether null values were detected.
    """
    null_info = state.get("null_values_info", {})
    if len(null_info) > 0:
        return "handle_nulls"
    else:
        return "process_features"


def route_after_validation(state: PreprocessingState) -> Literal["retry", "end"]:
    """
    Conditional edge: Route based on validation result.
    """
    validation_passed = state.get("validation_passed", False)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if validation_passed:
        return "end"
    elif iteration_count < max_iterations:
        return "retry"
    else:
        return "end"


def create_preprocessing_workflow() -> StateGraph:
    """
    Creates the LangGraph workflow for data preprocessing.
    
    Workflow:
    1. Load Data
    2. Detect Anomalies
    3. Handle Anomalies (if detected)
    4. Detect Null Values
    5. Handle Null Values (if detected)
    6. Process Features
    7. Validate Data
    8. Retry or End (based on validation)
    
    The workflow includes feedback loops where agents communicate results
    and can trigger re-processing with different strategies.
    """
    workflow = StateGraph(PreprocessingState)
    
    workflow.add_node("load_data", load_data_node)
    workflow.add_node("detect_anomalies", detect_anomalies_node)
    workflow.add_node("handle_anomalies", handle_anomalies_node)
    workflow.add_node("detect_nulls", detect_null_values_node)
    workflow.add_node("handle_nulls", handle_null_values_node)
    workflow.add_node("process_features", process_features_node)
    workflow.add_node("validate", validate_data_node)
    workflow.add_node("retry_decision", should_retry_node)
    
    workflow.set_entry_point("load_data")
    
    workflow.add_edge("load_data", "detect_anomalies")
    
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
            "process_features": "process_features"
        }
    )
    
    workflow.add_edge("handle_nulls", "process_features")
    
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
