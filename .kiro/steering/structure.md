# Project Structure & Organization

## Directory Layout

```
api-graph-builder/
├── data/                           # Input CSV files (not in version control)
│   ├── fms.csv                    # Fleet Management System API docs
│   ├── hq.csv                     # HQ system API docs
│   ├── hrms.csv                   # HR Management System API docs
│   └── wms.csv                    # Warehouse Management System API docs
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── models.py                  # Data models (APIRecord, GraphNode, etc.)
│   ├── csv_parser.py              # CSVParser class
│   ├── json_extractor.py          # JSONExtractor class
│   ├── graph_builder.py           # GraphBuilder class
│   ├── flow_detector.py           # FlowDetector class
│   ├── semantic_matcher.py        # SemanticMatcher class (Gemini integration)
│   ├── export_engine.py           # ExportEngine class
│   └── visualizer.py              # Visualizer class
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_csv_parser.py         # Unit tests for CSV parsing
│   ├── test_json_extractor.py     # Unit tests for JSON extraction
│   ├── test_graph_builder.py      # Unit tests for graph construction
│   ├── test_flow_detector.py      # Unit tests for flow detection
│   ├── test_semantic_matcher.py   # Unit tests for semantic matching
│   ├── test_export_engine.py      # Unit tests for export functionality
│   ├── test_visualizer.py         # Unit tests for visualization
│   ├── test_integration.py        # End-to-end integration tests
│   └── test_properties.py         # Property-based tests (Hypothesis)
│
├── .kiro/                         # Kiro configuration
│   ├── specs/                     # Feature specifications
│   │   └── api-graph-converter/
│   │       ├── requirements.md    # Requirements document
│   │       └── design.md          # Design document
│   └── steering/                  # Project guidelines
│       ├── product.md             # Product overview
│       ├── tech.md                # Tech stack & commands
│       └── structure.md           # This file
│
├── .gitignore                     # Git ignore patterns
├── LICENSE                        # Project license
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies (to be created)
└── .env.example                   # Example environment variables
```

## Module Organization

### Core Modules

Each module follows single responsibility principle:

- **models.py**: Dataclass definitions only, no logic
- **csv_parser.py**: File I/O and CSV parsing, returns structured data
- **json_extractor.py**: JSON parsing and key extraction, pure functions
- **graph_builder.py**: Graph construction, uses NetworkX
- **flow_detector.py**: Parameter matching and flow detection
- **semantic_matcher.py**: Gemini API integration for semantic analysis
- **export_engine.py**: Format conversion and file export
- **visualizer.py**: Graph visualization generation

### Data Flow

```
CSV Files → CSVParser → APIRecord[]
                           ↓
                    JSONExtractor (extract keys)
                           ↓
                    GraphBuilder → NetworkX Graph
                           ↓
                    FlowDetector (add potential_flow edges)
                           ↓
                    SemanticMatcher (add semantic_flow edges)
                           ↓
                    ┌──────┴──────┐
                    ↓             ↓
              ExportEngine    Visualizer
```

## Naming Conventions

### Files
- Snake case: `csv_parser.py`, `flow_detector.py`
- Test files: `test_<module_name>.py`

### Classes
- PascalCase: `CSVParser`, `GraphBuilder`, `FlowDetector`
- One class per file (except models.py)

### Functions/Methods
- Snake case: `parse_file()`, `extract_keys()`, `detect_flows()`
- Private methods: `_internal_helper()`

### Variables
- Snake case: `tool_name`, `api_endpoint`, `confidence_score`
- Constants: `MAX_BATCH_SIZE`, `DEFAULT_CONFIDENCE_THRESHOLD`

### Node IDs
- Tool nodes: `{csv_filename}.{tool_name}` (e.g., `fms.get_all_transporters`)
- Parameter nodes: Use parameter name directly (e.g., `waybill_number`)

### Edge Types
- `requires_input` - Tool → Input Parameter
- `produces_output` - Tool → Output Parameter
- `potential_flow` - Tool → Tool (via matching parameters)
- `semantic_flow` - Tool → Tool (via AI-detected semantic match)

## CSV File Format

Expected columns in input CSV files:
- `tool_name` (required) - API operation name
- `api_endpoint` (required) - API URL
- `input_payload` (required) - JSON string of input parameters
- `output_response` (required) - JSON string of output data
- `status_code` (optional) - HTTP status code
- `success` (optional) - Boolean success flag
- `curl_command` (optional) - Example curl command
- `timestamp` (optional) - When the API was documented

## Git Ignore Patterns

The `.gitignore` file excludes:
- CSV data files (`*.csv` in data/)
- Python cache (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `.venv/`)
- Test coverage reports (`htmlcov/`, `.coverage`)
- Environment files (`.env`)
- Generated outputs (`*.graphml`, `*.json`, `*.html`, `*.cypher`)

## Import Organization

Follow this import order in all Python files:
1. Standard library imports
2. Third-party imports (networkx, pandas, etc.)
3. Local application imports

Example:
```python
import json
from typing import List, Dict, Any
from dataclasses import dataclass

import networkx as nx
import pandas as pd

from .models import APIRecord, GraphNode
from .json_extractor import JSONExtractor
```
