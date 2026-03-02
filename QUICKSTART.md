# 🚀 Quick Start Guide - LangGraph Data Preprocessing Agents

## ⚡ 5-Minute Setup

### 1. Switch to the LangGraph Branch
```bash
git checkout Langgraph_agents
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Your First Preprocessing
```bash
python langgraph_main.py --input ./input_data/sample_data.csv --output ./data/processed.csv --verbose
```

---

## 📝 Basic Usage

### Command Line
```bash
# Simple preprocessing
python langgraph_main.py -i data.csv -o output.csv

# With custom strategies
python langgraph_main.py -i data.csv -o output.csv \
    --anomaly-strategy flag \
    --null-strategy median \
    --max-iterations 5

# Verbose output
python langgraph_main.py -i data.csv -o output.csv --verbose

# Different output format
python langgraph_main.py -i data.xlsx -o output.parquet --format parquet
```

### Python API
```python
from langgraph_agents.orchestrator import DataPreprocessingOrchestrator

# Create orchestrator
orchestrator = DataPreprocessingOrchestrator()

# Preprocess data
result = orchestrator.preprocess_data(
    data_source="./data/my_data.csv",
    anomaly_strategy="cap",      # cap, remove, transform, flag, group
    null_strategy="smart",        # smart, mean, median, mode, drop_rows, etc.
    max_iterations=3
)

# Check results
if result['success']:
    print("✓ Success!")
    orchestrator.save_processed_data("./output/processed.csv")
else:
    print("✗ Failed:", result['validation_errors'])
```

---

## 🧪 Run Tests

```bash
# Comprehensive test suite
python langgraph_agents/test_langgraph_workflow.py

# Usage examples
python langgraph_agents/example_usage.py
```

---

## 📊 Supported Formats

**Input/Output**: CSV, Excel, JSON, Parquet

---

## ⚙️ Available Strategies

### Anomaly Handling
- `cap` - Cap outliers at bounds (default)
- `remove` - Remove outlier rows
- `transform` - Log transformation
- `flag` - Create anomaly flags
- `group` - Group rare categories

### Null Handling
- `smart` - Adaptive strategy (default)
- `mean` - Fill with mean
- `median` - Fill with median
- `mode` - Fill with mode
- `drop_rows` - Remove rows
- `drop_columns` - Remove columns
- `forward_fill` - Forward propagation
- `backward_fill` - Backward propagation

---

## 📖 Documentation

- **`langgraph_agents/README.md`** - Complete documentation
- **`LANGGRAPH_SETUP.md`** - Detailed setup guide
- **`langgraph_agents/ARCHITECTURE.md`** - Architecture details
- **`PROJECT_OVERVIEW.md`** - Project overview
- **`IMPLEMENTATION_SUMMARY.md`** - Implementation summary

---

## 🎯 Common Tasks

### Preprocess for ML Training
```python
orchestrator = DataPreprocessingOrchestrator()
result = orchestrator.preprocess_data("train_data.csv")

if result['success']:
    df = result['processed_data']
    # Use df for model training
```

### Analyze Data Quality
```python
result = orchestrator.preprocess_data("data.csv")

print(f"Anomalies: {len(result['anomalies_detected'])}")
print(f"Null columns: {len(result['null_values_info'])}")
print(f"Steps taken: {result['preprocessing_steps']}")
```

### Get Workflow Summary
```python
orchestrator.preprocess_data("data.csv")
summary = orchestrator.get_workflow_summary()

print(f"Status: {summary['workflow_status']}")
print(f"Iterations: {summary['iterations_used']}")
print(f"Final shape: {summary['final_shape']}")
```

### View Agent Communication
```python
result = orchestrator.preprocess_data("data.csv")

for msg in result['feedback_messages']:
    print(f"{msg['from_agent']} → {msg['to_agent']}: {msg['message']}")
```

---

## 🔍 Troubleshooting

**Issue**: Module not found
```bash
pip install -r requirements.txt
```

**Issue**: File not found
```python
from pathlib import Path
print(Path("your_file.csv").exists())
```

**Issue**: Validation fails
```python
# Increase iterations
result = orchestrator.preprocess_data(
    data_source="data.csv",
    max_iterations=5
)
# Check errors
print(result['validation_errors'])
```

---

## 💡 Tips

1. **Start with defaults** - Use default strategies first
2. **Check verbose output** - Use `--verbose` flag to see details
3. **Review feedback** - Agent messages explain decisions
4. **Iterate strategies** - Try different strategies if validation fails
5. **Save intermediate results** - Save after each major step

---

## 🎓 Learn More

Run the examples to see the system in action:
```bash
python langgraph_agents/example_usage.py
```

View the workflow visualization:
```bash
python langgraph_main.py --show-workflow
```

---

**Ready to preprocess! 🚀**
