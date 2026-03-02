import pandas as pd
import numpy as np
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
from langgraph_agents.state import PreprocessingState


class RuleAction(Enum):
    """Actions to take when rule fails"""
    REJECT = "reject"
    FLAG = "flag"
    QUARANTINE = "quarantine"
    FIX = "fix"
    WARN = "warn"


@dataclass
class DataQualityRule:
    """Definition of a data quality rule"""
    name: str
    column: str
    condition: Callable[[pd.Series], pd.Series]
    action: RuleAction
    description: str
    fix_function: Callable[[pd.Series], pd.Series] = None


class DataQualityRulesEngine:
    """
    Engine for applying data quality rules.
    Supports range checks, pattern matching, and custom validations.
    """
    
    def __init__(self):
        self.rules: List[DataQualityRule] = []
        self.violations: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: DataQualityRule):
        """Add a quality rule"""
        self.rules.append(rule)
    
    def add_range_rule(self, column: str, min_val: float, max_val: float, 
                       action: RuleAction = RuleAction.FLAG):
        """Add a range check rule"""
        rule = DataQualityRule(
            name=f"{column}_range_check",
            column=column,
            condition=lambda s: (s >= min_val) & (s <= max_val),
            action=action,
            description=f"{column} must be between {min_val} and {max_val}",
            fix_function=lambda s: s.clip(lower=min_val, upper=max_val) if action == RuleAction.FIX else s
        )
        self.add_rule(rule)
    
    def add_pattern_rule(self, column: str, pattern: str, action: RuleAction = RuleAction.FLAG):
        """Add a pattern matching rule"""
        rule = DataQualityRule(
            name=f"{column}_pattern_check",
            column=column,
            condition=lambda s: s.astype(str).str.match(pattern, na=False),
            action=action,
            description=f"{column} must match pattern {pattern}"
        )
        self.add_rule(rule)
    
    def add_not_null_rule(self, column: str, action: RuleAction = RuleAction.REJECT):
        """Add a not-null rule"""
        rule = DataQualityRule(
            name=f"{column}_not_null",
            column=column,
            condition=lambda s: s.notna(),
            action=action,
            description=f"{column} must not be null"
        )
        self.add_rule(rule)
    
    def add_unique_rule(self, column: str, action: RuleAction = RuleAction.FLAG):
        """Add a uniqueness rule"""
        rule = DataQualityRule(
            name=f"{column}_unique",
            column=column,
            condition=lambda s: ~s.duplicated(keep=False),
            action=action,
            description=f"{column} values must be unique"
        )
        self.add_rule(rule)
    
    def apply_rules(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Apply all rules to dataframe"""
        df_result = df.copy()
        quarantine_records = []
        flagged_records = []
        rejected_count = 0
        fixed_count = 0
        
        for rule in self.rules:
            if rule.column not in df_result.columns:
                continue
            
            mask = rule.condition(df_result[rule.column])
            violations_mask = ~mask
            violation_count = violations_mask.sum()
            
            if violation_count > 0:
                violation_indices = df_result[violations_mask].index.tolist()
                
                self.violations.append({
                    "rule": rule.name,
                    "column": rule.column,
                    "count": violation_count,
                    "indices": violation_indices[:100],
                    "action": rule.action.value,
                    "description": rule.description
                })
                
                if rule.action == RuleAction.REJECT:
                    df_result = df_result[mask]
                    rejected_count += violation_count
                
                elif rule.action == RuleAction.FLAG:
                    flag_col = f"{rule.column}_quality_flag"
                    df_result[flag_col] = False
                    df_result.loc[violations_mask, flag_col] = True
                    flagged_records.extend(violation_indices)
                
                elif rule.action == RuleAction.QUARANTINE:
                    quarantine_df = df_result[violations_mask].copy()
                    quarantine_df['quarantine_reason'] = rule.description
                    quarantine_records.append(quarantine_df)
                    df_result = df_result[mask]
                
                elif rule.action == RuleAction.FIX and rule.fix_function:
                    df_result[rule.column] = rule.fix_function(df_result[rule.column])
                    fixed_count += violation_count
        
        return {
            "processed_data": df_result,
            "violations": self.violations,
            "quarantine_records": pd.concat(quarantine_records) if quarantine_records else None,
            "flagged_count": len(set(flagged_records)),
            "rejected_count": rejected_count,
            "fixed_count": fixed_count
        }


def apply_data_quality_rules_node(state: PreprocessingState) -> PreprocessingState:
    """
    Data Quality Rules Engine Agent - Applies range checks and validation rules.
    Rejects or flags records based on data quality rules.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data for quality rules")
        return state
    
    engine = DataQualityRulesEngine()
    
    quality_rules = state.get("metadata", {}).get("quality_rules", [])
    
    if not quality_rules:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            q1 = df[col].quantile(0.01)
            q99 = df[col].quantile(0.99)
            engine.add_range_rule(col, q1, q99, action=RuleAction.FLAG)
        
        for col in df.columns:
            if df[col].isnull().any():
                null_pct = df[col].isnull().sum() / len(df)
                if null_pct < 0.1:
                    engine.add_not_null_rule(col, action=RuleAction.FLAG)
    else:
        for rule_config in quality_rules:
            rule_type = rule_config.get("type")
            column = rule_config.get("column")
            action = RuleAction[rule_config.get("action", "FLAG").upper()]
            
            if rule_type == "range":
                engine.add_range_rule(
                    column,
                    rule_config.get("min"),
                    rule_config.get("max"),
                    action
                )
            elif rule_type == "pattern":
                engine.add_pattern_rule(
                    column,
                    rule_config.get("pattern"),
                    action
                )
            elif rule_type == "not_null":
                engine.add_not_null_rule(column, action)
            elif rule_type == "unique":
                engine.add_unique_rule(column, action)
    
    result = engine.apply_rules(df)
    
    state["processed_data"] = result["processed_data"]
    state["metadata"]["quality_violations"] = result["violations"]
    
    if result["quarantine_records"] is not None:
        state["metadata"]["quarantine_records"] = result["quarantine_records"]
    
    state["current_agent"] = "data_quality_rules_engine"
    state["preprocessing_steps"].append(
        f"Quality rules applied: {result['flagged_count']} flagged, "
        f"{result['rejected_count']} rejected, {result['fixed_count']} fixed"
    )
    
    state["feedback_messages"].append({
        "from_agent": "data_quality_rules_engine",
        "to_agent": "deduplication_agent",
        "message": f"Quality rules applied with {len(result['violations'])} violations",
        "summary": {
            "flagged": result["flagged_count"],
            "rejected": result["rejected_count"],
            "fixed": result["fixed_count"]
        }
    })
    
    return state


def deduplicate_records_node(state: PreprocessingState) -> PreprocessingState:
    """
    Deduplication Agent - Removes duplicates using primary key or hash.
    Smart deduplication with multiple strategies.
    """
    df = state.get("processed_data")
    
    if df is None:
        state["validation_errors"].append("No data for deduplication")
        return state
    
    initial_count = len(df)
    schema_config = state.get("metadata", {}).get("schema_config", {})
    primary_key = schema_config.get("primary_key")
    
    if primary_key:
        if isinstance(primary_key, str):
            primary_key = [primary_key]
        
        df_deduped = df.drop_duplicates(subset=primary_key, keep='first')
        dedup_method = f"primary key ({', '.join(primary_key)})"
    else:
        df['_row_hash'] = pd.util.hash_pandas_object(df, index=False)
        df_deduped = df.drop_duplicates(subset='_row_hash', keep='first')
        df_deduped = df_deduped.drop(columns=['_row_hash'])
        dedup_method = "row hash"
    
    duplicates_removed = initial_count - len(df_deduped)
    
    state["processed_data"] = df_deduped
    state["current_agent"] = "deduplication_agent"
    state["preprocessing_steps"].append(
        f"Deduplication removed {duplicates_removed} duplicates using {dedup_method}"
    )
    
    state["feedback_messages"].append({
        "from_agent": "deduplication_agent",
        "to_agent": "validator",
        "message": f"Deduplication completed: {duplicates_removed} duplicates removed",
        "method": dedup_method,
        "final_count": len(df_deduped)
    })
    
    return state
