import os
from pathlib import Path

# Configuration settings for the multi-agent data science system

class Config:
    # Data source directories
    DATA_SOURCE_DIRS = [
        "./input_data",
        "./data",
        "./datasets",
        "./raw_data"
    ]
    
    # Output directory for processed data
    PROCESSED_DATA_DIR = "./data"
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.json', '.parquet', '.txt']
    
    # Maximum file size to process (in MB)
    MAX_FILE_SIZE_MB = 100
    
    # Default encoding for text files
    DEFAULT_ENCODING = 'utf-8'
    
    # Header detection parameters
    HEADER_DETECTION_ROWS = 5  # Check first 5 rows for headers
    
    # Agent communication settings
    AGENT_COMMUNICATION_TIMEOUT = 30  # seconds
    
    @classmethod
    def get_data_dirs(cls):
        """Return list of data directories to search for files"""
        return [Path(d) for d in cls.DATA_SOURCE_DIRS]
    
    @classmethod
    def ensure_output_dir(cls):
        """Ensure output directory exists"""
        output_path = Path(cls.PROCESSED_DATA_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path