# LangGraph Data Preprocessing - Architecture Documentation

## 🏗️ System Architecture

### Overview

The LangGraph Data Preprocessing Agent System is built on a **state machine architecture** where multiple specialized agents process data through a directed acyclic graph (DAG) with conditional edges and feedback loops.

## 🔄 State Flow Architecture

### State Schema

```python
PreprocessingState = TypedDict({
    # Data
    "raw_data": pd.DataFrame,           # Original unmodified data
    "processed_data": pd.DataFrame,     # Current state of data
    
    # Metadata
    "data_source": str,                 # File path
    "data_format": str,                 # csv, excel, json, parquet
    "metadata": Dict,                   # File info, shapes, dtypes
    
    # Detection Results
    "anomalies_detected": List[Dict],   # Anomaly patterns found
    "null_values_info": Dict,           # Null value analysis
    
    # Processing Configuration
    "anomaly_handling_strategy": str,   # How to handle anomalies
    "null_handling_strategy": str,      # How to handle nulls
    
    # Validation
    "validation_passed": bool,          # Final validation status
    "validation_errors": List[str],     # Validation error messages
    
    # Workflow Control
    "current_agent": str,               # Currently executing agent
    "workflow_status": str,             # Overall workflow status
    "iteration_count": int,             # Retry counter
    "max_iterations": int,              # Maximum retries allowed
    
    # Audit Trail
    "preprocessing_steps": List[str],   # Step-by-step log
    "feedback_messages": List[Dict],    # Inter-agent communication
})
```

### State Annotations

Using LangGraph's `Annotated` type for list fields:
- `Annotated[List[Dict], add]` - Appends to list instead of replacing
- Enables cumulative tracking of anomalies, steps, and feedback

## 🤖 Agent Architecture

### 1. Data Loader Agent

**Responsibility**: Load data from various sources

**Input State**:
- `data_source`: File path

**Output State**:
- `raw_data`: Loaded DataFrame
- `processed_data`: Copy of raw data
- `metadata`: File information
- `data_format`: Detected format

**Logic**:
```python
1. Validate file exists
2. Detect file format from extension
3. Load using appropriate pandas reader
4. Initialize metadata
5. Send feedback to anomaly detector
```

**Deterministic**: Yes - Same file always loads identically

---

### 2. Anomaly Detector Agent

**Responsibility**: Detect outliers and anomalies

**Input State**:
- `processed_data`: Current DataFrame

**Output State**:
- `anomalies_detected`: List of anomaly patterns

**Detection Methods**:

1. **IQR Method** (Interquartile Range)
   ```python
   Q1 = quantile(0.25)
   Q3 = quantile(0.75)
   IQR = Q3 - Q1
   lower_bound = Q1 - 1.5 * IQR
   upper_bound = Q3 + 1.5 * IQR
   outliers = values < lower_bound OR values > upper_bound
   ```

2. **Z-Score Method**
   ```python
   z_score = abs((value - mean) / std)
   outliers = z_score > 3.0
   ```

3. **Rare Categories**
   ```python
   frequency = value_counts / total_count
   rare = frequency < 0.01  # 1% threshold
   ```

**Deterministic**: Yes - Statistical methods are deterministic

---

### 3. Anomaly Handler Agent

**Responsibility**: Handle detected anomalies

**Input State**:
- `processed_data`: Current DataFrame
- `anomalies_detected`: Detected patterns
- `anomaly_handling_strategy`: Strategy to use

**Output State**:
- `processed_data`: Modified DataFrame

**Strategies**:

| Strategy | Action | Use Case |
|----------|--------|----------|
| `cap` | Clip values at bounds | Preserve data volume |
| `remove` | Drop outlier rows | Clean dataset |
| `transform` | Log transformation | Reduce skewness |
| `flag` | Add indicator column | Keep all data |
| `group` | Merge rare categories | Categorical data |

**Deterministic**: Yes - Each strategy applies consistent rules

---

### 4. Null Detector Agent

**Responsibility**: Analyze missing values

**Input State**:
- `processed_data`: Current DataFrame

**Output State**:
- `null_values_info`: Per-column null analysis

**Analysis**:
```python
For each column:
    - Count null values
    - Calculate percentage
    - Record data type
```

**Deterministic**: Yes - Counting is deterministic

---

### 5. Null Handler Agent

**Responsibility**: Impute or remove null values

**Input State**:
- `processed_data`: Current DataFrame
- `null_values_info`: Null analysis
- `null_handling_strategy`: Strategy to use

**Output State**:
- `processed_data`: Modified DataFrame

