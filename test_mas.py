import asyncio
import pandas as pd
from pathlib import Path

from main_orchestrator import DataScienceMAS
from agents.detection_agent import DetectionAgent
from agents.loading_agent import LoadingAgent
from agents.processing_agent import ProcessingAgent
from utils.file_utils import load_data_with_fallback


def test_detection_agent():
    print("=== Testing Detection Agent ===")
    detector = DetectionAgent()
    state = detector.scan_directories(["./input_data", "./data"])
    
    print(f"Status: {state.processing_status}")
    print(f"Found {len(state.detected_files)} files")
    
    for file_info in state.detected_files:
        print(f"  - {file_info['name']} ({file_info['type']}) - {file_info['size_mb']} MB")
    
    summary = detector.get_file_summary()
    print(f"Summary: {summary}")
    return detector


def test_loading_agent(detector):
    print("\n=== Testing Loading Agent ===")
    loader = LoadingAgent()
    
    # Load the detected files
    if detector.state.detected_files:
        for file_info in detector.state.detected_files:
            print(f"Loading {file_info['name']}...")
            loader.load_file(file_info['path'], file_info['type'])
            
            if loader.state.processing_status == "completed":
                df_name = file_info['path'].stem
                df = loader.get_dataframe(df_name)
                if df is not None:
                    print(f"  Loaded dataframe '{df_name}' with shape {df.shape}")
                    print(f"  Columns: {list(df.columns)}")
                    print(f"  Sample data:\n{df.head(2)}")
            else:
                print(f"  Error loading {file_info['name']}: {loader.state.last_error}")
    
    return loader

def test_processing_agent(loader):
    print("\n=== Testing Processing Agent ===")
    processor = ProcessingAgent()
    
    # Get loaded dataframes
    dataframes = loader.state.loaded_dataframes
    print(f"Processing {len(dataframes)} dataframes")
    
    # Save the dataframes
    processor.save_multiple_dataframes(dataframes, "test_output")
    
    print(f"Saved files: {processor.get_processed_files()}")
    return processor

def test_header_detection():
    print("\n=== Testing Header Detection ===")
    # Test with our sample CSV that has headers in the third row
    sample_file = Path("input_data/sample_data.csv")
    
    if sample_file.exists():
        print(f"Testing header detection on {sample_file}")
        df = load_data_with_fallback(sample_file, "csv")
        print(f"Loaded dataframe with shape: {df.shape}")
        print(f"Columns detected: {list(df.columns)}")
        print(f"Sample data:\n{df.head()}")
    else:
        print(f"Sample file {sample_file} not found")


def test_full_mas_pipeline():
    print("\n=== Testing Full MAS Pipeline ===")
    mas = DataScienceMAS()
    
    # Run the full pipeline
    results = asyncio.run(mas.run_analysis_pipeline(["./input_data"]))
    
    if results:
        print("MAS pipeline completed successfully!")
        
        # Analyze loaded dataframes
        dataframes = mas.get_available_dataframes()
        for name, df in dataframes.items():
            print(f"\nAnalyzing dataframe '{name}':")
            analysis = mas.analyze_dataframe(name)
            for key, value in analysis.items():
                if key != 'basic_stats' or value != 'No numeric columns for stats':
                    print(f"  {key}: {value}")
    else:
        print("MAS pipeline failed")

if __name__ == "__main__":
    # Run all tests
    detector = test_detection_agent()
    loader = test_loading_agent(detector)
    processor = test_processing_agent(loader)
    test_header_detection()
    test_full_mas_pipeline()