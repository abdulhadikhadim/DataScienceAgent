import pandas as pd
import numpy as np
from pathlib import Path
from langgraph_agents.orchestrator import DataPreprocessingOrchestrator


def create_sample_data():
    """
    Create sample datasets with various data quality issues for testing.
    """
    np.random.seed(42)
    
    data = {
        'id': range(1, 101),
        'age': np.random.randint(18, 80, 100),
        'income': np.random.normal(50000, 15000, 100),
        'score': np.random.uniform(0, 100, 100),
        'category': np.random.choice(['A', 'B', 'C', 'D', 'Rare1', 'Rare2'], 100, p=[0.3, 0.3, 0.2, 0.15, 0.03, 0.02]),
        'status': np.random.choice(['Active', 'Inactive'], 100)
    }
    
    df = pd.DataFrame(data)
    
    df.loc[5, 'age'] = 150
    df.loc[10, 'age'] = 5
    df.loc[15, 'income'] = 500000
    df.loc[20, 'income'] = -10000
    df.loc[25, 'score'] = 250
    
    null_indices = np.random.choice(df.index, 15, replace=False)
    for idx in null_indices[:5]:
        df.loc[idx, 'age'] = np.nan
    for idx in null_indices[5:10]:
        df.loc[idx, 'income'] = np.nan
    for idx in null_indices[10:]:
        df.loc[idx, 'category'] = np.nan
    
    duplicate_rows = df.iloc[[0, 1, 2]].copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    return df


def test_basic_workflow():
    """
    Test the basic preprocessing workflow with default settings.
    """
    print("=" * 80)
    print("TEST 1: Basic Workflow with Default Settings")
    print("=" * 80)
    
    df = create_sample_data()
    test_file = Path("./input_data/test_sample.csv")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(test_file, index=False)
    
    orchestrator = DataPreprocessingOrchestrator()
    
    result = orchestrator.preprocess_data(
        data_source=str(test_file),
        anomaly_strategy="cap",
        null_strategy="smart",
        max_iterations=3
    )
    
    print(f"\nWorkflow Status: {result['workflow_status']}")
    print(f"Validation Passed: {result['success']}")
    print(f"Iterations Used: {result['iterations_used']}")
    
    print("\nPreprocessing Steps:")
    for i, step in enumerate(result['preprocessing_steps'], 1):
        print(f"  {i}. {step}")
    
    print(f"\nAnomalies Detected: {len(result['anomalies_detected'])}")
    for anomaly in result['anomalies_detected'][:3]:
        print(f"  - {anomaly['column']}: {anomaly['method']} ({anomaly['count']} instances)")
    
    print(f"\nNull Values Info: {len(result['null_values_info'])} columns")
    for col, info in result['null_values_info'].items():
        print(f"  - {col}: {info['count']} nulls ({info['percentage']:.2f}%)")
    
    if result['validation_errors']:
        print("\nValidation Errors:")
        for error in result['validation_errors']:
            print(f"  - {error}")
    
    print("\nFeedback Messages:")
    for msg in result['feedback_messages'][:5]:
        print(f"  [{msg['from_agent']} → {msg['to_agent']}]: {msg['message']}")
    
    if result['success']:
        orchestrator.save_processed_data("./data/processed_output.csv", format="csv")
        orchestrator.save_processed_data("./data/processed_output.parquet", format="parquet")
    
    return orchestrator


def test_different_strategies():
    """
    Test different anomaly and null handling strategies.
    """
    print("\n" + "=" * 80)
    print("TEST 2: Different Handling Strategies")
    print("=" * 80)
    
    df = create_sample_data()
    test_file = Path("./input_data/test_strategies.csv")
    df.to_csv(test_file, index=False)
    
    strategies = [
        ("cap", "smart"),
        ("flag", "median"),
        ("remove", "mean"),
        ("transform", "mode")
    ]
    
    for anomaly_strat, null_strat in strategies:
        print(f"\n--- Testing: Anomaly={anomaly_strat}, Null={null_strat} ---")
        
        orchestrator = DataPreprocessingOrchestrator()
        result = orchestrator.preprocess_data(
            data_source=str(test_file),
            anomaly_strategy=anomaly_strat,
            null_strategy=null_strat,
            max_iterations=2
        )
        
        print(f"Status: {result['workflow_status']}, Success: {result['success']}")
        
        if result['processed_data'] is not None:
            print(f"Final Shape: {result['processed_data'].shape}")


