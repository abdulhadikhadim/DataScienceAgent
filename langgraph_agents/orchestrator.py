from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from langgraph_agents.workflow import create_preprocessing_workflow
from langgraph_agents.state import PreprocessingState


class DataPreprocessingOrchestrator:
    """
    Main orchestrator for the LangGraph-based data preprocessing system.
    Manages the entire preprocessing workflow using deterministic agents.
    """
    
    def __init__(self):
        self.workflow = create_preprocessing_workflow()
        self.last_state = None
    
    def preprocess_data(
        self,
        data_source: str,
        anomaly_strategy: str = "cap",
        null_strategy: str = "smart",
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Run the complete preprocessing workflow on a data source.
        
        Args:
            data_source: Path to the data file
            anomaly_strategy: Strategy for handling anomalies 
                             (cap, remove, transform, flag, group)
            null_strategy: Strategy for handling null values 
                          (smart, drop_rows, drop_columns, mean, median, mode, 
                           forward_fill, backward_fill)
            max_iterations: Maximum number of retry iterations
        
        Returns:
            Dictionary containing processed data and workflow information
        """
        initial_state: PreprocessingState = {
            "raw_data": None,
            "processed_data": None,
            "data_source": data_source,
            "data_format": None,
            "anomalies_detected": [],
            "null_values_info": {},
            "preprocessing_steps": [],
            "anomaly_handling_strategy": anomaly_strategy,
            "null_handling_strategy": null_strategy,
            "validation_passed": False,
            "validation_errors": [],
            "current_agent": "orchestrator",
            "workflow_status": "initializing",
            "metadata": {},
            "feedback_messages": [],
            "iteration_count": 0,
            "max_iterations": max_iterations
        }
        
        final_state = self.workflow.invoke(initial_state)
        
        self.last_state = final_state
        
        return {
            "success": final_state.get("validation_passed", False),
            "workflow_status": final_state.get("workflow_status"),
            "processed_data": final_state.get("processed_data"),
            "preprocessing_steps": final_state.get("preprocessing_steps"),
            "anomalies_detected": final_state.get("anomalies_detected"),
            "null_values_info": final_state.get("null_values_info"),
            "validation_errors": final_state.get("validation_errors"),
            "feedback_messages": final_state.get("feedback_messages"),
            "metadata": final_state.get("metadata"),
            "iterations_used": final_state.get("iteration_count", 0)
        }
    
    def get_processed_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get the processed dataframe from the last run.
        """
        if self.last_state:
            return self.last_state.get("processed_data")
        return None
    
    def save_processed_data(self, output_path: str, format: str = "csv") -> bool:
        """
        Save the processed data to a file.
        
        Args:
            output_path: Path where to save the file
            format: Output format (csv, excel, parquet, json)
        
        Returns:
            True if successful, False otherwise
        """
        df = self.get_processed_dataframe()
        
        if df is None:
            print("No processed data available to save")
            return False
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "csv":
                df.to_csv(output_file, index=False)
            elif format == "excel":
                df.to_excel(output_file, index=False)
            elif format == "parquet":
                df.to_parquet(output_file)
            elif format == "json":
                df.to_json(output_file, orient="records", indent=2)
            else:
                print(f"Unsupported format: {format}")
                return False
            
            print(f"Processed data saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error saving processed data: {e}")
            return False
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the last workflow execution.
        """
        if not self.last_state:
            return {"error": "No workflow has been executed yet"}
        
        return {
            "workflow_status": self.last_state.get("workflow_status"),
            "validation_passed": self.last_state.get("validation_passed"),
            "preprocessing_steps": self.last_state.get("preprocessing_steps"),
            "iterations_used": self.last_state.get("iteration_count", 0),
            "anomalies_count": len(self.last_state.get("anomalies_detected", [])),
            "null_columns_count": len(self.last_state.get("null_values_info", {})),
            "validation_errors": self.last_state.get("validation_errors", []),
            "final_shape": self.last_state.get("processed_data").shape if self.last_state.get("processed_data") is not None else None,
            "feedback_messages_count": len(self.last_state.get("feedback_messages", []))
        }
    
    def get_feedback_log(self) -> list:
        """
        Get the complete feedback log showing agent communication.
        """
        if not self.last_state:
            return []
        
        return self.last_state.get("feedback_messages", [])
    
    def visualize_workflow(self) -> str:
        """
        Generate a text representation of the workflow graph.
        """
        workflow_description = """
        LangGraph Data Preprocessing Workflow
        =====================================
        
        [START]
           ↓
        [Load Data] ← Entry point
           ↓
        [Detect Anomalies]
           ↓
           ├─→ [Handle Anomalies] (if anomalies detected)
           │      ↓
           └─→ [Detect Null Values]
                  ↓
                  ├─→ [Handle Null Values] (if nulls detected)
                  │      ↓
                  └─→ [Process Features]
                         ↓
                      [Validate Data]
                         ↓
                         ├─→ [END] (if validation passed)
                         │
                         └─→ [Retry Decision] (if validation failed)
                                ↓
                                └─→ [Detect Anomalies] (feedback loop)
        
        Agent Communication Flow:
        - Data Loader → Anomaly Detector
        - Anomaly Detector → Anomaly Handler
        - Anomaly Handler → Null Handler
        - Null Detector → Null Handler
        - Null Handler → Feature Processor
        - Feature Processor → Validator
        - Validator → Orchestrator
        - Retry Decision → Anomaly Detector (feedback loop)
        """
        return workflow_description
