import pandas as pd
import numpy as np
from pathlib import Path
from langgraph_agents.enhanced_orchestrator import EnhancedDataPreprocessingOrchestrator
from langgraph_agents.nodes.schema_validator_node import DataSchema, ColumnSchema


def create_comprehensive_test_data():
    """Create comprehensive test dataset with all types of issues"""
    np.random.seed(42)
    
    data = {
        'id': range(1, 201),
        'customer_name': ['John Doe', 'jane smith', 'BOB WILSON', 'Alice Brown'] * 50,
        'email': ['john@example.com', 'JANE@TEST.COM', 'bob@company.org', 'alice@mail.net'] * 50,
        'phone': ['555-1234', '(555) 5678', '555 9012', '5553456'] * 50,
        'age': np.random.randint(18, 80, 200),
        'income': np.random.normal(50000, 15000, 200),
        'score': np.random.uniform(0, 100, 200),
        'category': np.random.choice(['A', 'B', 'C', 'D', 'Rare1'], 200, p=[0.3, 0.3, 0.2, 0.15, 0.05]),
        'status': np.random.choice(['Active', 'Inactive'], 200),
        'join_date': pd.date_range('2020-01-01', periods=200, freq='D').strftime('%Y-%m-%d').tolist(),
        'amount': np.random.uniform(10, 1000, 200)
    }
    
    df = pd.DataFrame(data)
    
    # Add anomalies
    df.loc[5, 'age'] = 150
    df.loc[10, 'age'] = 5
    df.loc[15, 'income'] = 500000
    df.loc[20, 'income'] = -10000
    df.loc[25, 'score'] = 250
    
    # Add null values
    null_indices = np.random.choice(df.index, 30, replace=False)
    for idx in null_indices[:10]:
        df.loc[idx, 'age'] = np.nan
    for idx in null_indices[10:20]:
        df.loc[idx, 'income'] = np.nan
    for idx in null_indices[20:]:
        df.loc[idx, 'category'] = np.nan
    
    # Add duplicates
    duplicate_rows = df.iloc[[0, 1, 2]].copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    # Add wrong data types (as strings)
    df.loc[30:35, 'age'] = df.loc[30:35, 'age'].astype(str)
    
    # Add inconsistent date formats
    df.loc[40:45, 'join_date'] = pd.date_range('2020-02-01', periods=6).strftime('%m/%d/%Y').tolist()
    
    # Add encoding issues (simulated)
    df.loc[50, 'customer_name'] = 'José García'
    
    return df


