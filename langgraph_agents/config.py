from pathlib import Path
from typing import Dict, Any


class LangGraphConfig:
    """
    Configuration settings for the LangGraph preprocessing system.
    """
    
    DEFAULT_ANOMALY_STRATEGY = "cap"
    DEFAULT_NULL_STRATEGY = "smart"
    DEFAULT_MAX_ITERATIONS = 3
    
    ANOMALY_STRATEGIES = [
        "cap",
        "remove", 
        "transform",
        "flag",
        "group"
    ]
    
    NULL_STRATEGIES = [
        "smart",
        "drop_rows",
        "drop_columns",
        "mean",
        "median",
        "mode",
        "forward_fill",
        "backward_fill"
    ]
    
    SUPPORTED_FORMATS = [
        ".csv",
        ".xlsx",
        ".xls",
        ".json",
        ".parquet"
    ]
    
    IQR_MULTIPLIER = 1.5
    
    Z_SCORE_THRESHOLD = 3.0
    
    RARE_CATEGORY_THRESHOLD = 0.01
    
    NULL_DROP_THRESHOLD = 0.5
    
    MIN_DATA_ROWS = 10
    
    RECOMMENDED_DATA_ROWS = 100
    
    ONE_HOT_MAX_CATEGORIES = 10
    
    OUTPUT_FORMATS = {
        "csv": ".csv",
        "excel": ".xlsx",
        "parquet": ".parquet",
        "json": ".json"
    }
    
    @staticmethod
    def get_default_state() -> Dict[str, Any]:
        """
        Get default initial state configuration.
        """
        return {
            "raw_data": None,
            "processed_data": None,
            "data_source": None,
            "data_format": None,
            "anomalies_detected": [],
            "null_values_info": {},
            "preprocessing_steps": [],
            "anomaly_handling_strategy": LangGraphConfig.DEFAULT_ANOMALY_STRATEGY,
            "null_handling_strategy": LangGraphConfig.DEFAULT_NULL_STRATEGY,
            "validation_passed": False,
            "validation_errors": [],
            "current_agent": "orchestrator",
            "workflow_status": "initializing",
            "metadata": {},
            "feedback_messages": [],
            "iteration_count": 0,
            "max_iterations": LangGraphConfig.DEFAULT_MAX_ITERATIONS
        }
    
    @staticmethod
    def validate_strategy(strategy_type: str, strategy: str) -> bool:
        """
        Validate if a strategy is supported.
        """
        if strategy_type == "anomaly":
            return strategy in LangGraphConfig.ANOMALY_STRATEGIES
        elif strategy_type == "null":
            return strategy in LangGraphConfig.NULL_STRATEGIES
        return False
    
    @staticmethod
    def validate_file_format(file_path: str) -> bool:
        """
        Validate if a file format is supported.
        """
        file_extension = Path(file_path).suffix.lower()
        return file_extension in LangGraphConfig.SUPPORTED_FORMATS
