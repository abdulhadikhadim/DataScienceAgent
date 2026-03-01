import asyncio
from pathlib import Path
import pandas as pd

from agents.detection_agent import DetectionAgent
from agents.loading_agent import LoadingAgent
from agents.processing_agent import ProcessingAgent
from agents.communication import AgentCollaborationManager, AgentType
from config.settings import Config


class DataScienceMAS:
    """
    Main orchestrator for the Multi-Agent System that acts as a data scientist.
    """
    
    def __init__(self):
        # Initialize agents
        self.detection_agent = DetectionAgent()
        self.loading_agent = LoadingAgent()
        self.processing_agent = ProcessingAgent()
        
        # Initialize collaboration manager
        self.collaboration_manager = AgentCollaborationManager()
        self.collaboration_manager.register_agents(
            self.detection_agent,
            self.loading_agent
        )
    
    async def run_analysis_pipeline(self, data_dirs: list = None):
        """
        Run the complete analysis pipeline: detect -> load -> process
        """
        print("Starting Data Science MAS Pipeline...")
        
        # Step 1: Coordinate data loading (detection + loading)
        detection_result, loading_result = await self.collaboration_manager.coordinate_data_loading(data_dirs)
        
        if detection_result and loading_result:
            print(f"Detected {len(detection_result['result'].get('detected_files', []))} files")
            print(f"Successfully loaded {len(loading_result['result'].get('loaded_dataframes', {}))} dataframes")
            
            # Step 2: Process and save loaded data
            loaded_dfs = self.loading_agent.state.loaded_dataframes
            if loaded_dfs:
                print(f"Processing and saving {len(loaded_dfs)} dataframes...")
                self.processing_agent.save_multiple_dataframes(loaded_dfs)
                
                print("Processed files:")
                for name, path in self.processing_agent.get_processed_files().items():
                    print(f"  - {name}: {path}")
            
            return {
                'detection': detection_result,
                'loading': loading_result,
                'processing': self.processing_agent.state.dict()
            }
        else:
            print("Pipeline failed - no data detected or loaded")
            return None
    
    def get_available_dataframes(self) -> dict:
        """
        Get the dataframes that have been loaded.
        """
        return self.loading_agent.state.loaded_dataframes
    
    def analyze_dataframe(self, df_name: str) -> dict:
        """
        Perform basic analysis on a loaded dataframe.
        """
        df = self.loading_agent.get_dataframe(df_name)
        if df is None:
            return {'error': f'Dataframe {df_name} not found'}
        
        analysis = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'basic_stats': df.describe().to_dict() if df.select_dtypes(include=['number']).shape[1] > 0 else 'No numeric columns for stats',
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        return analysis


def main():
    # Create the MAS instance
    mas = DataScienceMAS()
    
    # Define data source directories to scan
    data_source_dirs = ["./input_data", "./data", "./sample_data"]
    
    # Run the analysis pipeline
    results = asyncio.run(mas.run_analysis_pipeline(data_source_dirs))
    
    if results:
        print("\nPipeline completed successfully!")
        
        # Display basic info about loaded dataframes
        dataframes = mas.get_available_dataframes()
        for name, df in dataframes.items():
            print(f"\nDataframe '{name}' shape: {df.shape}")
            print(f"Columns: {list(df.columns)[:10]}{'...' if len(df.columns) > 10 else ''}")
    else:
        print("\nPipeline failed to complete.")

if __name__ == "__main__":
    main()