from typing import TypedDict, List, Dict, Any, Optional
import pandas as pd


class EnhancedPreprocessingState(TypedDict):
    """
    Enhanced state for comprehensive preprocessing workflow.
    Includes all new data quality features.
    
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
    
    schema_validation_result: Optional[Dict[str, Any]]
    type_casting_changes: List[str]
    format_normalizations: List[str]
    encoding_fixes: List[str]
    
    referential_integrity_issues: List[str]
    quality_rule_violations: List[Dict[str, Any]]
    quarantine_records: Optional[pd.DataFrame]
    
    duplicates_removed: int
    
    parallel_execution_enabled: bool
    chunk_processing_enabled: bool
    partition_strategy: Optional[str]
    
    performance_metrics: Dict[str, Any]
