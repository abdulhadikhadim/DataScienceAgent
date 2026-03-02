from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add
import pandas as pd


class PreprocessingState(TypedDict):
    """
    Shared state for the LangGraph preprocessing workflow.
    This state is passed between all agents in the graph.
    """
    raw_data: Optional[pd.DataFrame]
    processed_data: Optional[pd.DataFrame]
    
    data_source: Optional[str]
    data_format: Optional[str]
    
    anomalies_detected: Annotated[List[Dict[str, Any]], add]
    null_values_info: Dict[str, Any]
    preprocessing_steps: Annotated[List[str], add]
    
    anomaly_handling_strategy: str
    null_handling_strategy: str
    
    validation_passed: bool
    validation_errors: Annotated[List[str], add]
    
    current_agent: str
    workflow_status: str
    
    metadata: Dict[str, Any]
    feedback_messages: Annotated[List[Dict[str, Any]], add]
    
    iteration_count: int
    max_iterations: int
