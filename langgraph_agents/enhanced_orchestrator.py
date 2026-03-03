from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime
from enhanced_workflow import create_enhanced_preprocessing_workflow
from enhanced_state import EnhancedPreprocessingState
from core.parallel_executor import ParallelExecutor, DataFramePartitioner, ChunkProcessor, PerformanceMonitor


class EnhancedDataPreprocessingOrchestrator:
    """
    Enhanced orchestrator with full data quality features, parallelism, and OOP design.
    
    Features:
    - Schema validation with Pydantic
    - Data type casting and format normalization
    - Encoding standardization
    - Referential integrity checks
    - Data quality rules engine
    - Parallel processing support
    - Chunk processing for large datasets
    - Performance monitoring
    - Comprehensive error handling
    """
    
    def __init__(self, 
                 enable_parallel: bool = True,
                 max_workers: Optional[int] = None,
                 chunk_size: int = 10000):
        self.workflow = create_enhanced_preprocessing_workflow()
        self.last_state = None
        self.enable_parallel = enable_parallel
        self.parallel_executor = ParallelExecutor(max_workers=max_workers) if enable_parallel else None
        self.chunk_processor = ChunkProcessor(chunk_size=chunk_size)
        self.performance_monitor = PerformanceMonitor()
    
    def preprocess_data(
        self,
        data_source: str,
        schema_config: Optional[Dict[str, Any]] = None,
        quality_rules: Optional[List[Dict[str, Any]]] = None,
        anomaly_strategy: str = "cap",
        null_strategy: str = "smart",
        max_iterations: int = 3,
        enable_chunking: bool = False,
        partition_strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive preprocessing workflow.
        
        Args:
            data_source: Path to data file
            schema_config: Schema definition for validation
            quality_rules: List of data quality rules
            anomaly_strategy: Anomaly handling strategy
            null_strategy: Null handling strategy
            max_iterations: Maximum retry iterations
            enable_chunking: Process large files in chunks
            partition_strategy: Data partitioning strategy for parallel processing
        
        Returns:
            Comprehensive preprocessing results
        """
        start_time = datetime.now()
        
        initial_state: EnhancedPreprocessingState = {
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
            
            "metadata": {
                "schema_config": schema_config,
                "quality_rules": quality_rules or []
            },
            "feedback_messages": [],
            
            "iteration_count": 0,
            "max_iterations": max_iterations,
            
            "schema_validation_result": None,
            "type_casting_changes": [],
            "format_normalizations": [],
            "encoding_fixes": [],
            
            "referential_integrity_issues": [],
            "quality_rule_violations": [],
            "quarantine_records": None,
            
            "duplicates_removed": 0,
            
            "parallel_execution_enabled": self.enable_parallel,
            "chunk_processing_enabled": enable_chunking,
            "partition_strategy": partition_strategy,
            
            "performance_metrics": {}
        }
        
        final_state = self.workflow.invoke(initial_state)
        
        self.last_state = final_state
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        performance_stats = self.performance_monitor.get_all_stats()
        
        return {
            "success": final_state.get("validation_passed", False),
            "workflow_status": final_state.get("workflow_status"),
            "processed_data": final_state.get("processed_data"),
            
            "preprocessing_steps": final_state.get("preprocessing_steps"),
            "anomalies_detected": final_state.get("anomalies_detected"),
            "null_values_info": final_state.get("null_values_info"),
            "validation_errors": final_state.get("validation_errors"),
            
            "schema_validation": final_state.get("schema_validation_result"),
            "type_casting_changes": final_state.get("type_casting_changes"),
            "format_normalizations": final_state.get("format_normalizations"),
            "encoding_fixes": final_state.get("encoding_fixes"),
            
            "referential_integrity_issues": final_state.get("referential_integrity_issues"),
            "quality_violations": final_state.get("quality_rule_violations"),
            "quarantine_records": final_state.get("quarantine_records"),
            
            "duplicates_removed": final_state.get("duplicates_removed", 0),
            
            "feedback_messages": final_state.get("feedback_messages"),
            "metadata": final_state.get("metadata"),
            "iterations_used": final_state.get("iteration_count", 0),
            
            "execution_time_seconds": execution_time,
            "performance_metrics": performance_stats
        }
    
    def preprocess_large_dataset(
        self,
        data_source: str,
        chunk_size: int = 10000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Preprocess large dataset using chunk processing.
        """
        def process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
            temp_state = {
                "processed_data": chunk,
                **kwargs
            }
            return temp_state["processed_data"]
        
        processed_df = self.chunk_processor.read_csv_in_chunks(
            data_source,
            process_chunk
        )
        
        return {
            "success": True,
            "processed_data": processed_df,
            "processing_method": "chunked"
        }
    
    def preprocess_partitioned_data(
        self,
        data_source: str,
        partition_key: Optional[str] = None,
        n_partitions: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Preprocess data using partitioning and parallel execution.
        """
        df = pd.read_csv(data_source) if data_source.endswith('.csv') else pd.read_parquet(data_source)
        
        if partition_key and partition_key in df.columns:
            partitions = DataFramePartitioner.partition_by_key(df, partition_key)
        else:
            partitions = DataFramePartitioner.partition_by_rows(df, n_partitions)
        
        from core.parallel_executor import ParallelTask
        
        def process_partition(partition_df: pd.DataFrame) -> pd.DataFrame:
            # Create initial state with the partition data
            initial_state = {
                "raw_data": partition_df,
                "processed_data": partition_df.copy(),
                "data_source": "partition",
                "data_format": "dataframe",
                "anomalies_detected": [],
                "null_values_info": {},
                "preprocessing_steps": [],
                "anomaly_handling_strategy": kwargs.get("anomaly_strategy", "cap"),
                "null_handling_strategy": kwargs.get("null_strategy", "smart"),
                "validation_passed": False,
                "validation_errors": [],
                "current_agent": "data_loader",
                "workflow_status": "initialized",
                "metadata": {},
                "feedback_messages": [],
                "iteration_count": 0,
                "max_iterations": kwargs.get("max_iterations", 3),
                "schema_validation_result": None,
                "type_casting_changes": [],
                "format_normalizations": [],
                "encoding_fixes": [],
                "referential_integrity_issues": [],
                "quality_rule_violations": [],
                "quarantine_records": None,
                "duplicates_removed": 0,
                "parallel_execution_enabled": False,
                "chunk_processing_enabled": False,
                "partition_strategy": None,
                "performance_metrics": {}
            }
            
            try:
                final_state = self.workflow.invoke(initial_state)
                return final_state.get("processed_data", partition_df)
            except Exception as e:
                print(f"Error processing partition: {e}")
                return partition_df
        
        tasks = [
            ParallelTask(
                name=f"partition_{i}",
                function=process_partition,
                args=(partition,)
            )
            for i, partition in enumerate(partitions if isinstance(partitions, list) else partitions.values())
        ]
        
        result = self.parallel_executor.execute_parallel(tasks)
        
        if result["error_count"] > 0:
            return {
                "success": False,
                "errors": result["errors"]
            }
        
        processed_partitions = [r for r in result["results"].values() if r is not None]
        
        if not processed_partitions:
            return {
                "success": False,
                "error": "All partitions failed to process"
            }
        
        final_df = pd.concat(processed_partitions, ignore_index=True)
        
        return {
            "success": True,
            "processed_data": final_df,
            "processing_method": "partitioned_parallel",
            "partitions_processed": len(processed_partitions)
        }
    
    def get_processed_dataframe(self) -> Optional[pd.DataFrame]:
        """Get processed dataframe from last run"""
        if self.last_state:
            return self.last_state.get("processed_data")
        return None
    
    def get_quarantine_records(self) -> Optional[pd.DataFrame]:
        """Get quarantined records from last run"""
        if self.last_state:
            return self.last_state.get("quarantine_records")
        return None
    
    def save_processed_data(self, output_path: str, format: str = "csv") -> bool:
        """Save processed data to file"""
        df = self.get_processed_dataframe()
        
        if df is None:
            print("No processed data available")
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
            print(f"Error saving: {e}")
            return False
    
    def save_quarantine_records(self, output_path: str, format: str = "csv") -> bool:
        """Save quarantined records to file"""
        df = self.get_quarantine_records()
        
        if df is None or len(df) == 0:
            print("No quarantine records to save")
            return False
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "csv":
                df.to_csv(output_file, index=False)
            elif format == "parquet":
                df.to_parquet(output_file)
            
            print(f"Quarantine records saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error saving quarantine: {e}")
            return False
    
    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        if not self.last_state:
            return {"error": "No workflow executed"}
        
        schema_result = self.last_state.get("schema_validation_result")
        schema_valid = schema_result.get("valid", None) if schema_result else None
        
        return {
            "workflow_status": self.last_state.get("workflow_status"),
            "validation_passed": self.last_state.get("validation_passed"),
            
            "data_quality": {
                "schema_valid": schema_valid,
                "anomalies_count": len(self.last_state.get("anomalies_detected", [])),
                "null_columns": len(self.last_state.get("null_values_info", {})),
                "quality_violations": len(self.last_state.get("quality_rule_violations", [])),
                "duplicates_removed": self.last_state.get("duplicates_removed", 0),
                "quarantine_count": len(self.last_state.get("quarantine_records", [])) if self.last_state.get("quarantine_records") is not None else 0
            },
            
            "transformations": {
                "type_changes": len(self.last_state.get("type_casting_changes", [])),
                "format_normalizations": len(self.last_state.get("format_normalizations", [])),
                "encoding_fixes": len(self.last_state.get("encoding_fixes", []))
            },
            
            "processing": {
                "steps_count": len(self.last_state.get("preprocessing_steps", [])),
                "iterations_used": self.last_state.get("iteration_count", 0),
                "validation_errors": len(self.last_state.get("validation_errors", [])),
                "feedback_messages": len(self.last_state.get("feedback_messages", []))
            },
            
            "final_data": {
                "shape": self.last_state.get("processed_data").shape if self.last_state.get("processed_data") is not None else None,
                "columns": list(self.last_state.get("processed_data").columns) if self.last_state.get("processed_data") is not None else []
            }
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance metrics report"""
        return self.performance_monitor.get_all_stats()
    
    def visualize_enhanced_workflow(self) -> str:
        """Generate enhanced workflow visualization"""
        return """
        Enhanced LangGraph Data Preprocessing Workflow
        ==============================================
        
        [START]
           ↓
        [Load Data]
           ↓
        [Validate Schema] ──→ [Enforce Schema] (if validation fails)
           ↓                         ↓
        [Cast Data Types] ←──────────┘
           ↓
        [Normalize Formats] (dates, strings, phone, email)
           ↓
        [Standardize Encoding] (UTF-8)
           ↓
        [Check Referential Integrity] (PK/FK validation)
           ↓
        [Detect Anomalies] (IQR, Z-score, rare categories)
           ↓
           ├─→ [Handle Anomalies] (if detected)
           │      ↓
           └─→ [Detect Null Values]
                  ↓
                  ├─→ [Handle Nulls] (if detected)
                  │      ↓
                  └─→ [Apply Quality Rules] (range checks, patterns)
                         ↓
                      [Deduplicate] (PK or hash-based)
                         ↓
                      [Process Features] (encoding, scaling)
                         ↓
                      [Validate Data]
                         ↓
                         ├─→ [END] (if passed)
                         │
                         └─→ [Retry Decision] (if failed)
                                ↓
                                └─→ [Detect Anomalies] (feedback loop)
        
        Parallel Processing Support:
        - Independent column operations run in parallel
        - Data partitioning for large datasets
        - Chunk processing for memory efficiency
        
        OOP Design Patterns:
        - Strategy Pattern: Processing strategies
        - Factory Pattern: Agent creation
        - Singleton Pattern: Strategy registry
        - Template Method: Base agent execution
        - Chain of Responsibility: Sequential agents
        """