**Smart Strategy Logic**:
```python
if null_percentage > 50%:
    drop_column()
elif dtype is numeric:
    if skew > 1:
        fill_with_median()
    else:
        fill_with_mean()
elif dtype is categorical:
    fill_with_mode()
```

**Deterministic**: Yes - Statistical measures are deterministic

---

### 6. Feature Processor Agent

**Responsibility**: Feature engineering and encoding

**Input State**:
- `processed_data`: Current DataFrame

**Output State**:
- `processed_data`: Transformed DataFrame

**Operations**:

1. **Duplicate Removal**
   ```python
   df.drop_duplicates()
   ```

2. **Categorical Encoding**
   - Binary (2 categories) → Label Encoding
   - Few categories (≤10) → One-Hot Encoding
   - Many categories (>10) → Label Encoding

3. **Numerical Scaling**
   ```python
   StandardScaler: (x - mean) / std
   ```

**Deterministic**: Yes - Transformations are deterministic

---

### 7. Validator Agent

**Responsibility**: Validate ML-readiness

**Input State**:
- `processed_data`: Current DataFrame

**Output State**:
- `validation_passed`: Boolean
- `validation_errors`: List of errors

**Validation Checks**:

1. ✓ No null values
2. ✓ No infinite values
3. ✓ Sufficient data volume (≥10 rows)
4. ✓ At least one feature
5. ✓ Non-zero variance in numeric columns
6. ⚠ Warning: Object dtypes remaining
7. ⚠ Warning: Duplicate rows

**Deterministic**: Yes - Rule-based validation

---

### 8. Retry Decision Agent

**Responsibility**: Manage feedback loop

**Input State**:
- `validation_passed`: Boolean
- `iteration_count`: Current iteration
- `max_iterations`: Maximum allowed

**Output State**:
- `workflow_status`: "completed" or "retrying"
- `iteration_count`: Incremented
- Strategy adjustments

**Logic**:
```python
if validation_passed:
    return "end"
elif iteration_count < max_iterations:
    adjust_strategies()
    return "retry"
else:
    return "end"
```

**Strategy Adjustment**:
- Anomaly: cap → flag
- Null: smart → median

**Deterministic**: Yes - Rule-based decisions

---

## 🔀 Workflow Graph

### Node Connections

```
START
  ↓
load_data
  ↓
detect_anomalies
  ↓
  ├─→ [anomalies found] → handle_anomalies
  │                            ↓
  └─→ [no anomalies] ─────────→ detect_nulls
                                  ↓
                                  ├─→ [nulls found] → handle_nulls
                                  │                        ↓
                                  └─→ [no nulls] ─────────→ process_features
                                                              ↓
                                                           validate
                                                              ↓
                                                              ├─→ [passed] → END
                                                              │
                                                              └─→ [failed] → retry_decision
                                                                                ↓
                                                                                ├─→ [can retry] → detect_anomalies
                                                                                │                  (FEEDBACK LOOP)
                                                                                └─→ [max iterations] → END
```

### Conditional Edges

1. **After Anomaly Detection**
   ```python
   if len(anomalies_detected) > 0:
       goto("handle_anomalies")
   else:
       goto("detect_nulls")
   ```

2. **After Null Detection**
   ```python
   if len(null_values_info) > 0:
       goto("handle_nulls")
   else:
       goto("process_features")
   ```

3. **After Validation**
   ```python
   if validation_passed:
       goto(END)
   elif iteration_count < max_iterations:
       goto("retry_decision")
   else:
       goto(END)
   ```

---

## 💬 Agent Communication

### Feedback Message Structure

```python
{
    "from_agent": str,        # Sender agent name
    "to_agent": str,          # Receiver agent name
    "message": str,           # Human-readable message
    "data_info": Dict,        # Optional structured data
    "anomaly_summary": Dict,  # Optional anomaly details
    "null_summary": Dict,     # Optional null details
    # ... other context-specific fields
}
```

### Communication Flow

```
Data Loader
  ↓ "Data loaded with shape (100, 5)"
Anomaly Detector
  ↓ "Found 3 anomaly patterns"
Anomaly Handler
  ↓ "Handled using cap strategy"
Null Detector
  ↓ "Found nulls in 2 columns"
Null Handler
  ↓ "Handled using smart strategy"
Feature Processor
  ↓ "Applied 5 transformations"
Validator
  ↓ "Validation passed - ready for ML"
```

---

## 🔁 Feedback Loop Mechanism

### Iteration Flow

