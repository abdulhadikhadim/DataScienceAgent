# LangGraph Agents Setup Guide

## 📋 Overview

This document provides setup and usage instructions for the LangGraph-based data preprocessing agent system.

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

The system requires:
- `langgraph>=0.0.48` - For workflow orchestration
- `langchain>=0.1.16` - For agent framework
- `pandas>=2.2.2` - For data manipulation
- `numpy>=1.26.4` - For numerical operations
- `scikit-learn>=1.4.1` - For preprocessing utilities
- `pydantic>=2.6.4` - For state validation

## 🚀 Quick Start

### 1. Basic Preprocessing

```python
from langgraph_agents.orchestrator import DataPreprocessingOrchestrator

# Create orchestrator
orchestrator = DataPreprocessingOrchestrator()

# Run preprocessing
result = orchestrator.preprocess_data(
    data_source="./input_data/my_data.csv"
)

# Save results
if result['success']:
    orchestrator.save_processed_data("./data/output.csv")
```

### 2. Custom Strategies

```python
result = orchestrator.preprocess_data(
    data_source="./input_data/my_data.csv",
    anomaly_strategy="flag",      # Options: cap, remove, transform, flag, group
    null_strategy="median",        # Options: smart, mean, median, mode, drop_rows, etc.
    max_iterations=5               # Maximum retry attempts
)
```

### 3. Analyze Results

```python
# Get workflow summary
summary = orchestrator.get_workflow_summary()
print(f"Status: {summary['workflow_status']}")
print(f"Iterations: {summary['iterations_used']}")

# Get feedback log
feedback = orchestrator.get_feedback_log()
for msg in feedback:
    print(f"{msg['from_agent']} → {msg['to_agent']}: {msg['message']}")

# Get preprocessing steps
for step in result['preprocessing_steps']:
    print(f"✓ {step}")
```

## 📊 Supported Data Formats

- **CSV** (`.csv`)
- **Excel** (`.xlsx`, `.xls`)
- **JSON** (`.json`)
- **Parquet** (`.parquet`)

## 🎯 Preprocessing Strategies

### Anomaly Handling

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `cap` | Cap outliers at IQR bounds | Preserve data volume |
| `remove` | Remove outlier rows | Clean dataset |
| `transform` | Log transformation | Reduce skewness |
| `flag` | Create anomaly flags | Keep all data, mark outliers |
| `group` | Group rare categories | Categorical data |

### Null Value Handling

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `smart` | Adaptive based on data type | General purpose |
| `mean` | Fill with column mean | Numeric, normal distribution |
| `median` | Fill with column median | Numeric, skewed distribution |
| `mode` | Fill with most frequent | Categorical data |
| `drop_rows` | Remove rows with nulls | Small null percentage |
| `drop_columns` | Remove columns with nulls | High null percentage |
| `forward_fill` | Propagate last valid value | Time series |
| `backward_fill` | Propagate next valid value | Time series |

## 🔄 Workflow Execution Flow

```
1. Data Loader
   ↓
2. Anomaly Detector
   ↓
3. Anomaly Handler (if anomalies found)
   ↓
4. Null Detector
   ↓
5. Null Handler (if nulls found)
   ↓
6. Feature Processor
   ↓
7. Validator
   ↓
8. Retry Decision (if validation fails)
   ↓ (loop back to step 2)
9. End
```

## 🧪 Testing

### Run All Tests

```bash
python langgraph_agents/test_langgraph_workflow.py
```

### Run Examples

```bash
python langgraph_agents/example_usage.py
```

### Test Individual Components

```python
from langgraph_agents.nodes.anomaly_detector_node import detect_anomalies_node
from langgraph_agents.state import PreprocessingState
import pandas as pd

# Create test state
state = {
    "processed_data": pd.read_csv("test.csv"),
    "anomalies_detected": [],
    # ... other required fields
}

# Test anomaly detection
result_state = detect_anomalies_node(state)
print(f"Anomalies found: {len(result_state['anomalies_detected'])}")
```

## 📁 Project Structure

```
langgraph_agents/
├── __init__.py                    # Package initialization
├── state.py                       # State schema
├── workflow.py                    # LangGraph workflow
├── orchestrator.py                # Main orchestrator
├── config.py                      # Configuration
├── README.md                      # Documentation
├── nodes/                         # Agent nodes
│   ├── data_loader_node.py
│   ├── anomaly_detector_node.py
│   ├── anomaly_handler_node.py
│   ├── null_handler_node.py
│   ├── feature_processor_node.py
│   └── validator_node.py
├── test_langgraph_workflow.py     # Tests
└── example_usage.py               # Examples
```

