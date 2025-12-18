# Design Document

## Overview

The API Graph Converter is a Python-based tool that transforms CSV-based API documentation into graph representations. The system parses CSV files containing API metadata (tool names, endpoints, input/output payloads) and constructs a directed graph where nodes represent API tools and their parameters, with edges representing input/output relationships and potential data flows between APIs.

The tool enables developers to:
- Visualize API relationships and dependencies
- Identify potential API chains where one API's output can feed another's input
- Query for APIs with specific characteristics
- Export graphs in multiple formats for analysis

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   CSV Files     │
│ (fms, hq, etc.) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CSV Parser     │
│  - Read files   │
│  - Parse JSON   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Graph Builder  │
│  - Create nodes │
│  - Create edges │
│  - Detect flows │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Graph Store    │
│  (NetworkX)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Semantic Matcher│
│  (Gemini AI)    │
│  - Find hidden  │
│    connections  │
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐
    │ Export │    │Visualize│   │  Neo4j │
    │ Engine │    │ Engine  │   │ Export │
    └────────┘    └────────┘    └────────┘
```

### Component Architecture

The system follows a modular architecture with clear separation of concerns:

1. **CSV Parser Module**: Handles file I/O and CSV parsing
2. **JSON Extractor Module**: Extracts and flattens JSON structures
3. **Graph Builder Module**: Constructs the graph structure
4. **Flow Detector Module**: Identifies potential API chains using exact and fuzzy matching
5. **Semantic Matcher Module**: Uses Gemini AI to find semantic relationships between parameters
6. **Export Engine Module**: Handles multiple export formats (JSON, GraphML, DOT, Neo4j Cypher)
7. **Visualization Module**: Generates interactive visualizations

## Components and Interfaces

### 1. CSV Parser

**Responsibility**: Read and parse CSV files containing API documentation

**Interface**:
```python
class CSVParser:
    def parse_file(self, file_path: str) -> List[APIRecord]:
        """Parse a single CSV file and return list of API records"""
        
    def parse_multiple(self, file_paths: List[str]) -> List[APIRecord]:
        """Parse multiple CSV files and return combined records"""
        
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate that CSV has required columns"""
```

**Key Methods**:
- `parse_file()`: Reads CSV, validates schema, returns structured records
- `parse_multiple()`: Batch processes multiple files
- `validate_schema()`: Ensures required columns exist

### 2. JSON Extractor

**Responsibility**: Extract and flatten JSON structures from input/output payloads

**Interface**:
```python
class JSONExtractor:
    def extract_keys(self, json_str: str, prefix: str = "") -> List[str]:
        """Extract all keys from JSON string with dot notation"""
        
    def flatten_json(self, obj: dict, parent_key: str = "") -> Dict[str, Any]:
        """Recursively flatten nested JSON objects"""
        
    def infer_type(self, value: Any) -> str:
        """Infer data type from JSON value"""
```

**Key Methods**:
- `extract_keys()`: Recursively extracts all keys using dot notation
- `flatten_json()`: Converts nested JSON to flat key-value pairs
- `infer_type()`: Determines parameter data types

### 3. Graph Builder

**Responsibility**: Construct the graph structure from parsed API records

**Interface**:
```python
class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_tool_node(self, tool_name: str, csv_file: str, metadata: dict):
        """Add a tool node with CSV filename prefix"""
        
    def add_parameter_node(self, param_name: str, param_type: str):
        """Add a parameter node (input or output)"""
        
    def add_input_edge(self, tool_id: str, param_name: str, metadata: dict):
        """Create edge from tool to input parameter"""
        
    def add_output_edge(self, tool_id: str, param_name: str, metadata: dict):
        """Create edge from tool to output parameter"""
        
    def build_from_records(self, records: List[APIRecord]) -> nx.DiGraph:
        """Build complete graph from API records"""
```

**Key Methods**:
- `add_tool_node()`: Creates tool nodes with `{csv_filename}.{tool_name}` format
- `add_parameter_node()`: Creates parameter nodes with type metadata
- `add_input_edge()` / `add_output_edge()`: Creates directed edges
- `build_from_records()`: Orchestrates graph construction

### 4. Flow Detector

**Responsibility**: Identify potential data flows between APIs

**Interface**:
```python
class FlowDetector:
    def detect_flows(self, graph: nx.DiGraph) -> List[PotentialFlow]:
        """Detect all potential flows in the graph"""
        
    def find_matching_params(self, output_params: Set[str], 
                            input_params: Set[str]) -> List[Match]:
        """Find matching parameter names between outputs and inputs"""
        
    def calculate_confidence(self, match: Match) -> float:
        """Calculate confidence score for a parameter match"""
        
    def add_flow_edges(self, graph: nx.DiGraph, flows: List[PotentialFlow]):
        """Add potential_flow edges to the graph"""
```

**Key Methods**:
- `detect_flows()`: Finds all output→input parameter matches
- `find_matching_params()`: Uses exact and fuzzy matching
- `calculate_confidence()`: Scores match quality (0.0 to 1.0)
- `add_flow_edges()`: Creates edges between potentially chainable APIs

### 5. Semantic Matcher

**Responsibility**: Use Gemini AI to identify semantic relationships between parameters that don't have matching names

**Interface**:
```python
class SemanticMatcher:
    def __init__(self, api_key: str):
        self.client = genai.GenerativeModel('gemini-pro')
        
    def analyze_graph(self, graph: nx.DiGraph) -> List[SemanticMatch]:
        """Analyze entire graph to find semantic connections"""
        
    def find_semantic_matches(self, output_params: List[ParameterInfo], 
                             input_params: List[ParameterInfo]) -> List[SemanticMatch]:
        """Use Gemini to find semantic matches between parameters"""
        
    def build_prompt(self, outputs: List[ParameterInfo], 
                    inputs: List[ParameterInfo]) -> str:
        """Construct prompt for Gemini API"""
        
    def parse_gemini_response(self, response: str) -> List[SemanticMatch]:
        """Parse Gemini's response into structured matches"""
        
    def add_semantic_edges(self, graph: nx.DiGraph, 
                          matches: List[SemanticMatch]):
        """Add semantic_flow edges to the graph"""
