# Data Science Agent - Project Overview

## 📁 Repository Structure

This repository contains **two implementations** of a multi-agent data science preprocessing system:

### 1. **Original Implementation** (Main Branch)
Located in root directory - Traditional multi-agent system with async communication

### 2. **LangGraph Implementation** (Langgraph_agents Branch) ⭐ NEW
Located in `langgraph_agents/` - Modern LangGraph-based deterministic agent system

---

## 🌿 Branch: `Langgraph_agents`

### Overview
A comprehensive, production-ready data preprocessing system built with **LangGraph** that uses deterministic agents to handle:
- ✅ Data loading from multiple formats
- ✅ Anomaly detection and handling
- ✅ Null value detection and imputation
- ✅ Feature engineering and encoding
- ✅ Data validation for ML readiness
- ✅ Intelligent feedback loops and retry mechanisms

### Key Features

#### 🤖 Deterministic Agents
1. **Data Loader Agent** - Loads CSV, Excel, JSON, Parquet files
2. **Anomaly Detector Agent** - IQR, Z-score, rare category detection
3. **Anomaly Handler Agent** - Cap, remove, transform, flag strategies
4. **Null Detector Agent** - Comprehensive null value analysis
5. **Null Handler Agent** - Smart imputation strategies
6. **Feature Processor Agent** - Encoding, scaling, duplicate removal
7. **Validator Agent** - ML-readiness validation
8. **Retry Decision Agent** - Feedback loop management

#### 🔄 Workflow Architecture
```
Load Data → Detect Anomalies → Handle Anomalies → Detect Nulls 
  → Handle Nulls → Process Features → Validate → Retry/End
```

#### 💬 Agent Communication
- Agents send feedback messages to each other
- State is shared across all agents
- Conditional routing based on data quality
- Automatic retry with strategy adjustment

### Directory Structure

```
langgraph_agents/
├── __init__.py
├── state.py                      # Shared state schema
├── workflow.py                   # LangGraph workflow definition
├── orchestrator.py               # Main orchestrator class
├── config.py                     # Configuration settings
├── README.md                     # Detailed documentation
├── nodes/                        # Agent implementations
│   ├── data_loader_node.py
│   ├── anomaly_detector_node.py
│   ├── anomaly_handler_node.py
│   ├── null_handler_node.py
│   ├── feature_processor_node.py
│   └── validator_node.py
├── test_langgraph_workflow.py    # Comprehensive tests
└── example_usage.py              # Usage examples
```

### Quick Start

```bash
# Switch to the LangGraph branch
git checkout Langgraph_agents

# Install dependencies
pip install -r requirements.txt

# Run basic preprocessing
python langgraph_main.py --input data.csv --output processed.csv

# Run with custom strategies
python langgraph_main.py --input data.csv --output processed.csv \
    --anomaly-strategy flag --null-strategy median --verbose

# Run tests
python langgraph_agents/test_langgraph_workflow.py

# Run examples
python langgraph_agents/example_usage.py
```

### Python API Usage

```python
from langgraph_agents.orchestrator import DataPreprocessingOrchestrator

# Create orchestrator
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
    print("✓ Preprocessing successful!")
    orchestrator.save_processed_data("./output/processed.csv")
    
    # Get workflow summary
    summary = orchestrator.get_workflow_summary()
    print(f"Iterations: {summary['iterations_used']}")
    print(f"Final shape: {summary['final_shape']}")
else:
    print("✗ Preprocessing failed")
    print(f"Errors: {result['validation_errors']}")
```

### Preprocessing Strategies

#### Anomaly Handling
- **cap**: Cap outliers at IQR bounds
- **remove**: Remove outlier rows
- **transform**: Log transformation
- **flag**: Create anomaly indicator columns
- **group**: Group rare categories

#### Null Handling
- **smart**: Adaptive (drops >50% null cols, uses median/mean/mode)
- **mean**: Fill with column mean
- **median**: Fill with column median
- **mode**: Fill with most frequent value
- **drop_rows**: Remove rows with nulls
- **drop_columns**: Remove columns with nulls
- **forward_fill**: Propagate last valid value
- **backward_fill**: Propagate next valid value

### Testing

The system includes comprehensive tests:

1. **Basic Workflow Test** - Default settings
2. **Strategy Comparison Test** - Different strategies
3. **Feedback Loop Test** - Retry mechanism
4. **Visualization Test** - Workflow graph
5. **Edge Cases Test** - Error handling

### Documentation

- **`langgraph_agents/README.md`** - Complete system documentation
- **`LANGGRAPH_SETUP.md`** - Setup and usage guide
- **`PROJECT_OVERVIEW.md`** - This file

### Advantages Over Original Implementation

| Feature | Original | LangGraph |
|---------|----------|-----------|
| State Management | Manual | Built-in TypedDict |
| Workflow Definition | Imperative | Declarative Graph |
| Conditional Routing | Manual | Graph Edges |
| Feedback Loops | Custom | Native Support |
| Retry Logic | Manual | Integrated |
| Visualization | None | Built-in |
| Testing | Basic | Comprehensive |
| Type Safety | Partial | Full Pydantic |

---

## 🌿 Branch: `main`

### Original Implementation
Traditional multi-agent system with:
- Detection Agent
- Loading Agent  
- Processing Agent
- Communication Hub
- Async message passing

Located in:
- `agents/` directory
- `main_orchestrator.py`
- `test_mas.py`

---

## 🚀 Getting Started

### For New Users - Use LangGraph Implementation

```bash
# Clone repository
git clone <repo-url>
cd DataScienceAgent

# Switch to LangGraph branch
git checkout Langgraph_agents

# Install dependencies
pip install -r requirements.txt

# Run example
python langgraph_agents/example_usage.py
```

### For Existing Users - Migrate to LangGraph

The LangGraph implementation provides:
- Better structure and maintainability
- More robust error handling
- Comprehensive testing
- Full documentation
- Production-ready code

---

## 📊 Supported Data Formats

Both implementations support:
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)
- JSON (`.json`)
- Parquet (`.parquet`)

---

## 🔧 Dependencies

Core requirements:
- Python 3.8+
- LangGraph 0.0.48+
- LangChain 0.1.16+
- Pandas 2.2.2+
- NumPy 1.26.4+
- Scikit-learn 1.4.1+
- Pydantic 2.6.4+

See `requirements.txt` for complete list.

---

## 📈 Use Cases

1. **Data Cleaning** - Automated preprocessing pipeline
2. **ML Preparation** - Get data ready for model training
3. **Data Quality** - Detect and fix data issues
4. **ETL Pipelines** - Integrate into data workflows
5. **Research** - Reproducible preprocessing

---

## 🎯 Roadmap

### Completed ✅
- LangGraph-based agent system
- Deterministic preprocessing agents
- Anomaly detection and handling
- Null value handling
- Feature engineering
- Validation and retry logic
- Comprehensive testing
- Full documentation

### Future Enhancements 🔮
- Additional preprocessing strategies
- Custom agent plugins
- Distributed processing
- Real-time monitoring dashboard
- Integration with ML frameworks
- Cloud deployment support

---

## 📝 Contributing

When contributing:
1. Work on the `Langgraph_agents` branch for new features
2. Follow existing code structure
3. Add tests for new functionality
4. Update documentation
5. Ensure deterministic behavior

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Authors

Data Science Team

---

## 📞 Support

For questions or issues:
1. Check `LANGGRAPH_SETUP.md` for setup help
2. Review `langgraph_agents/README.md` for API docs
3. Run tests to verify installation
4. Check example usage files

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-02  
**Branch**: Langgraph_agents
