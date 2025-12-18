# API Graph Builder

A Python tool that automatically builds graph representations and GraphRAGs from API documentation stored in CSV format.

## Overview

API Graph Builder transforms CSV-based API documentation into queryable graph structures where:
- **Nodes** represent API tools and their JSON parameters
- **Edges** represent input/output relationships and data flows between APIs
- **Semantic analysis** (optional) identifies hidden connections using AI

## Features

- 📊 Parse CSV files containing API metadata (endpoints, payloads, responses)
- 🔍 Extract and flatten nested JSON structures from API inputs/outputs
- 🕸️ Build directed graphs showing API dependencies and parameter relationships
- 🔗 Detect potential API chains where one API's output feeds another's input
- 🤖 Use AI (Gemini) to find semantic relationships between parameters
- 💾 Export graphs in multiple formats (JSON, GraphML, DOT, Neo4j Cypher)
- 📈 Generate interactive visualizations for exploring API relationships

## Installation

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd api-graph-builder

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

Parse CSV files and build a graph:

```bash
python -m src.main --input data/fms.csv data/hq.csv --output graph.json
```

### With Flow Detection

Detect potential data flows between APIs:

```bash
python -m src.main \
  --input data/*.csv \
  --output graph.json \
  --detect-flows
```

### Export to Different Formats

```bash
# Export as GraphML (for Gephi, Cytoscape)
python -m src.main --input data/*.csv --export graphml --output graph.graphml

# Export as DOT (for Graphviz)
python -m src.main --input data/*.csv --export dot --output graph.dot

# Export as Neo4j Cypher statements
python -m src.main --input data/*.csv --export neo4j --output graph.cypher
```

### Command Line Options

```
--input, -i          Input CSV file(s) (required)
--output, -o         Output file path (default: graph.json)
--export, -e         Export format: json, graphml, dot, neo4j (default: json)
--detect-flows       Enable flow detection between APIs
--fuzzy-threshold    Fuzzy matching threshold 0.0-1.0 (default: 0.8)
--verbose, -v        Enable verbose logging
```

## CSV File Format

Input CSV files should contain the following columns:

### Required Columns
- `tool_name` - API operation name
- `api_endpoint` - API URL
- `input_payload` - JSON string of input parameters
- `output_response` - JSON string of output data

### Optional Columns
- `status_code` - HTTP status code
- `success` - Boolean success flag
- `curl_command` - Example curl command
- `timestamp` - When the API was documented

### Example CSV

```csv
tool_name,api_endpoint,input_payload,output_response,status_code
get_user,/api/users,"{""user_id"": 1}","{""name"": ""John"", ""email"": ""john@example.com""}",200
send_email,/api/email,"{""email"": ""test@example.com"", ""subject"": ""Test""}","{""message_id"": ""123""}",200
create_order,/api/orders,"{""user_id"": 1, ""product_id"": 42}","{""order_id"": ""ORD-001"", ""status"": ""pending""}",201
```

## Graph Structure

### Node Types

1. **Tool Nodes** - Represent API operations
   - ID format: `{csv_filename}.{tool_name}`
   - Example: `fms.get_all_transporters`

2. **Parameter Nodes** - Represent JSON keys from inputs/outputs
   - ID format: parameter name (e.g., `user_id`, `email`)
   - Nested keys use dot notation: `user.address.city`
   - Array elements use brackets: `items[0].id`

### Edge Types

1. **requires_input** - Tool → Input Parameter
2. **produces_output** - Tool → Output Parameter
3. **potential_flow** - Tool → Tool (via matching parameters)
4. **semantic_flow** - Tool → Tool (via AI-detected semantic match)

## Visualization

### Generate Interactive Visualizations

Create an interactive HTML visualization with zoom, pan, and hover details:

```bash
# Full graph visualization (all nodes and edges)
python -m src.main \
  --input data/*.csv \
  --detect-flows \
  --visualize \
  --viz-output graph.html

# Flow-focused visualization (only API-to-API connections)
python -m src.main \
  --input data/*.csv \
  --detect-flows \
  --flow-viz \
  --viz-output flows.html
```

### Visualization Features

- **Interactive**: Zoom, pan, and hover over nodes for details
- **Color-coded nodes**:
  - 🔴 Red: API tools
  - 🔵 Teal: Input parameters
  - 🟢 Light teal: Output parameters
- **Directional arrows**: Show data flow direction
- **Edge types**:
  - Light blue: requires_input
  - Dark blue: produces_output
  - Red: potential_flow (API chains)
  - Orange: semantic_flow (AI-detected)

### Layout Options

```bash
# Spring layout (default, force-directed)
--viz-layout spring

# Circular layout
--viz-layout circular

# Kamada-Kawai layout (energy-based)
--viz-layout kamada_kawai
```

## Example Output

After processing your API documentation:

```
Graph statistics: X nodes, Y edges
- N tool nodes (API operations)
- M parameter nodes
- K potential flows detected
```

**Generated files:**
- `flows_pyvis.html` - Interactive flow visualization
- `graph.json` - Graph data in JSON format

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_json_extractor.py -v

# Run with verbose output
pytest -v
```

## Project Structure

```
api-graph-builder/
├── data/                    # CSV files with API documentation
├── src/                     # Source code
│   ├── models.py           # Data models
│   ├── csv_parser.py       # CSV parsing
│   ├── json_extractor.py   # JSON extraction
│   ├── graph_builder.py    # Graph construction
│   ├── flow_detector.py    # Flow detection
│   ├── export_engine.py    # Export functionality
│   └── main.py             # CLI entry point
├── tests/                   # Test suite
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Advanced Features

### Semantic Matching with Gemini AI

To enable AI-powered semantic parameter matching:

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Create a `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
```

3. Run with semantic analysis (feature coming soon):
```bash
python -m src.main --input data/*.csv --semantic-matching
```

### Neo4j Integration

Import the graph into Neo4j for advanced querying:

```bash
# Export to Cypher
python -m src.main --input data/*.csv --export neo4j --output graph.cypher

# Import into Neo4j
cat graph.cypher | cypher-shell -u neo4j -p password
```

Example Neo4j queries:

```cypher
// Find all tools that produce 'waybill_number' as output
MATCH (t:Tool)-[:produces_output]->(p:Parameter {name: 'waybill_number'})
RETURN t.name, t.api_endpoint

// Find API chains
MATCH (a:Tool)-[:potential_flow]->(b:Tool)
RETURN a.name, b.name

// Find all input parameters for a specific tool
MATCH (t:Tool {name: 'fms.get_all_transporters'})-[:requires_input]->(p:Parameter)
RETURN p.name
```

## Development

### Code Quality

```bash
# Type checking
mypy src/ --strict

# Run linter
ruff check src/

# Format code
black src/ tests/
```

### Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write tests for new features
4. Maintain 80%+ test coverage

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Built with:
- [NetworkX](https://networkx.org/) - Graph data structures
- [pandas](https://pandas.pydata.org/) - CSV parsing
- [PyVis](https://pyvis.readthedocs.io/) - Interactive graph visualization
- [Google Gemini](https://ai.google.dev/) - AI-powered semantic analysis
- [pytest](https://pytest.org/) - Testing framework