def test_enhanced_basic_workflow():
    """Test enhanced workflow with all features"""
    print("=" * 80)
    print("TEST 1: Enhanced Workflow - All Features")
    print("=" * 80)
    
    df = create_comprehensive_test_data()
    test_file = Path("./input_data/enhanced_test.csv")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(test_file, index=False)
    
    # Define schema
    schema_config = {
        "name": "CustomerData",
        "version": "1.0",
        "columns": [
            {"name": "id", "dtype": "int", "nullable": False},
            {"name": "customer_name", "dtype": "string", "nullable": False},
            {"name": "email", "dtype": "string", "nullable": False, 
             "regex_pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
            {"name": "phone", "dtype": "string", "nullable": True},
            {"name": "age", "dtype": "int", "nullable": True, "min_value": 18, "max_value": 100},
            {"name": "income", "dtype": "float", "nullable": True, "min_value": 0},
            {"name": "score", "dtype": "float", "nullable": True, "min_value": 0, "max_value": 100},
            {"name": "category", "dtype": "string", "nullable": True, 
             "allowed_values": ["A", "B", "C", "D"]},
            {"name": "status", "dtype": "string", "nullable": False, 
             "allowed_values": ["Active", "Inactive"]},
            {"name": "join_date", "dtype": "datetime", "nullable": False},
            {"name": "amount", "dtype": "float", "nullable": False, "min_value": 0}
        ],
        "primary_key": ["id"]
    }
    
    # Define quality rules
    quality_rules = [
        {"type": "range", "column": "age", "min": 18, "max": 100, "action": "FLAG"},
        {"type": "range", "column": "income", "min": 0, "max": 200000, "action": "FLAG"},
        {"type": "not_null", "column": "id", "action": "REJECT"},
        {"type": "unique", "column": "id", "action": "FLAG"}
    ]
    
    orchestrator = EnhancedDataPreprocessingOrchestrator(
        enable_parallel=True,
        max_workers=4
    )
    
    result = orchestrator.preprocess_data(
        data_source=str(test_file),
        schema_config=schema_config,
        quality_rules=quality_rules,
        anomaly_strategy="cap",
        null_strategy="smart",
        max_iterations=3
    )
    
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Status: {result['workflow_status']}")
    print(f"Success: {result['success']}")
    print(f"Execution Time: {result['execution_time_seconds']:.2f}s")
    
    print(f"\n{'='*80}")
    print("DATA QUALITY SUMMARY")
    print(f"{'='*80}")
    summary = orchestrator.get_comprehensive_summary()
    
    print(f"\nSchema Validation: {summary['data_quality']['schema_valid']}")
    print(f"Anomalies Detected: {summary['data_quality']['anomalies_count']}")
    print(f"Null Columns: {summary['data_quality']['null_columns']}")
    print(f"Quality Violations: {summary['data_quality']['quality_violations']}")
    print(f"Duplicates Removed: {summary['data_quality']['duplicates_removed']}")
    print(f"Quarantine Count: {summary['data_quality']['quarantine_count']}")
    
    print(f"\n{'='*80}")
    print("TRANSFORMATIONS")
    print(f"{'='*80}")
    print(f"Type Changes: {summary['transformations']['type_changes']}")
    print(f"Format Normalizations: {summary['transformations']['format_normalizations']}")
    print(f"Encoding Fixes: {summary['transformations']['encoding_fixes']}")
    
    print(f"\n{'='*80}")
    print("PREPROCESSING STEPS")
    print(f"{'='*80}")
    for i, step in enumerate(result['preprocessing_steps'][:15], 1):
        print(f"{i}. {step}")
    
    if result['success']:
        orchestrator.save_processed_data("./data/enhanced_output.csv")
        orchestrator.save_processed_data("./data/enhanced_output.parquet", format="parquet")
        
        if orchestrator.get_quarantine_records() is not None:
            orchestrator.save_quarantine_records("./data/quarantine.csv")
    
    return orchestrator


def test_parallel_processing():
    """Test parallel processing capabilities"""
    print("\n" + "=" * 80)
    print("TEST 2: Parallel Processing")
    print("=" * 80)
    
    df = create_comprehensive_test_data()
    test_file = Path("./input_data/parallel_test.csv")
    df.to_csv(test_file, index=False)
    
    orchestrator = EnhancedDataPreprocessingOrchestrator(
        enable_parallel=True,
        max_workers=4
    )
    
    result = orchestrator.preprocess_partitioned_data(
        data_source=str(test_file),
        n_partitions=4,
        anomaly_strategy="flag",
        null_strategy="median"
    )
    
    print(f"\nProcessing Method: {result.get('processing_method')}")
    print(f"Partitions Processed: {result.get('partitions_processed')}")
    print(f"Success: {result['success']}")
    
    if result['success']:
        print(f"Final Shape: {result['processed_data'].shape}")


def test_chunk_processing():
    """Test chunk processing for large datasets"""
    print("\n" + "=" * 80)
    print("TEST 3: Chunk Processing")
    print("=" * 80)
    
    # Create larger dataset
    large_df = pd.concat([create_comprehensive_test_data() for _ in range(5)], ignore_index=True)
    test_file = Path("./input_data/large_test.csv")
    large_df.to_csv(test_file, index=False)
    
    print(f"Dataset size: {large_df.shape}")
    
    orchestrator = EnhancedDataPreprocessingOrchestrator(chunk_size=500)
    
    result = orchestrator.preprocess_large_dataset(
        data_source=str(test_file),
        chunk_size=500
    )
    
    print(f"Processing Method: {result.get('processing_method')}")
    print(f"Success: {result['success']}")


def test_schema_validation():
    """Test schema validation and enforcement"""
    print("\n" + "=" * 80)
    print("TEST 4: Schema Validation & Enforcement")
    print("=" * 80)
    
    df = create_comprehensive_test_data()
    test_file = Path("./input_data/schema_test.csv")
    df.to_csv(test_file, index=False)
    
    schema_config = {
        "name": "StrictSchema",
        "version": "2.0",
        "columns": [
            {"name": "id", "dtype": "int", "nullable": False},
            {"name": "age", "dtype": "int", "nullable": False, "min_value": 0, "max_value": 120},
            {"name": "income", "dtype": "float", "nullable": False, "min_value": 0},
        ],
        "primary_key": ["id"]
    }
    
    orchestrator = EnhancedDataPreprocessingOrchestrator()
    
    result = orchestrator.preprocess_data(
        data_source=str(test_file),
        schema_config=schema_config
    )
    
    if result['schema_validation']:
        print(f"\nSchema Valid: {result['schema_validation']['valid']}")
        print(f"Errors: {len(result['schema_validation'].get('errors', []))}")
        print(f"Warnings: {len(result['schema_validation'].get('warnings', []))}")


def test_data_quality_rules():
    """Test data quality rules engine"""
    print("\n" + "=" * 80)
    print("TEST 5: Data Quality Rules Engine")
    print("=" * 80)
    
    df = create_comprehensive_test_data()
    test_file = Path("./input_data/quality_test.csv")
    df.to_csv(test_file, index=False)
    
    quality_rules = [
        {"type": "range", "column": "age", "min": 18, "max": 65, "action": "QUARANTINE"},
        {"type": "range", "column": "score", "min": 0, "max": 100, "action": "FIX"},
        {"type": "pattern", "column": "email", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$", "action": "FLAG"},
        {"type": "not_null", "column": "customer_name", "action": "REJECT"}
    ]
    
    orchestrator = EnhancedDataPreprocessingOrchestrator()
    
    result = orchestrator.preprocess_data(
        data_source=str(test_file),
        quality_rules=quality_rules
    )
    
    print(f"\nQuality Violations: {len(result['quality_violations'])}")
    for violation in result['quality_violations'][:5]:
        print(f"  - {violation['rule']}: {violation['count']} violations ({violation['action']})")
    
    quarantine = orchestrator.get_quarantine_records()
    if quarantine is not None:
        print(f"\nQuarantined Records: {len(quarantine)}")


def test_performance_monitoring():
    """Test performance monitoring"""
    print("\n" + "=" * 80)
    print("TEST 6: Performance Monitoring")
    print("=" * 80)
    
    df = create_comprehensive_test_data()
    test_file = Path("./input_data/perf_test.csv")
    df.to_csv(test_file, index=False)
    
    orchestrator = EnhancedDataPreprocessingOrchestrator()
    
    result = orchestrator.preprocess_data(data_source=str(test_file))
    
    perf_report = orchestrator.get_performance_report()
    
    print(f"\nExecution Time: {result['execution_time_seconds']:.2f}s")
    print(f"Performance Metrics: {len(perf_report)} tracked")


def test_workflow_visualization():
    """Test workflow visualization"""
    print("\n" + "=" * 80)
    print("TEST 7: Enhanced Workflow Visualization")
    print("=" * 80)
    
    orchestrator = EnhancedDataPreprocessingOrchestrator()
    print(orchestrator.visualize_enhanced_workflow())


def run_all_enhanced_tests():
    """Run all enhanced tests"""
    print("\n" + "=" * 80)
    print("ENHANCED LANGGRAPH PREPROCESSING - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    test_enhanced_basic_workflow()
    test_parallel_processing()
    test_chunk_processing()
    test_schema_validation()
    test_data_quality_rules()
    test_performance_monitoring()
    test_workflow_visualization()
    
    print("\n" + "=" * 80)
    print("ALL ENHANCED TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_all_enhanced_tests()
