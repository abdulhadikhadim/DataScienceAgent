import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator, ValidationError
from datetime import datetime
from state import PreprocessingState


class ColumnSchema(BaseModel):
    """Schema definition for a single column"""
    name: str
    dtype: str
    nullable: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    regex_pattern: Optional[str] = None
    description: Optional[str] = None


class DataSchema(BaseModel):
    """Complete data schema definition"""
    name: str
    version: str = "1.0"
    columns: List[ColumnSchema]
    primary_key: Optional[List[str]] = None
    foreign_keys: Optional[Dict[str, str]] = None
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate dataframe against schema"""
        errors = []
        warnings = []
        
        expected_cols = {col.name for col in self.columns}
        actual_cols = set(df.columns)
        
        missing_cols = expected_cols - actual_cols
        extra_cols = actual_cols - expected_cols
        
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        if extra_cols:
            warnings.append(f"Extra columns: {extra_cols}")
        
        for col_schema in self.columns:
            if col_schema.name not in df.columns:
                continue
            
            col_data = df[col_schema.name]
            
            expected_dtype = col_schema.dtype
            actual_dtype = str(col_data.dtype)
            
            if not self._dtypes_compatible(expected_dtype, actual_dtype):
                errors.append(
                    f"Column '{col_schema.name}': expected {expected_dtype}, got {actual_dtype}"
                )
            
            if not col_schema.nullable:
                null_count = col_data.isnull().sum()
                if null_count > 0:
                    errors.append(
                        f"Column '{col_schema.name}': {null_count} null values found (not nullable)"
                    )
            
            if col_schema.min_value is not None and pd.api.types.is_numeric_dtype(col_data):
                min_val = col_data.min()
                if min_val < col_schema.min_value:
                    errors.append(
                        f"Column '{col_schema.name}': min value {min_val} < {col_schema.min_value}"
                    )
            
            if col_schema.max_value is not None and pd.api.types.is_numeric_dtype(col_data):
                max_val = col_data.max()
                if max_val > col_schema.max_value:
                    errors.append(
                        f"Column '{col_schema.name}': max value {max_val} > {col_schema.max_value}"
                    )
            
            if col_schema.allowed_values is not None:
                invalid_values = set(col_data.dropna().unique()) - set(col_schema.allowed_values)
                if invalid_values:
                    errors.append(
                        f"Column '{col_schema.name}': invalid values {invalid_values}"
                    )
            
            if col_schema.regex_pattern is not None:
                import re
                pattern = re.compile(col_schema.regex_pattern)
                invalid_count = sum(
                    not pattern.match(str(val)) 
                    for val in col_data.dropna() 
                    if val is not None
                )
                if invalid_count > 0:
                    warnings.append(
                        f"Column '{col_schema.name}': {invalid_count} values don't match pattern"
                    )
        
        if self.primary_key:
            for pk_col in self.primary_key:
                if pk_col in df.columns:
                    null_count = df[pk_col].isnull().sum()
                    if null_count > 0:
                        errors.append(f"Primary key '{pk_col}' has {null_count} null values")
                    
                    dup_count = df[pk_col].duplicated().sum()
                    if dup_count > 0:
                        errors.append(f"Primary key '{pk_col}' has {dup_count} duplicates")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _dtypes_compatible(self, expected: str, actual: str) -> bool:
        """Check if data types are compatible"""
        type_mapping = {
            "int": ["int64", "int32", "int16", "int8"],
            "float": ["float64", "float32", "float16"],
            "string": ["object", "string"],
            "bool": ["bool"],
            "datetime": ["datetime64[ns]", "datetime64"]
        }
        
        for base_type, compatible_types in type_mapping.items():
            if expected == base_type or expected in compatible_types:
                return actual in compatible_types
        
        return expected == actual


def validate_schema_node(state: PreprocessingState) -> PreprocessingState:
    """
    Schema Validator Agent - Validates data against defined schema.
    Enforces schema validation using Pydantic models.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for schema validation")
        return state
    
    schema_config = state.get("metadata", {}).get("schema_config")
    
    if schema_config is None:
        state["preprocessing_steps"].append("Schema validation skipped - no schema defined")
        return state
    
    try:
        schema = DataSchema(**schema_config)
        
        validation_result = schema.validate_dataframe(df)
        
        state["metadata"]["schema_validation"] = validation_result
        
        if validation_result["valid"]:
            state["preprocessing_steps"].append(
                f"Schema validation passed for '{schema.name}' v{schema.version}"
            )
            
            if validation_result["warnings"]:
                state["preprocessing_steps"].append(
                    f"Schema validation warnings: {len(validation_result['warnings'])}"
                )
        else:
            state["validation_errors"].extend(validation_result["errors"])
            state["preprocessing_steps"].append(
                f"Schema validation failed with {len(validation_result['errors'])} errors"
            )
        
        state["feedback_messages"].append({
            "from_agent": "schema_validator",
            "to_agent": "data_type_caster",
            "message": f"Schema validation {'passed' if validation_result['valid'] else 'failed'}",
            "validation_result": validation_result
        })
        
    except ValidationError as e:
        state["validation_errors"].append(f"Schema definition error: {str(e)}")
    except Exception as e:
        state["validation_errors"].append(f"Schema validation error: {str(e)}")
    
    state["current_agent"] = "schema_validator"
    return state


