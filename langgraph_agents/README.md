# LangGraph Data Preprocessing Agent System

A comprehensive, deterministic multi-agent system built with LangGraph for automated data preprocessing and preparation for machine learning models.

## 🎯 Overview

This system implements a sophisticated data preprocessing pipeline using LangGraph's state machine architecture. Multiple specialized agents work together to handle various data quality issues including anomalies, null values, feature engineering, and validation.

## 🏗️ Architecture

### Agent Workflow

```
[Data Loader] → [Anomaly Detector] → [Anomaly Handler] → [Null Detector] 
    → [Null Handler] → [Feature Processor] → [Validator] → [END/Retry]
```

### Deterministic Agents

1. **Data Loader Agent**
   - Loads data from multiple formats (CSV, Excel, JSON, Parquet)
   - Validates file existence and format
   - Initializes metadata tracking

2. **Anomaly Detector Agent**
   - Detects outliers using IQR method
   - Identifies anomalies using Z-score (threshold: 3σ)
   - Finds rare categorical values (<1% frequency)
   - Deterministic and reproducible results

3. **Anomaly Handler Agent**
   - **Strategies**: cap, remove, transform, flag, group
   - Applies consistent handling based on selected strategy
   - Tracks all modifications

4. **Null Value Detector Agent**
   - Identifies missing values across all columns
   - Calculates null percentages
   - Categorizes by data type

5. **Null Value Handler Agent**
   - **Strategies**: smart, drop_rows, drop_columns, mean, median, mode, forward_fill, backward_fill
   - Smart strategy: Adaptive based on null percentage and data type
   - Deterministic imputation methods

6. **Feature Processor Agent**
   - Removes duplicate rows
   - Encodes categorical variables (binary, one-hot, label encoding)
   - Standardizes numerical features
   - Creates derived features

7. **Validator Agent**
   - Checks for remaining null values
   - Validates no infinite values
   - Ensures sufficient data volume
   - Verifies feature variance
   - Confirms ML-readiness

8. **Retry Decision Agent**
   - Implements feedback loop
   - Adjusts strategies on validation failure
   - Limits iterations to prevent infinite loops

## 📊 State Management

The system uses a shared `PreprocessingState` that flows through all agents:

```python
{
    "raw_data": pd.DataFrame,           # Original data
    "processed_data": pd.DataFrame,     # Current processed data
    "anomalies_detected": List[Dict],   # Detected anomalies
    "null_values_info": Dict,           # Null value information
    "preprocessing_steps": List[str],   # Audit trail
    "validation_passed": bool,          # Validation status
    "feedback_messages": List[Dict],    # Agent communication
    "iteration_count": int,             # Retry counter
    # ... more fields
}
```

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from langgraph_agents.orchestrator import DataPreprocessingOrchestrator

# Initialize orchestrator
orchestrator = DataPreprocessingOrchestrator()

# Preprocess data
result = orchestrator.preprocess_data(
    data_source="./data/my_data.csv",
    anomaly_strategy="cap",
    null_strategy="smart",
    max_iterations=3
)

# Check results
if result['success']:
    print("Preprocessing successful!")
    orchestrator.save_processed_data("./output/processed.csv")
else:
    print("Errors:", result['validation_errors'])
