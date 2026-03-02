from pathlib import Path
import pandas as pd
import numpy as np
from langgraph_agents.orchestrator import DataPreprocessingOrchestrator


def example_1_basic_usage():
    """
    Example 1: Basic usage with a CSV file
    """
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80)
    
    orchestrator = DataPreprocessingOrchestrator()
    
    result = orchestrator.preprocess_data(
        data_source="./input_data/sample_data.csv",
        anomaly_strategy="cap",
        null_strategy="smart",
        max_iterations=3
    )
    
    if result['success']:
        print("✓ Preprocessing completed successfully!")
        print(f"  Final shape: {result['processed_data'].shape}")
        
        orchestrator.save_processed_data("./data/output.csv", format="csv")
        print("  Saved to: ./data/output.csv")
    else:
        print("✗ Preprocessing failed")
        print(f"  Errors: {result['validation_errors']}")


def example_2_custom_strategies():
    """
    Example 2: Using custom preprocessing strategies
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Custom Strategies")
    print("=" * 80)
    
    orchestrator = DataPreprocessingOrchestrator()
    
    result = orchestrator.preprocess_data(
        data_source="./input_data/sample_data.csv",
        anomaly_strategy="flag",
        null_strategy="median",
        max_iterations=5
    )
    
    print(f"Preprocessing steps taken:")
    for step in result['preprocessing_steps']:
        print(f"  • {step}")


def example_3_analyzing_feedback():
    """
    Example 3: Analyzing agent feedback and communication
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Agent Feedback Analysis")
    print("=" * 80)
    
    orchestrator = DataPreprocessingOrchestrator()
    
    result = orchestrator.preprocess_data(
        data_source="./input_data/sample_data.csv"
    )
    
    print("Agent Communication Flow:")
    for msg in result['feedback_messages']:
        print(f"\n  {msg['from_agent']} → {msg['to_agent']}")
        print(f"  Message: {msg['message']}")


def example_4_multiple_formats():
    """
    Example 4: Working with different file formats
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Multiple File Formats")
    print("=" * 80)
    
    formats = {
        "CSV": "./input_data/data.csv",
        "Excel": "./input_data/data.xlsx",
        "JSON": "./input_data/data.json",
        "Parquet": "./input_data/data.parquet"
    }
    
    orchestrator = DataPreprocessingOrchestrator()
    
    for format_name, file_path in formats.items():
        if Path(file_path).exists():
            print(f"\nProcessing {format_name} file...")
            result = orchestrator.preprocess_data(data_source=file_path)
            print(f"  Status: {result['workflow_status']}")


def example_5_workflow_summary():
    """
    Example 5: Getting detailed workflow summary
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Workflow Summary")
    print("=" * 80)
    
    orchestrator = DataPreprocessingOrchestrator()
    
    orchestrator.preprocess_data(
        data_source="./input_data/sample_data.csv"
    )
    
    summary = orchestrator.get_workflow_summary()
    
    print("\nWorkflow Execution Summary:")
    print(f"  Status: {summary['workflow_status']}")
    print(f"  Validation Passed: {summary['validation_passed']}")
    print(f"  Iterations Used: {summary['iterations_used']}")
    print(f"  Anomalies Found: {summary['anomalies_count']}")
    print(f"  Null Columns: {summary['null_columns_count']}")
    print(f"  Final Shape: {summary['final_shape']}")
    print(f"  Feedback Messages: {summary['feedback_messages_count']}")


def example_6_programmatic_data():
    """
    Example 6: Creating and preprocessing data programmatically
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Programmatic Data Creation")
    print("=" * 80)
    
    np.random.seed(42)
    df = pd.DataFrame({
        'feature1': np.random.normal(100, 15, 200),
        'feature2': np.random.exponential(50, 200),
        'feature3': np.random.choice(['Cat1', 'Cat2', 'Cat3'], 200),
        'target': np.random.randint(0, 2, 200)
    })
    
    df.loc[10:20, 'feature1'] = np.nan
    df.loc[5, 'feature2'] = 1000
    df.loc[15, 'feature2'] = -50
    
    temp_file = Path("./input_data/programmatic_data.csv")
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(temp_file, index=False)
    
    orchestrator = DataPreprocessingOrchestrator()
    result = orchestrator.preprocess_data(
        data_source=str(temp_file),
        anomaly_strategy="cap",
        null_strategy="smart"
    )
    
    print(f"Original shape: {df.shape}")
    print(f"Processed shape: {result['processed_data'].shape}")
    print(f"Success: {result['success']}")


def example_7_visualize_workflow():
    """
    Example 7: Visualizing the workflow graph
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Workflow Visualization")
    print("=" * 80)
    
    orchestrator = DataPreprocessingOrchestrator()
    print(orchestrator.visualize_workflow())


def main():
    """
    Run all examples
    """
    print("\n" + "=" * 80)
    print("LANGGRAPH DATA PREPROCESSING - USAGE EXAMPLES")
    print("=" * 80)
    
    example_1_basic_usage()
    example_2_custom_strategies()
    example_3_analyzing_feedback()
    example_4_multiple_formats()
    example_5_workflow_summary()
    example_6_programmatic_data()
    example_7_visualize_workflow()
    
    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