```

**Key Methods**:
- `analyze_graph()`: Orchestrates semantic analysis of the entire graph
- `find_semantic_matches()`: Sends parameter lists to Gemini for analysis
- `build_prompt()`: Creates structured prompt with parameter context
- `parse_gemini_response()`: Extracts matches from Gemini's JSON response
- `add_semantic_edges()`: Creates edges with `semantic_flow` type

**Prompt Strategy**:
The system will send batches of parameters to Gemini with context:
```
You are analyzing API parameters to find semantic relationships.

Output Parameters (from API X):
- waybill_number (string): "13514521797602"
- wbn (string): "1490822109976161"  
- registration_number (string): "WB73G1174"

Input Parameters (from API Y):
- trackingNumber (string): required
- vehicle_reg (string): optional
- ref_ids (string): required

Task: Identify which output parameters could semantically match which input parameters.
Consider: abbreviations, synonyms, domain knowledge, data types, sample values.

Return JSON array of matches:
[
  {
    "output_param": "waybill_number",
    "input_param": "trackingNumber", 
    "confidence": 0.95,
    "reasoning": "Both represent shipment tracking identifiers"
  },
  {
    "output_param": "wbn",
    "input_param": "ref_ids",
    "confidence": 0.90,
    "reasoning": "wbn is waybill number abbreviation, ref_ids accepts reference IDs"
  }
]
```

**Batching Strategy**:
- Process APIs in batches to avoid token limits
- Focus on cross-system connections (FMS → HQ, WMS → FMS, etc.)
- Cache results to avoid redundant API calls
- Rate limit to respect Gemini API quotas

### 6. Export Engine

**Responsibility**: Export graph in multiple formats

**Interface**:
```python
class ExportEngine:
    def export_json(self, graph: nx.DiGraph, output_path: str):
        """Export graph as JSON"""
        
    def export_graphml(self, graph: nx.DiGraph, output_path: str):
        """Export graph as GraphML XML"""
        
    def export_dot(self, graph: nx.DiGraph, output_path: str):
        """Export graph as Graphviz DOT"""
        
    def export_neo4j_cypher(self, graph: nx.DiGraph, output_path: str):
        """Export graph as Neo4j Cypher statements"""
        
    def export_networkx(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Return NetworkX graph object"""
        
    def to_dict(self, graph: nx.DiGraph) -> dict:
        """Convert graph to dictionary representation"""
```

**Key Methods**:
- `export_json()`: Node-link JSON format
- `export_graphml()`: XML format for tools like Gephi
- `export_dot()`: Graphviz format for rendering
- `export_neo4j_cypher()`: Cypher CREATE statements for Neo4j import
- `to_dict()`: Python dictionary for programmatic access

### 7. Visualization Module

**Responsibility**: Generate interactive graph visualizations

**Interface**:
```python
class Visualizer:
    def create_interactive_plot(self, graph: nx.DiGraph, 
                               output_path: str = "graph.html"):
        """Create interactive HTML visualization using Plotly/Pyvis"""
        
    def create_static_plot(self, graph: nx.DiGraph, 
                          output_path: str = "graph.png"):
        """Create static image using matplotlib"""
        
    def apply_layout(self, graph: nx.DiGraph, 
                    layout: str = "spring") -> Dict[str, Tuple[float, float]]:
        """Apply graph layout algorithm"""
        
    def style_nodes(self, node_type: str) -> dict:
        """Return styling for node type"""
        
    def style_edges(self, edge_type: str) -> dict:
        """Return styling for edge type"""
```

**Key Methods**:
- `create_interactive_plot()`: HTML visualization with zoom/pan
- `create_static_plot()`: PNG/SVG export
- `apply_layout()`: Spring, hierarchical, or circular layouts
- `style_nodes()` / `style_edges()`: Visual differentiation

## Data Models

### APIRecord

Represents a single row from the CSV file:

```python
@dataclass
class APIRecord:
    tool_name: str
    api_endpoint: str
    input_payload: str  # JSON string
    output_response: str  # JSON string
    status_code: Optional[int] = None
    success: Optional[bool] = None
    curl_command: Optional[str] = None
    timestamp: Optional[str] = None
    source_file: str = ""  # CSV filename
```

### GraphNode

Represents a node in the graph:

```python
@dataclass
class GraphNode:
    node_id: str  # Format: "{csv_file}.{tool_name}" or parameter name
    node_type: str  # "tool", "input_param", "output_param"
    metadata: Dict[str, Any]  # Additional properties
    
    # For tool nodes:
    # - api_endpoint
    # - curl_command
    # - status_code
    # - timestamp
    # - source_file
    
    # For parameter nodes:
    # - data_type
    # - sample_value
```

### GraphEdge

Represents an edge in the graph:

```python
@dataclass
class GraphEdge:
    source: str  # Node ID
    target: str  # Node ID
    edge_type: str  # "requires_input", "produces_output", "potential_flow", "semantic_flow"
    metadata: Dict[str, Any]
    
    # For input/output edges:
    # - parameter_name
    # - data_type
    
    # For potential_flow edges:
    # - matching_parameter
    # - confidence_score
    # - match_type: "exact" or "fuzzy"
    
    # For semantic_flow edges:
    # - output_param
    # - input_param
    # - confidence_score
    # - reasoning (from Gemini)
    # - match_type: "semantic"
```

### PotentialFlow

Represents a detected data flow between APIs:

```python
@dataclass
class PotentialFlow:
    source_tool: str  # Tool that produces output
    target_tool: str  # Tool that consumes input
    matching_param: str  # Parameter name that matches
    confidence: float  # 0.0 to 1.0
    match_type: str  # "exact", "fuzzy", "semantic"

@dataclass
class SemanticMatch:
    output_param: str  # Output parameter name
    input_param: str  # Input parameter name
    source_tool: str  # Tool producing the output
    target_tool: str  # Tool consuming the input
    confidence: float  # 0.0 to 1.0 from Gemini
    reasoning: str  # Gemini's explanation for the match

@dataclass
class ParameterInfo:
    name: str  # Parameter name
    data_type: str  # Inferred type
    sample_value: Optional[Any]  # Example value from CSV
    tool_name: str  # Associated tool
    param_type: str  # "input" or "output"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Tool Node Uniqueness

*For any* set of CSV files processed, all tool nodes in the resulting graph should have unique identifiers in the format `{csv_filename}.{tool_name}`, ensuring no naming conflicts.

**Validates: Requirements 2.1, 2.3**

### Property 2: JSON Parsing Round Trip

*For any* valid JSON string in input_payload or output_response, parsing and extracting keys should not raise exceptions and should produce a non-empty list of parameter names when the JSON contains at least one key.

**Validates: Requirements 1.5, 3.1, 4.1**

### Property 3: Edge Directionality Consistency

*For any* edge in the graph, if the edge type is "requires_input" or "produces_output", the source node must be of type "tool" and the target node must be of type "input_param" or "output_param" respectively.

**Validates: Requirements 5.5, 6.5**

### Property 4: Parameter Node Reuse

*For any* parameter name that appears in multiple tools, the graph should contain exactly one parameter node with that name, with multiple edges connecting it to different tool nodes.

**Validates: Requirements 5.3, 6.3**

### Property 5: Flow Detection Symmetry

*For any* two tools A and B, if there exists a potential_flow edge from A to B based on matching parameter P, then tool A must have an output edge to parameter P and tool B must have an input edge from parameter P.

**Validates: Requirements 8.1, 8.3**

### Property 6: Export Format Validity

*For any* graph exported to GraphML, DOT, or JSON format, the exported file should be parseable by standard tools (NetworkX for GraphML/JSON, Graphviz for DOT) and should reconstruct a graph with the same number of nodes and edges.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 7: Neo4j Export Validity

*For any* graph exported to Neo4j Cypher format, the generated Cypher statements should be syntactically valid and executable in Neo4j, creating the same number of nodes and relationships as the source graph.

**Validates: Requirements 7.1, 7.5**

### Property 8: Nested Key Extraction

*For any* nested JSON object with depth N, all keys at all levels should be extracted with proper dot notation, and the number of extracted keys should be greater than or equal to N.

**Validates: Requirements 3.2, 4.2**

### Property 9: Confidence Score Bounds

*For any* potential flow detected, the confidence score should be a float value between 0.0 and 1.0 inclusive, with exact matches having confidence 1.0.

**Validates: Requirements 8.3, 8.5**

### Property 10: Graph Connectivity

*For any* tool node in the graph, it should have at least one outgoing edge (either to an input parameter, output parameter, or another tool via potential_flow), unless the tool has no parseable input or output.

**Validates: Requirements 5.1, 6.1**

## Error Handling

### CSV Parsing Errors

- **Missing Required Columns**: Log error with missing column names, skip file
- **Malformed CSV**: Log error with line number, skip file
- **Empty File**: Log warning, skip file
- **Encoding Issues**: Attempt UTF-8, fallback to latin-1, log warning

### JSON Parsing Errors

- **Invalid JSON**: Log warning with tool name, skip parameter extraction for that field
- **Empty JSON**: Skip parameter extraction, no error
- **Null Values**: Skip parameter extraction, no error
- **Truncated JSON**: Attempt best-effort parsing, log warning

### Graph Construction Errors

- **Duplicate Node IDs**: Should not occur with CSV prefix, but log error if detected
- **Invalid Edge**: Log error with source/target node IDs, skip edge
- **Missing Node Reference**: Log error, skip edge creation

### Export Errors

- **File Write Permission**: Raise exception with clear message
- **Invalid Format**: Raise exception with supported formats list
- **Large Graph**: Log warning if graph exceeds 10,000 nodes, proceed with export

### Query Errors

- **Invalid Regex Pattern**: Raise exception with pattern syntax error
- **Node Not Found**: Return empty list, no error
- **Path Too Long**: Log warning, limit results to max_length parameter

## Testing Strategy

### Unit Testing

The system will use pytest for unit testing with the following test coverage:

1. **CSV Parser Tests**
   - Test parsing valid CSV files
   - Test handling missing columns
   - Test handling malformed CSV
   - Test multiple file parsing

2. **JSON Extractor Tests**
   - Test flat JSON extraction
   - Test nested JSON extraction with dot notation
   - Test array handling with bracket notation
   - Test invalid JSON handling
   - Test type inference

3. **Graph Builder Tests**
   - Test tool node creation with CSV prefix
   - Test parameter node creation
   - Test edge creation
   - Test duplicate handling

4. **Flow Detector Tests**
   - Test exact parameter matching
   - Test fuzzy parameter matching
   - Test confidence score calculation
   - Test flow edge creation

5. **Semantic Matcher Tests**
   - Test Gemini API integration
   - Test prompt construction
   - Test response parsing
   - Test semantic edge creation
   - Test batching logic
   - Test caching mechanism

6. **Export Engine Tests**
   - Test JSON export/import round trip
   - Test GraphML export validity
   - Test DOT export validity
   - Test Neo4j Cypher export validity
   - Test format conversion

7. **Visualization Tests**
   - Test interactive HTML generation
   - Test static image generation
   - Test layout algorithms
   - Test node/edge styling

### Property-Based Testing

The system will use Hypothesis for property-based testing with a minimum of 100 iterations per test:

1. **Property Test: Tool Node Uniqueness** (Property 1)
   - Generate random CSV data with duplicate tool names
   - Verify all tool nodes have unique IDs with CSV prefix

2. **Property Test: JSON Parsing Robustness** (Property 2)
   - Generate random valid JSON structures
   - Verify parsing never raises exceptions
   - Verify non-empty JSON produces non-empty key lists

3. **Property Test: Edge Directionality** (Property 3)
   - Generate random graphs
   - Verify all edges have correct source/target node types

4. **Property Test: Parameter Node Reuse** (Property 4)
   - Generate APIs with overlapping parameters
   - Verify parameter nodes are reused correctly

5. **Property Test: Flow Detection Symmetry** (Property 5)
   - Generate random API pairs with matching parameters
   - Verify flow edges are consistent with input/output edges

6. **Property Test: Export Round Trip** (Property 6)
   - Generate random graphs
   - Export and re-import in each format
   - Verify node and edge counts match

7. **Property Test: Neo4j Export Validity** (Property 7)
   - Generate random graphs
   - Export to Neo4j Cypher format
   - Verify Cypher syntax is valid

8. **Property Test: Nested Key Extraction** (Property 8)
   - Generate nested JSON with varying depths
   - Verify all keys are extracted with proper notation

9. **Property Test: Confidence Score Bounds** (Property 9)
   - Generate random parameter matches
   - Verify confidence scores are in [0.0, 1.0] range

10. **Property Test: Graph Connectivity** (Property 10)
    - Generate random API records
    - Verify all tool nodes have at least one edge

### Integration Testing

- Test end-to-end workflow: CSV → Graph → Export
- Test with real CSV files (fms.csv, hq.csv, wms.csv, hrms.csv)
- Test visualization generation
- Test query operations on real data

### Performance Testing

- Test with large CSV files (>10,000 rows)
- Test graph construction time
- Test query performance
- Test export performance for large graphs

## Implementation Notes

### Technology Stack

- **Language**: Python 3.9+
- **Graph Library**: NetworkX 3.0+
- **CSV Parsing**: pandas 2.0+
- **JSON Handling**: Built-in json module
- **Visualization**: Plotly or Pyvis for interactive, matplotlib for static
- **Testing**: pytest, hypothesis
- **Type Checking**: mypy with strict mode

### Dependencies

```
networkx>=3.0
pandas>=2.0
plotly>=5.0
pytest>=7.0
hypothesis>=6.0
google-generativeai>=0.3.0  # Gemini API
python-dotenv>=1.0.0  # For API key management
```

### Performance Considerations

- Use generators for large CSV files to reduce memory footprint
- Cache parameter node lookups to avoid duplicate creation
- Use NetworkX's built-in algorithms for path finding
- Lazy load visualization for large graphs (>1000 nodes)

### Extensibility

The design supports future extensions:
- Additional export formats (GraphSON, CSV)
- Alternative LLMs for semantic matching (Claude, GPT-4, local models)
- Embedding-based similarity for parameter matching
- Integration with graph databases (Neo4j, ArangoDB)
- API recommendation based on graph analysis
- Automatic API documentation generation from graph

### Gemini API Configuration

The system requires a Gemini API key for semantic matching:

1. **API Key Setup**: Store in `.env` file or environment variable
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

2. **Rate Limiting**: Implement exponential backoff for API calls
3. **Cost Management**: Cache results, batch requests efficiently
4. **Fallback**: System works without Gemini (only exact/fuzzy matching)

**Example Semantic Matches**:
- `waybill_number` (HQ) ↔ `wbn` (FMS) - abbreviation
- `registration_number` (FMS) ↔ `vehicle_reg` (WMS) - synonym
- `user_id` (HRMS) ↔ `username` (HQ) - related concepts
- `center_id` (FMS) ↔ `fc_uuid` (WMS) - domain knowledge

### Neo4j Integration

For users who want to query the graph using Neo4j:

1. **Export to Cypher**: Use `export_neo4j_cypher()` to generate CREATE statements
2. **Import to Neo4j**: Run the generated Cypher file in Neo4j Browser or using neo4j-admin
3. **Query with Cypher**: Use Neo4j's powerful query language for complex graph traversals

Example Cypher queries after import:
```cypher
// Find all tools that produce 'waybill_number' as output
MATCH (t:Tool)-[:produces_output]->(p:Parameter {name: 'waybill_number'})
RETURN t.name, t.api_endpoint

// Find API chains (tool A -> tool B via matching parameters)
MATCH (a:Tool)-[:potential_flow]->(b:Tool)
RETURN a.name, b.name

// Find all input parameters for a specific tool
MATCH (t:Tool {name: 'fms.get_all_transporters'})-[:requires_input]->(p:Parameter)
RETURN p.name, p.data_type
```