```

## 🔧 Configuration Options

### Anomaly Handling Strategies

- **cap**: Cap outliers at bounds (IQR-based)
- **remove**: Remove rows with outliers
- **transform**: Apply log transformation
- **flag**: Create binary flag columns
- **group**: Group rare categories as "Other"

### Null Handling Strategies

- **smart**: Adaptive strategy based on data characteristics
  - Drops columns with >50% nulls
  - Uses median for skewed numeric data
  - Uses mean for normal numeric data
  - Uses mode for categorical data
- **drop_rows**: Remove rows with null values
- **drop_columns**: Remove columns with null values
- **mean**: Fill with column mean
- **median**: Fill with column median
- **mode**: Fill with column mode
- **forward_fill**: Forward fill missing values
- **backward_fill**: Backward fill missing values

## 📁 Directory Structure

```
langgraph_agents/
├── __init__.py
├── state.py                    # State schema definition
├── workflow.py                 # LangGraph workflow definition
├── orchestrator.py             # Main orchestrator class
├── nodes/
│   ├── __init__.py
│   ├── data_loader_node.py     # Data loading agent
│   ├── anomaly_detector_node.py # Anomaly detection agent
│   ├── anomaly_handler_node.py  # Anomaly handling agent
│   ├── null_handler_node.py     # Null value handling agent
│   ├── feature_processor_node.py # Feature engineering agent
│   └── validator_node.py        # Validation agent
├── test_langgraph_workflow.py  # Comprehensive tests
├── example_usage.py            # Usage examples
└── README.md                   # This file
```

## 🧪 Testing

Run comprehensive tests:

```bash
python langgraph_agents/test_langgraph_workflow.py
```

Run example usage:

```bash
python langgraph_agents/example_usage.py
```

## 🔄 Feedback Loop Mechanism

The system implements intelligent feedback loops:

1. **Agent Communication**: Agents send feedback messages to downstream agents
2. **Validation Retry**: Failed validation triggers strategy adjustment
3. **Iteration Limiting**: Maximum iterations prevent infinite loops
4. **Strategy Adaptation**: Strategies change on retry (e.g., cap → flag)

Example feedback flow:
```
Data Loader → "Data loaded with shape (100, 5)"
Anomaly Detector → "Found 3 anomaly patterns"
Anomaly Handler → "Handled using cap strategy"
Validator → "Validation failed - retrying with different strategy"
Retry Decision → "Switching to flag strategy"
```

## 📈 Features

### ✅ Deterministic Processing
- All agents use deterministic algorithms
- Reproducible results with same input
- No randomness in decision-making

### ✅ Comprehensive Anomaly Detection
- Statistical methods (IQR, Z-score)
- Categorical anomaly detection
- Multiple handling strategies

### ✅ Intelligent Null Handling
- Adaptive strategies based on data type
- Percentage-based decisions
- Multiple imputation methods

### ✅ Feature Engineering
- Automatic encoding of categorical variables
- Feature scaling and normalization
- Duplicate removal

### ✅ Validation & Quality Checks
- ML-readiness validation
- Data quality metrics
- Comprehensive error reporting

### ✅ Audit Trail
- Complete preprocessing history
- Agent communication logs
- Feedback message tracking

## 🎓 Advanced Usage

### Custom Workflow Execution

```python
from langgraph_agents.workflow import create_preprocessing_workflow

# Create custom workflow
workflow = create_preprocessing_workflow()

# Define initial state
initial_state = {
    "data_source": "./data/custom.csv",
    "anomaly_handling_strategy": "transform",
    "null_handling_strategy": "median",
    # ... other state fields
}

# Execute workflow
final_state = workflow.invoke(initial_state)
```

### Analyzing Agent Communication

```python
orchestrator = DataPreprocessingOrchestrator()
result = orchestrator.preprocess_data("./data/data.csv")

# Get feedback log
feedback_log = orchestrator.get_feedback_log()

for message in feedback_log:
    print(f"{message['from_agent']} → {message['to_agent']}")
    print(f"Message: {message['message']}")
```

### Workflow Summary

```python
summary = orchestrator.get_workflow_summary()
print(f"Status: {summary['workflow_status']}")
print(f"Iterations: {summary['iterations_used']}")
print(f"Final Shape: {summary['final_shape']}")
```

## 🔍 Monitoring & Debugging

### Preprocessing Steps Audit

```python
result = orchestrator.preprocess_data("./data/data.csv")

for step in result['preprocessing_steps']:
    print(f"✓ {step}")
```

### Anomaly Analysis

```python
for anomaly in result['anomalies_detected']:
    print(f"Column: {anomaly['column']}")
    print(f"Method: {anomaly['method']}")
    print(f"Count: {anomaly['count']}")
    print(f"Sample values: {anomaly['values']}")
```

## 🛠️ Extending the System

### Adding New Agents

1. Create a new node file in `nodes/`
2. Define the agent function with `PreprocessingState` parameter
3. Add the node to the workflow in `workflow.py`
4. Update conditional edges if needed

### Custom Preprocessing Strategies

Modify the handler nodes to include custom strategies:

```python
def handle_anomalies_node(state: PreprocessingState) -> PreprocessingState:
    strategy = state.get("anomaly_handling_strategy")
    
    if strategy == "custom_strategy":
        # Implement custom logic
        pass
```

## 📊 Performance Considerations

- **Memory**: Processes data in-memory using pandas
- **Scalability**: Suitable for datasets up to several GB
- **Speed**: Deterministic algorithms ensure fast processing
- **Parallelization**: Sequential agent execution (can be parallelized for independent operations)

## 🤝 Contributing

This is a production-ready system for data preprocessing. Contributions welcome for:
- Additional preprocessing strategies
- New agent types
- Performance optimizations
- Extended validation rules

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- LangGraph for workflow orchestration
- Pandas for data manipulation
- Scikit-learn for preprocessing utilities
- NumPy for numerical operations

---

**Version**: 1.0.0  
**Author**: Data Science Team  
**Last Updated**: 2026-03-02