def enforce_schema_node(state: PreprocessingState) -> PreprocessingState:
    """
    Schema Enforcer Agent - Enforces schema by casting types and fixing issues.
    """
    df = state.get("processed_data")
    schema_config = state.get("metadata", {}).get("schema_config")
    
    if df is None or schema_config is None:
        return state
    
    try:
        schema = DataSchema(**schema_config)
        df_enforced = df.copy()
        fixes_applied = []
        
        for col_schema in schema.columns:
            if col_schema.name not in df_enforced.columns:
                df_enforced[col_schema.name] = None
                fixes_applied.append(f"Added missing column: {col_schema.name}")
                continue
            
            col = df_enforced[col_schema.name]
            
            try:
                if col_schema.dtype == "int":
                    df_enforced[col_schema.name] = pd.to_numeric(col, errors='coerce').astype('Int64')
                    fixes_applied.append(f"Cast {col_schema.name} to int")
                elif col_schema.dtype == "float":
                    df_enforced[col_schema.name] = pd.to_numeric(col, errors='coerce')
                    fixes_applied.append(f"Cast {col_schema.name} to float")
                elif col_schema.dtype == "string":
                    df_enforced[col_schema.name] = col.astype(str)
                    fixes_applied.append(f"Cast {col_schema.name} to string")
                elif col_schema.dtype == "bool":
                    df_enforced[col_schema.name] = col.astype(bool)
                    fixes_applied.append(f"Cast {col_schema.name} to bool")
                elif col_schema.dtype == "datetime":
                    df_enforced[col_schema.name] = pd.to_datetime(col, errors='coerce')
                    fixes_applied.append(f"Cast {col_schema.name} to datetime")
            except Exception as e:
                state["validation_errors"].append(
                    f"Failed to cast {col_schema.name} to {col_schema.dtype}: {str(e)}"
                )
        
        extra_cols = set(df_enforced.columns) - {col.name for col in schema.columns}
        if extra_cols:
            df_enforced = df_enforced.drop(columns=list(extra_cols))
            fixes_applied.append(f"Removed extra columns: {extra_cols}")
        
        state["processed_data"] = df_enforced
        state["preprocessing_steps"].append(
            f"Schema enforcement applied {len(fixes_applied)} fixes"
        )
        
        state["feedback_messages"].append({
            "from_agent": "schema_enforcer",
            "to_agent": "data_type_caster",
            "message": f"Schema enforced with {len(fixes_applied)} fixes",
            "fixes": fixes_applied
        })
        
    except Exception as e:
        state["validation_errors"].append(f"Schema enforcement error: {str(e)}")
    
    state["current_agent"] = "schema_enforcer"
    return state
