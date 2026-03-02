import pandas as pd
import numpy as np
from typing import Dict, Any
import chardet
from langgraph_agents.state import PreprocessingState


def standardize_encoding_node(state: PreprocessingState) -> PreprocessingState:
    """
    Encoding Standardizer Agent - Standardizes text encoding to UTF-8.
    Handles encoding issues at source connection level.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for encoding standardization")
        return state
    
    df_standardized = df.copy()
    encoding_fixes = []
    
    for col in df_standardized.columns:
        if df_standardized[col].dtype == 'object':
            try:
                for idx in df_standardized.index:
                    val = df_standardized.at[idx, col]
                    
                    if pd.isna(val):
                        continue
                    
                    if isinstance(val, str):
                        try:
                            val_bytes = val.encode('latin-1')
                            detected = chardet.detect(val_bytes)
                            
                            if detected['encoding'] and detected['encoding'].lower() != 'utf-8':
                                decoded = val_bytes.decode(detected['encoding'], errors='ignore')
                                df_standardized.at[idx, col] = decoded.encode('utf-8', errors='ignore').decode('utf-8')
                                encoding_fixes.append(f"{col}[{idx}]: {detected['encoding']} -> UTF-8")
                        except:
                            df_standardized.at[idx, col] = str(val).encode('utf-8', errors='ignore').decode('utf-8')
                            encoding_fixes.append(f"{col}[{idx}]: forced UTF-8")
                
                df_standardized[col] = df_standardized[col].str.replace(r'[^\x00-\x7F]+', '', regex=True)
                
            except Exception as e:
                state["validation_errors"].append(f"Encoding error in column {col}: {str(e)}")
    
    state["processed_data"] = df_standardized
    state["current_agent"] = "encoding_standardizer"
    state["preprocessing_steps"].append(
        f"Encoding standardization fixed {len(encoding_fixes)} issues"
    )
    
    state["feedback_messages"].append({
        "from_agent": "encoding_standardizer",
        "to_agent": "referential_integrity_checker",
        "message": f"Encoding standardized with {len(encoding_fixes)} fixes",
        "fixes_count": len(encoding_fixes)
    })
    
    return state


def check_referential_integrity_node(state: PreprocessingState) -> PreprocessingState:
    """
    Referential Integrity Checker Agent - Validates primary/foreign key constraints.
    Enforces referential integrity checks in pipeline.
    """
    df = state.get("processed_data")
    schema_config = state.get("metadata", {}).get("schema_config")
    
    if df is None:
        state["validation_errors"].append("No data for referential integrity check")
        return state
    
    integrity_issues = []
    
    if schema_config and "primary_key" in schema_config:
        primary_keys = schema_config["primary_key"]
        
        if isinstance(primary_keys, str):
            primary_keys = [primary_keys]
        
        for pk in primary_keys:
            if pk in df.columns:
                null_count = df[pk].isnull().sum()
                if null_count > 0:
                    integrity_issues.append(f"Primary key '{pk}' has {null_count} null values")
                
                dup_count = df[pk].duplicated().sum()
                if dup_count > 0:
                    integrity_issues.append(f"Primary key '{pk}' has {dup_count} duplicates")
                    
                    df_deduped = df.drop_duplicates(subset=[pk], keep='first')
                    state["processed_data"] = df_deduped
                    state["preprocessing_steps"].append(
                        f"Removed {dup_count} duplicates based on primary key '{pk}'"
                    )
    
    if schema_config and "foreign_keys" in schema_config:
        foreign_keys = schema_config["foreign_keys"]
        
        for fk_col, ref_table in foreign_keys.items():
            if fk_col in df.columns:
                null_count = df[fk_col].isnull().sum()
                if null_count > 0:
                    integrity_issues.append(
                        f"Foreign key '{fk_col}' has {null_count} null values (referencing {ref_table})"
                    )
    
    if integrity_issues:
        state["validation_errors"].extend(integrity_issues)
        state["preprocessing_steps"].append(
            f"Referential integrity check found {len(integrity_issues)} issues"
        )
    else:
        state["preprocessing_steps"].append("Referential integrity check passed")
    
    state["current_agent"] = "referential_integrity_checker"
    
    state["feedback_messages"].append({
        "from_agent": "referential_integrity_checker",
        "to_agent": "data_quality_rules_engine",
        "message": f"Referential integrity check completed with {len(integrity_issues)} issues",
        "issues": integrity_issues
    })
    
    return state