def test_feedback_loop():
    """
    Test the feedback loop and retry mechanism.
    """
    print("\n" + "=" * 80)
    print("TEST 3: Feedback Loop and Retry Mechanism")
    print("=" * 80)
    
    df = pd.DataFrame({
        'col1': [1, 2, np.nan, np.nan, np.nan, 6, 7, 8],
        'col2': ['a', 'b', 'c', None, None, None, None, None],
        'col3': [100, 200, 300, 400, 500, 10000, 20000, 30000]
    })
    
    test_file = Path("./input_data/test_feedback.csv")
    df.to_csv(test_file, index=False)
    
    orchestrator = DataPreprocessingOrchestrator()
    result = orchestrator.preprocess_data(
        data_source=str(test_file),
        anomaly_strategy="cap",
        null_strategy="smart",
        max_iterations=3
    )
    
    print(f"\nIterations Used: {result['iterations_used']}")
    print(f"Final Status: {result['workflow_status']}")
    
    print("\nFeedback Communication Log:")
    for i, msg in enumerate(result['feedback_messages'], 1):
        print(f"\n{i}. {msg['from_agent']} → {msg['to_agent']}")
        print(f"   Message: {msg['message']}")
        if 'anomaly_summary' in msg:
            print(f"   Details: {msg['anomaly_summary']}")
        if 'null_summary' in msg:
            print(f"   Details: {msg['null_summary']}")
    
    summary = orchestrator.get_workflow_summary()
    print("\nWorkflow Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


def test_visualization():
    """
    Test workflow visualization.
    """
    print("\n" + "=" * 80)
    print("TEST 4: Workflow Visualization")
    print("=" * 80)
    
    orchestrator = DataPreprocessingOrchestrator()
    print(orchestrator.visualize_workflow())


def test_edge_cases():
    """
    Test edge cases and error handling.
    """
    print("\n" + "=" * 80)
    print("TEST 5: Edge Cases and Error Handling")
    print("=" * 80)
    
    print("\n--- Test 5a: Non-existent file ---")
    orchestrator = DataPreprocessingOrchestrator()
    result = orchestrator.preprocess_data(
        data_source="./nonexistent_file.csv"
    )
    print(f"Status: {result['workflow_status']}")
    print(f"Errors: {result['validation_errors']}")
    
    print("\n--- Test 5b: Empty dataframe ---")
    empty_df = pd.DataFrame()
    test_file = Path("./input_data/test_empty.csv")
    empty_df.to_csv(test_file, index=False)
    
    result = orchestrator.preprocess_data(
        data_source=str(test_file)
    )
    print(f"Status: {result['workflow_status']}")
    print(f"Errors: {result['validation_errors']}")
    
    print("\n--- Test 5c: All null columns ---")
    null_df = pd.DataFrame({
        'col1': [np.nan] * 10,
        'col2': [np.nan] * 10,
        'col3': [np.nan] * 10
    })
    test_file = Path("./input_data/test_all_null.csv")
    null_df.to_csv(test_file, index=False)
    
    result = orchestrator.preprocess_data(
        data_source=str(test_file),
        null_strategy="drop_columns"
    )
    print(f"Status: {result['workflow_status']}")
    print(f"Final shape: {result['processed_data'].shape if result['processed_data'] is not None else 'None'}")


def run_all_tests():
    """
    Run all test cases.
    """
    print("\n" + "=" * 80)
    print("LANGGRAPH DATA PREPROCESSING AGENT - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    test_basic_workflow()
    test_different_strategies()
    test_feedback_loop()
    test_visualization()
    test_edge_cases()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
