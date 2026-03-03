from typing import TypedDict, List, Dict, Any, Optional
import pandas as pd


class PreprocessingState(TypedDict):
    """
    Shared state for the LangGraph preprocessing workflow.
    This state is passed between all agents in the graph.
    
    Note: Lists are NOT annotated with add operator to avoid MemoryError.
    Each node should modify the state dict in place and return it.
    """
    raw_data: Optional[pd.DataFrame]
    processed_data: Optional[pd.DataFrame]
    
    data_source: Optional[str]
    data_format: Optional[str]
    
    anomalies_detected: List[Dict[str, Any]]
    null_values_info: Dict[str, Any]
    preprocessing_steps: List[str]
    
    anomaly_handling_strategy: str
    null_handling_strategy: str
    
    validation_passed: bool
    validation_errors: List[str]
    
    current_agent: str
    workflow_status: str
    
    metadata: Dict[str, Any]
    feedback_messages: List[Dict[str, Any]]
    
    iteration_count: int
    max_iterations: int
