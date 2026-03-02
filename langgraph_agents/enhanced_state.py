from typing import TypedDict, List, Dict, Any, Optional, Annotated
from operator import add
import pandas as pd


class EnhancedPreprocessingState(TypedDict):
    """
    Enhanced state for comprehensive preprocessing workflow.
    Includes all new data quality features.
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
    
    schema_validation_result: Optional[Dict[str, Any]]
    type_casting_changes: Annotated[List[str], add]
    format_normalizations: Annotated[List[str], add]
    encoding_fixes: Annotated[List[str], add]
    
    referential_integrity_issues: Annotated[List[str], add]
    quality_rule_violations: Annotated[List[Dict[str, Any]], add]
    quarantine_records: Optional[pd.DataFrame]
    
    duplicates_removed: int
    
    parallel_execution_enabled: bool
    chunk_processing_enabled: bool
    partition_strategy: Optional[str]
    
    performance_metrics: Dict[str, Any]
