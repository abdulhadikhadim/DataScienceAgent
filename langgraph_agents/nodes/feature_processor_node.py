import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from typing import Dict, Any
from state import PreprocessingState


def process_features_node(state: PreprocessingState) -> PreprocessingState:
    """
    Feature Processor Agent - Performs feature engineering and transformations.
    - Encoding categorical variables
    - Scaling numerical features
    - Creating derived features
    - Removing duplicates
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data available for feature processing")
        return state
    
    df_processed = df.copy()
    processing_actions = []
    
    initial_duplicates = df_processed.duplicated().sum()
    if initial_duplicates > 0:
        df_processed = df_processed.drop_duplicates()
        processing_actions.append(f"Removed {initial_duplicates} duplicate rows")
    
    categorical_columns = df_processed.select_dtypes(include=['object', 'category']).columns
    
    for col in categorical_columns:
        unique_values = df_processed[col].nunique()
        
        if unique_values == 2:
            le = LabelEncoder()
            df_processed[col] = le.fit_transform(df_processed[col].astype(str))
            processing_actions.append(f"Binary encoded: {col}")
        
        elif unique_values <= 10:
            dummies = pd.get_dummies(df_processed[col], prefix=col, drop_first=True)
            df_processed = pd.concat([df_processed, dummies], axis=1)
            df_processed = df_processed.drop(columns=[col])
            processing_actions.append(f"One-hot encoded: {col} ({unique_values} categories)")
        
        else:
            le = LabelEncoder()
            df_processed[f"{col}_encoded"] = le.fit_transform(df_processed[col].astype(str))
            processing_actions.append(f"Label encoded: {col} -> {col}_encoded")
    
    numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        if df_processed[col].std() > 0:
            col_min = df_processed[col].min()
            col_max = df_processed[col].max()
            
            if col_min >= 0 and col_max <= 1:
                continue
            
            scaler = StandardScaler()
            df_processed[f"{col}_scaled"] = scaler.fit_transform(df_processed[[col]])
            processing_actions.append(f"Standardized: {col}")
    
    state["processed_data"] = df_processed
    state["current_agent"] = "feature_processor"
    state["preprocessing_steps"].append(
        f"Processed features: {len(processing_actions)} transformations applied"
    )
    
    state["feedback_messages"].append({
        "from_agent": "feature_processor",
        "to_agent": "validator",
        "message": f"Feature processing completed with {len(processing_actions)} transformations",
        "processing_summary": {
            "transformations_count": len(processing_actions),
            "new_shape": df_processed.shape,
            "new_columns": df_processed.shape[1] - df.shape[1],
            "actions": processing_actions
        }
    })
    
    return state
