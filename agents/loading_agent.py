from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from utils.file_utils import load_data_with_fallback
from config.settings import Config


class LoadingAgentState(BaseModel):
    """
    State for the loading agent
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    loaded_dataframes: Dict[str, pd.DataFrame] = Field(default_factory=dict)
    processing_status: str = "idle"
    last_error: str = None
    currently_loading_file: str = None
    loaded_file_info: Dict[str, Any] = Field(default_factory=dict)


class LoadingAgent:
    """
    Agent responsible for loading data files with header detection fallbacks.
    """
    
    def __init__(self):
        self.state = LoadingAgentState()
    
    def load_file(self, file_path: Path, file_type: str = None) -> LoadingAgentState:
        """
        Load a single file with fallback mechanisms for header detection.
        """
        try:
            self.state.currently_loading_file = str(file_path)
            self.state.processing_status = "loading"
            
            # If file type is not provided, detect it
            if not file_type:
                from utils.file_utils import detect_file_type
                file_type = detect_file_type(file_path)
            
            # Load the file with fallback mechanisms
            df = load_data_with_fallback(file_path, file_type)
            
            # Store the loaded dataframe
            file_key = file_path.stem  # Use filename without extension as key
            self.state.loaded_dataframes[file_key] = df
            
            # Store file info
            self.state.loaded_file_info[file_key] = {
                'path': str(file_path),
                'type': file_type,
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': {str(col): str(dtype) for col, dtype in df.dtypes.items()},
                'header_row_detected': self._detect_header_row(file_path, file_type)  # Simplified
            }
            
            self.state.processing_status = "completed"
            self.state.last_error = None
            self.state.currently_loading_file = None
            
            return self.state
            
        except Exception as e:
            self.state.processing_status = "error"
            self.state.last_error = str(e)
            self.state.currently_loading_file = None
            return self.state
    
    def load_multiple_files(self, file_list: List[Dict[str, Any]]) -> LoadingAgentState:
        """
        Load multiple files with fallback mechanisms.
        """
        try:
            self.state.processing_status = "loading_multiple"
            
            for file_info in file_list:
                file_path = file_info['path']
                file_type = file_info['type']
                
                # Load each file individually
                self.load_file(file_path, file_type)
                
                # Check if there was an error
                if self.state.processing_status == "error":
                    # Continue with other files despite error
                    continue
            
            self.state.processing_status = "completed"
            self.state.last_error = None
            
            return self.state
            
        except Exception as e:
            self.state.processing_status = "error"
            self.state.last_error = str(e)
            return self.state
    
    def _detect_header_row(self, file_path: Path, file_type: str) -> int:
        """
        Internal method to detect header row (simplified for this example).
        In a real implementation, this would use more sophisticated detection.
        """
        # This is a simplified placeholder - in reality, the detection happens
        # during the load_data_with_fallback function
        return 0  # Will be determined during actual loading
    
    def get_dataframe(self, key: str) -> pd.DataFrame:
        """
        Get a specific loaded dataframe by key.
        """
        return self.state.loaded_dataframes.get(key)
    
    def get_loaded_info(self) -> Dict[str, Any]:
        """
        Get information about loaded data.
        """
        return {
            "total_dataframes": len(self.state.loaded_dataframes),
            "dataframe_info": self.state.loaded_file_info,
            "status": self.state.processing_status
        }
    
    def update_state(self, new_state: LoadingAgentState):
        """
        Update the agent's state.
        """
        self.state = new_state