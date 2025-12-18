# Technical Stack

## Language & Runtime

- Python 3.12+
- Type hints with mypy strict mode

## Core Dependencies

### Graph & Data Processing
- `networkx>=3.0` - Graph data structure and algorithms
- `pandas>=2.0` - CSV parsing and data manipulation
- Built-in `json` module - JSON parsing and manipulation

### AI & Semantic Analysis
- `google-genai>=0.1.0` - Gemini API for semantic parameter matching
- `python-dotenv>=1.0.0` - Environment variable management for API keys

### Visualization
- `plotly>=5.0` or `pyvis` - Interactive HTML graph visualizations
- `matplotlib` - Static graph image generation

### Testing
- `pytest>=7.0` - Unit and integration testing
- `hypothesis>=6.0` - Property-based testing (minimum 100 iterations per test)

## Project Structure

```
api-graph-builder/
├── data/                    # CSV files with API documentation
│   ├── fms.csv             # Fleet Management System APIs
│   ├── hq.csv              # HQ system APIs
│   ├── hrms.csv            # HR Management System APIs
│   └── wms.csv             # Warehouse Management System APIs
├── .kiro/
│   ├── specs/              # Feature specifications
│   └── steering/           # Project guidelines (this file)
├── src/                    # Source code (to be created)
├── tests/                  # Test suite (to be created)
└── README.md
```

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run property-based tests only
pytest -m property

# Run type checking
mypy src/ --strict
```

### Usage
```bash
# Parse CSV files and build graph
python -m src.main --input data/*.csv --output graph.json

# Export to different formats
python -m src.main --input data/*.csv --export graphml --output graph.graphml
python -m src.main --input data/*.csv --export neo4j --output graph.cypher

# Generate visualization
python -m src.main --input data/*.csv --visualize --output graph.html
```

## Configuration

### Environment Variables
- `GEMINI_API_KEY` - Required for semantic parameter matching (optional feature)

Store in `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

## Code Quality Standards

- All code must have type hints
- Minimum 80% test coverage
- All property-based tests must run 100+ iterations
- Use dataclasses for data models
- Follow PEP 8 style guidelines
- Document all public APIs with docstrings
