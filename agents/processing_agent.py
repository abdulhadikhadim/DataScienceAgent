from pathlib import Path
from typing import Dict, Any
import pandas as pd
from pydantic import BaseModel, Field
import json

from config.settings import Config


class ProcessingAgentState(BaseModel):
    """
    State for the processing agent
    """
    processed_files: Dict[str, str] = Field(default_factory=dict)  # filename -> output_path
    processing_status: str = "idle"
    last_error: str = None
    output_directory: str = Field(default_factory=lambda: str(Config.ensure_output_dir()))


class ProcessingAgent:
    """
    Agent responsible for processing and saving data to the configured output directory.
    """
    
    def __init__(self):
        self.state = ProcessingAgentState()
    
    def save_dataframe(self, df: pd.DataFrame, output_name: str, file_format: str = 'parquet') -> ProcessingAgentState:
        """
        Save a dataframe to the configured output directory.
        """
        try:
            self.state.processing_status = "saving"
            
            # Ensure output directory exists
            output_dir = Path(self.state.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create output file path
            if file_format == 'parquet':
                output_path = output_dir / f"{output_name}.parquet"
                df.to_parquet(output_path)
            elif file_format == 'csv':
                output_path = output_dir / f"{output_name}.csv"
                df.to_csv(output_path, index=False)
            elif file_format == 'excel':
                output_path = output_dir / f"{output_name}.xlsx"
                df.to_excel(output_path, index=False)
            elif file_format == 'json':
                output_path = output_dir / f"{output_name}.json"
                df.to_json(output_path, orient='records', indent=2)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
            
            # Update state with the saved file info
            self.state.processed_files[output_name] = str(output_path)
            
            self.state.processing_status = "completed"
            self.state.last_error = None
            
            return self.state
            
        except Exception as e:
            self.state.processing_status = "error"
            self.state.last_error = str(e)
            return self.state
    
    def save_multiple_dataframes(self, dataframes: Dict[str, pd.DataFrame], base_name: str = "processed") -> ProcessingAgentState:
        """
        Save multiple dataframes to the output directory with unique names.
        """
        try:
            self.state.processing_status = "saving_multiple"
            
            for idx, (name, df) in enumerate(dataframes.items()):
                output_name = f"{base_name}_{name}" if name else f"{base_name}_{idx}"
                self.save_dataframe(df, output_name)
                
                # Check if there was an error
                if self.state.processing_status == "error":
                    # Continue with other dataframes despite error
                    continue
            
            self.state.processing_status = "completed"
            self.state.last_error = None
            
            return self.state
            
        except Exception as e:
            self.state.processing_status = "error"
            self.state.last_error = str(e)
            return self.state
    
    def get_processed_files(self) -> Dict[str, str]:
        """
        Get information about processed files.
        """
        return self.state.processed_files
    
    def update_output_directory(self, new_directory: str):
        """
        Update the output directory.
        """
        new_path = Path(new_directory)
        new_path.mkdir(parents=True, exist_ok=True)
        self.state.output_directory = str(new_path)
    
    def update_state(self, new_state: ProcessingAgentState):
        """
        Update the agent's state.
        """
        self.state = new_state