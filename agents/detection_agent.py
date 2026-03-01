from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from pydantic import BaseModel, Field

from utils.file_utils import scan_for_data_files, detect_file_type
from config.settings import Config


class DetectionAgentState(BaseModel):
    """
    State for the detection agent
    """
    detected_files: List[Dict[str, Any]] = Field(default_factory=list)
    processing_status: str = "idle"
    last_error: str = None
    search_directories: List[str] = Field(default_factory=lambda: [str(d) for d in Config.get_data_dirs()])


class DetectionAgent:
    """
    Agent responsible for detecting and identifying data files in specified directories.
    """
    
    def __init__(self):
        self.state = DetectionAgentState()
    
    def scan_directories(self, custom_dirs: List[str] = None) -> DetectionAgentState:
        """
        Scan directories for data files and update the agent's state.
        """
        try:
            self.state.processing_status = "scanning"
            
            # Use custom directories if provided, otherwise use configured ones
            if custom_dirs:
                search_paths = [Path(d) for d in custom_dirs]
            else:
                search_paths = Config.get_data_dirs()
            
            # Scan for data files
            detected_files = scan_for_data_files(search_paths)
            
            # Update state
            self.state.detected_files = detected_files
            self.state.processing_status = "completed"
            self.state.last_error = None
            
            return self.state
            
        except Exception as e:
            self.state.processing_status = "error"
            self.state.last_error = str(e)
            return self.state
    
    def identify_file_types(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize detected files by type.
        """
        categorized = {}
        for file_info in self.state.detected_files:
            file_type = file_info['type']
            if file_type not in categorized:
                categorized[file_type] = []
            categorized[file_type].append(file_info)
        return categorized
    
    def get_file_summary(self) -> Dict[str, Any]:
        """
        Get a summary of detected files.
        """
        summary = {
            "total_files": len(self.state.detected_files),
            "by_type": {},
            "total_size_mb": 0,
            "directories_scanned": self.state.search_directories
        }
        
        for file_info in self.state.detected_files:
            file_type = file_info['type']
            if file_type not in summary["by_type"]:
                summary["by_type"][file_type] = {"count": 0, "size_mb": 0}
            summary["by_type"][file_type]["count"] += 1
            summary["by_type"][file_type]["size_mb"] += file_info['size_mb']
            summary["total_size_mb"] += file_info['size_mb']
        
        return summary
    
    def get_file_paths_by_type(self, file_type: str) -> List[Path]:
        """
        Get file paths filtered by type.
        """
        return [
            file_info['path'] for file_info in self.state.detected_files
            if file_info['type'] == file_type
        ]
    
    def update_state(self, new_state: DetectionAgentState):
        """
        Update the agent's state.
        """
        self.state = new_state