## 🔍 Debugging

### Enable Verbose Output

```python
result = orchestrator.preprocess_data(
    data_source="./data/data.csv"
)

# Print all preprocessing steps
print("\nPreprocessing Steps:")
for i, step in enumerate(result['preprocessing_steps'], 1):
    print(f"{i}. {step}")

# Print anomalies
print("\nAnomalies Detected:")
for anomaly in result['anomalies_detected']:
    print(f"  Column: {anomaly['column']}")
    print(f"  Method: {anomaly['method']}")
    print(f"  Count: {anomaly['count']}")

# Print validation errors
if result['validation_errors']:
    print("\nValidation Errors:")
    for error in result['validation_errors']:
        print(f"  ✗ {error}")
```

### Visualize Workflow

```python
orchestrator = DataPreprocessingOrchestrator()
print(orchestrator.visualize_workflow())
```

## ⚙️ Configuration

### Default Settings

```python
from langgraph_agents.config import LangGraphConfig

# View default settings
print(f"Default anomaly strategy: {LangGraphConfig.DEFAULT_ANOMALY_STRATEGY}")
print(f"Default null strategy: {LangGraphConfig.DEFAULT_NULL_STRATEGY}")
print(f"IQR multiplier: {LangGraphConfig.IQR_MULTIPLIER}")
print(f"Z-score threshold: {LangGraphConfig.Z_SCORE_THRESHOLD}")
```

### Custom Configuration

Modify `config.py` to adjust:
- Detection thresholds
- Strategy defaults
- Validation rules
- Output formats

## 🎓 Advanced Usage

### Access Intermediate States

```python
from langgraph_agents.workflow import create_preprocessing_workflow

workflow = create_preprocessing_workflow()

# Execute with custom state
initial_state = {
    "data_source": "./data/data.csv",
    "anomaly_handling_strategy": "cap",
    # ... other fields
}

final_state = workflow.invoke(initial_state)

# Access any state field
print(f"Anomalies: {final_state['anomalies_detected']}")
print(f"Null info: {final_state['null_values_info']}")
print(f"Metadata: {final_state['metadata']}")
```

### Custom Node Development

```python
from langgraph_agents.state import PreprocessingState

def custom_preprocessing_node(state: PreprocessingState) -> PreprocessingState:
    """
    Custom preprocessing logic.
    """
    df = state.get("processed_data")
    
    # Your custom logic here
    # ...
    
    state["processed_data"] = df
    state["preprocessing_steps"].append("Custom preprocessing applied")
    
    return state
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'langgraph'`
```bash
pip install langgraph>=0.0.48
```

**Issue**: `File not found` error
```python
# Ensure file path is correct
from pathlib import Path
file_path = Path("./input_data/data.csv")
print(f"File exists: {file_path.exists()}")
```

**Issue**: Validation always fails
```python
# Check validation errors
result = orchestrator.preprocess_data("./data/data.csv")
print("Validation errors:", result['validation_errors'])

# Increase max iterations
result = orchestrator.preprocess_data(
    data_source="./data/data.csv",
    max_iterations=5
)
```

## 📈 Performance Tips

1. **Large Datasets**: Process in chunks if memory is limited
2. **Multiple Files**: Reuse orchestrator instance
3. **Custom Strategies**: Implement domain-specific logic in handler nodes
4. **Monitoring**: Use feedback messages to track progress

## 🤝 Integration Examples

### With Scikit-learn

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Preprocess data
orchestrator = DataPreprocessingOrchestrator()
result = orchestrator.preprocess_data("./data/data.csv")

if result['success']:
    df = result['processed_data']
    
    # Prepare for ML
    X = df.drop('target', axis=1)
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
```

### With Pandas Pipeline

```python
import pandas as pd

# Load and preprocess
orchestrator = DataPreprocessingOrchestrator()
result = orchestrator.preprocess_data("./data/data.csv")

# Continue with pandas operations
df = result['processed_data']
df_grouped = df.groupby('category').agg({'value': 'mean'})
```

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review example usage in `example_usage.py`
3. Run tests to verify setup: `test_langgraph_workflow.py`

---

**Happy Preprocessing! 🚀**
