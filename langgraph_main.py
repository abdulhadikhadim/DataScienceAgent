#!/usr/bin/env python3
"""
LangGraph Data Preprocessing Agent - Main Entry Point

This script provides a command-line interface for the LangGraph-based
data preprocessing system.
"""

import argparse
import sys
from pathlib import Path
from langgraph_agents.orchestrator import DataPreprocessingOrchestrator
from langgraph_agents.config import LangGraphConfig


def main():
    """
    Main entry point for the LangGraph preprocessing system.
    """
    parser = argparse.ArgumentParser(
        description="LangGraph Data Preprocessing Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python langgraph_main.py --input data.csv --output processed.csv
  
  # Custom strategies
  python langgraph_main.py --input data.csv --output processed.csv \\
      --anomaly-strategy flag --null-strategy median
  
  # Multiple iterations
  python langgraph_main.py --input data.csv --output processed.csv \\
      --max-iterations 5
  
  # Different output format
  python langgraph_main.py --input data.csv --output processed.parquet \\
      --format parquet
  
  # Verbose output
  python langgraph_main.py --input data.csv --output processed.csv --verbose
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input data file path (CSV, Excel, JSON, or Parquet)"
    )
    
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path for processed data"
    )
    
    parser.add_argument(
        "--anomaly-strategy",
        choices=LangGraphConfig.ANOMALY_STRATEGIES,
        default=LangGraphConfig.DEFAULT_ANOMALY_STRATEGY,
        help=f"Strategy for handling anomalies (default: {LangGraphConfig.DEFAULT_ANOMALY_STRATEGY})"
    )
    
    parser.add_argument(
        "--null-strategy",
        choices=LangGraphConfig.NULL_STRATEGIES,
        default=LangGraphConfig.DEFAULT_NULL_STRATEGY,
        help=f"Strategy for handling null values (default: {LangGraphConfig.DEFAULT_NULL_STRATEGY})"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=LangGraphConfig.DEFAULT_MAX_ITERATIONS,
        help=f"Maximum retry iterations (default: {LangGraphConfig.DEFAULT_MAX_ITERATIONS})"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "excel", "parquet", "json"],
        default="csv",
        help="Output file format (default: csv)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--show-workflow",
        action="store_true",
        help="Display workflow visualization and exit"
    )
    
    args = parser.parse_args()
    
    if args.show_workflow:
        orchestrator = DataPreprocessingOrchestrator()
        print(orchestrator.visualize_workflow())
        return 0
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    if not LangGraphConfig.validate_file_format(args.input):
        print(f"Error: Unsupported file format. Supported formats: {LangGraphConfig.SUPPORTED_FORMATS}", 
              file=sys.stderr)
        return 1
    
    print("=" * 80)
    print("LangGraph Data Preprocessing Agent")
    print("=" * 80)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Anomaly Strategy: {args.anomaly_strategy}")
    print(f"Null Strategy: {args.null_strategy}")
    print(f"Max Iterations: {args.max_iterations}")
    print("=" * 80)
    
    orchestrator = DataPreprocessingOrchestrator()
    
    print("\n🚀 Starting preprocessing workflow...\n")
    
    result = orchestrator.preprocess_data(
        data_source=args.input,
        anomaly_strategy=args.anomaly_strategy,
        null_strategy=args.null_strategy,
        max_iterations=args.max_iterations
    )
    
    if args.verbose:
        print("\n" + "=" * 80)
        print("PREPROCESSING STEPS")
        print("=" * 80)
        for i, step in enumerate(result['preprocessing_steps'], 1):
            print(f"{i}. {step}")
        
        if result['anomalies_detected']:
            print("\n" + "=" * 80)
            print("ANOMALIES DETECTED")
            print("=" * 80)
            for anomaly in result['anomalies_detected']:
                print(f"\nColumn: {anomaly['column']}")
                print(f"  Method: {anomaly['method']}")
                print(f"  Count: {anomaly['count']}")
                if 'lower_bound' in anomaly and 'upper_bound' in anomaly:
                    print(f"  Bounds: [{anomaly['lower_bound']:.2f}, {anomaly['upper_bound']:.2f}]")
        
        if result['null_values_info']:
            print("\n" + "=" * 80)
            print("NULL VALUES")
            print("=" * 80)
            for col, info in result['null_values_info'].items():
                print(f"{col}: {info['count']} nulls ({info['percentage']:.2f}%)")
        
        print("\n" + "=" * 80)
        print("AGENT FEEDBACK")
        print("=" * 80)
        for msg in result['feedback_messages']:
            print(f"\n[{msg['from_agent']} → {msg['to_agent']}]")
            print(f"  {msg['message']}")
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Status: {result['workflow_status']}")
    print(f"Validation Passed: {'✓ Yes' if result['success'] else '✗ No'}")
    print(f"Iterations Used: {result['iterations_used']}")
    
    if result['processed_data'] is not None:
        print(f"Final Shape: {result['processed_data'].shape}")
    
    if result['validation_errors']:
        print("\n⚠️  Validation Errors:")
        for error in result['validation_errors']:
            print(f"  • {error}")
    
    if result['success']:
        print("\n💾 Saving processed data...")
        success = orchestrator.save_processed_data(args.output, format=args.format)
        
        if success:
            print(f"✓ Successfully saved to: {args.output}")
            print("\n" + "=" * 80)
            print("PREPROCESSING COMPLETED SUCCESSFULLY")
            print("=" * 80)
            return 0
        else:
            print(f"✗ Failed to save output file", file=sys.stderr)
            return 1
    else:
        print("\n" + "=" * 80)
        print("PREPROCESSING FAILED")
        print("=" * 80)
        print("The data could not be preprocessed successfully.")
        print("Please review the validation errors above and adjust your data or strategies.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
