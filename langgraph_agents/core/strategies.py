from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd
import numpy as np
from enum import Enum


class StrategyType(Enum):
    """Types of processing strategies"""
    ANOMALY_HANDLING = "anomaly_handling"
    NULL_HANDLING = "null_handling"
    ENCODING = "encoding"
    VALIDATION = "validation"
    NORMALIZATION = "normalization"


class ProcessingStrategy(ABC):
    """
    Strategy Pattern for different processing approaches.
    Allows runtime selection of algorithms.
    """
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def apply(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Apply the strategy to data"""
        pass
    
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> bool:
        """Validate if strategy can be applied"""
        pass


class AnomalyHandlingStrategy(ProcessingStrategy):
    """Base class for anomaly handling strategies"""
    
    def __init__(self, name: str):
        super().__init__(name)


class CapOutliersStrategy(AnomalyHandlingStrategy):
    """Cap outliers at IQR bounds"""
    
    def __init__(self):
        super().__init__("cap_outliers")
    
    def validate(self, data: pd.DataFrame) -> bool:
        return len(data.select_dtypes(include=[np.number]).columns) > 0
    
    def apply(self, data: pd.DataFrame, column: str = None, **kwargs) -> pd.DataFrame:
        df = data.copy()
        columns = [column] if column else df.select_dtypes(include=[np.number]).columns
        
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df[col] = df[col].clip(lower=lower, upper=upper)
        
        return df


class RemoveOutliersStrategy(AnomalyHandlingStrategy):
    """Remove rows with outliers"""
    
    def __init__(self):
        super().__init__("remove_outliers")
    
    def validate(self, data: pd.DataFrame) -> bool:
        return len(data) > 10
    
    def apply(self, data: pd.DataFrame, column: str = None, **kwargs) -> pd.DataFrame:
        df = data.copy()
        columns = [column] if column else df.select_dtypes(include=[np.number]).columns
        
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower) & (df[col] <= upper)]
        
        return df


class NullHandlingStrategy(ProcessingStrategy):
    """Base class for null handling strategies"""
    
    def __init__(self, name: str):
        super().__init__(name)


class SmartImputationStrategy(NullHandlingStrategy):
    """Smart imputation based on data characteristics"""
    
    def __init__(self):
        super().__init__("smart_imputation")
    
    def validate(self, data: pd.DataFrame) -> bool:
        return data.isnull().sum().sum() > 0
    
    def apply(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df = data.copy()
        
        for col in df.columns:
            null_pct = df[col].isnull().sum() / len(df)
            
            if null_pct > 0.5:
                df = df.drop(columns=[col])
                continue
            
            if df[col].dtype in [np.float64, np.int64]:
                if df[col].skew() > 1:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mean(), inplace=True)
            else:
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    df[col].fillna(mode_val[0], inplace=True)
        
        return df


class EncodingStrategy(ProcessingStrategy):
    """Base class for encoding strategies"""
    
    def __init__(self, name: str):
        super().__init__(name)


class AutoEncodingStrategy(EncodingStrategy):
    """Automatic encoding based on cardinality"""
    
    def __init__(self):
        super().__init__("auto_encoding")
    
    def validate(self, data: pd.DataFrame) -> bool:
        return len(data.select_dtypes(include=['object', 'category']).columns) > 0
    
    def apply(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        from sklearn.preprocessing import LabelEncoder
        
        df = data.copy()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            
            if unique_count == 2:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
            elif unique_count <= 10:
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df, dummies], axis=1)
                df = df.drop(columns=[col])
            else:
                le = LabelEncoder()
                df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
        
        return df


class StrategyRegistry:
    """
    Registry for managing processing strategies.
    Singleton Pattern.
    """
    
    _instance = None
    _strategies: Dict[StrategyType, Dict[str, ProcessingStrategy]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_strategies()
        return cls._instance
    
    def _initialize_strategies(self):
        """Initialize default strategies"""
        self._strategies = {
            StrategyType.ANOMALY_HANDLING: {
                "cap": CapOutliersStrategy(),
                "remove": RemoveOutliersStrategy()
            },
            StrategyType.NULL_HANDLING: {
                "smart": SmartImputationStrategy()
            },
            StrategyType.ENCODING: {
                "auto": AutoEncodingStrategy()
            }
        }
    
    def register(self, strategy_type: StrategyType, name: str, strategy: ProcessingStrategy):
        """Register a new strategy"""
        if strategy_type not in self._strategies:
            self._strategies[strategy_type] = {}
        self._strategies[strategy_type][name] = strategy
    
    def get(self, strategy_type: StrategyType, name: str) -> ProcessingStrategy:
        """Get a strategy by type and name"""
        if strategy_type not in self._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        if name not in self._strategies[strategy_type]:
            raise ValueError(f"Unknown strategy: {name} for type {strategy_type}")
        return self._strategies[strategy_type][name]
    
    def list_strategies(self, strategy_type: StrategyType) -> List[str]:
        """List available strategies for a type"""
        return list(self._strategies.get(strategy_type, {}).keys())