```
Iteration 1:
  detect_anomalies → handle_anomalies (cap) → ... → validate (FAIL)
    ↓
  retry_decision: Switch to "flag" strategy
    ↓
Iteration 2:
  detect_anomalies → handle_anomalies (flag) → ... → validate (FAIL)
    ↓
  retry_decision: Switch to "median" for nulls
    ↓
Iteration 3:
  detect_anomalies → handle_anomalies (flag) → ... → validate (PASS)
    ↓
  END
```

### Strategy Evolution

| Iteration | Anomaly Strategy | Null Strategy |
|-----------|------------------|---------------|
| 1 | cap | smart |
| 2 | flag | smart |
| 3 | flag | median |

---

## 📊 Data Flow

### Data Transformations

```
Raw Data (loaded)
  ↓
Anomalies Capped/Removed/Flagged
  ↓
Nulls Imputed/Removed
  ↓
Duplicates Removed
  ↓
Categories Encoded
  ↓
Numerics Scaled
  ↓
Validated Data (ML-ready)
```

### State Evolution

```python
# Initial
state = {
    "raw_data": None,
    "processed_data": None,
    "anomalies_detected": [],
    ...
}

# After Data Loader
state = {
    "raw_data": DataFrame(100, 5),
    "processed_data": DataFrame(100, 5),
    "metadata": {...},
    ...
}

# After Anomaly Handler
state = {
    "processed_data": DataFrame(95, 5),  # 5 rows removed
    "anomalies_detected": [3 patterns],
    ...
}

# After Null Handler
state = {
    "processed_data": DataFrame(95, 5),  # nulls filled
    "null_values_info": {2 columns},
    ...
}

# After Feature Processor
state = {
    "processed_data": DataFrame(95, 12),  # 7 new features
    ...
}

# After Validator
state = {
    "validation_passed": True,
    "workflow_status": "completed",
    ...
}
```

---

## 🎯 Design Principles

### 1. Determinism
- All agents use deterministic algorithms
- Same input → Same output
- No randomness in processing

### 2. Immutability
- Original `raw_data` never modified
- All operations on `processed_data`
- Audit trail preserved

### 3. Transparency
- Every step logged
- All decisions recorded
- Complete feedback trail

### 4. Modularity
- Each agent has single responsibility
- Agents are independent
- Easy to add/modify agents

### 5. Robustness
- Comprehensive error handling
- Validation at each step
- Graceful degradation

---

## 🔧 Extension Points

### Adding New Agents

1. Create node file in `nodes/`
2. Define function signature:
   ```python
   def my_agent_node(state: PreprocessingState) -> PreprocessingState:
       # Process state
       return state
   ```
3. Add to workflow:
   ```python
   workflow.add_node("my_agent", my_agent_node)
   workflow.add_edge("previous_agent", "my_agent")
   ```

### Custom Strategies

Extend handler nodes:
```python
if strategy == "custom":
    # Implement custom logic
    pass
```

### Custom Validation Rules

Extend validator node:
```python
# Add custom checks
if custom_condition:
    validation_errors.append("Custom error")
```

---

## 📈 Performance Characteristics

### Time Complexity
- Data Loading: O(n)
- Anomaly Detection: O(n * m) where m = columns
- Null Handling: O(n * m)
- Feature Processing: O(n * m)
- Validation: O(n * m)

**Overall**: O(n * m) per iteration

### Space Complexity
- O(n * m) for data storage
- O(k) for anomaly tracking
- O(m) for null info

**Overall**: O(n * m)

### Scalability
- Suitable for datasets: 10 - 10M rows
- Memory-bound by pandas DataFrame
- Can process multi-GB files

---

## 🛡️ Error Handling

### Error Propagation

```python
try:
    # Agent logic
except Exception as e:
    state["workflow_status"] = "error"
    state["validation_errors"].append(str(e))
    return state
```

### Validation Errors

Non-fatal errors that allow retry:
- Remaining null values
- Insufficient data
- Zero variance features

### Fatal Errors

Errors that stop workflow:
- File not found
- Unsupported format
- Empty DataFrame

---

## 📝 Audit Trail

### Tracking

Every operation logged in:
1. `preprocessing_steps` - Human-readable steps
2. `feedback_messages` - Agent communication
3. `metadata` - Structural changes

### Example Audit Log

```python
preprocessing_steps = [
    "Loaded data from ./data/file.csv",
    "Detected 3 anomaly patterns",
    "Handled 3 anomaly patterns using 'cap' strategy",
    "Detected null values in 2 columns (total: 15)",
    "Handled null values in 2 columns using 'smart' strategy",
    "Processed features: 5 transformations applied",
    "Validation passed with 1 warnings"
]
```

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2026-03-02
