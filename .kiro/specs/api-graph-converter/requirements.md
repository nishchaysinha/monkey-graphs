# Requirements Document

## Introduction

This document specifies the requirements for an API Graph Converter tool that transforms CSV-based API documentation into graph representations. The tool will parse API metadata from CSV files and create a graph structure where nodes represent API tools and their JSON parameters/responses, with edges representing input/output relationships.

## Glossary

- **API Tool**: A named API endpoint operation documented in the CSV files (e.g., get_all_transporters, search_vehicle_in_repo)
- **Tool Node**: A graph node representing an API tool/function
- **Parameter Node**: A graph node representing a JSON key from input_payload or output_response
- **Input Edge**: A directed edge from a Tool Node to a Parameter Node representing an input parameter
- **Output Edge**: A directed edge from a Tool Node to a Parameter Node representing an output field
- **CSV Parser**: The component that reads and parses CSV files containing API documentation
- **Graph Builder**: The component that constructs the graph structure from parsed CSV data
- **Graph Representation**: The data structure (nodes and edges) representing API relationships

## Requirements

### Requirement 1

**User Story:** As a developer, I want to load CSV files containing API documentation, so that I can convert them into graph representations.

#### Acceptance Criteria

1. WHEN a user provides a CSV file path, THE System SHALL read the CSV file and parse its contents
2. WHEN the CSV file contains the required columns (tool_name, api_endpoint, input_payload, output_response), THE System SHALL extract these fields successfully
3. WHEN the CSV file is malformed or missing required columns, THE System SHALL report a clear error message
4. WHEN multiple CSV files are provided, THE System SHALL process each file and merge the results into a single graph
5. WHEN the CSV contains JSON strings in input_payload or output_response columns, THE System SHALL parse them into structured data

### Requirement 2

**User Story:** As a developer, I want the system to create nodes for API tools, so that each API operation is represented in the graph.

#### Acceptance Criteria

1. WHEN the System processes a CSV row, THE System SHALL create a Tool Node with the node identifier formatted as "{csv_filename}.{tool_name}"
2. WHEN a Tool Node is created, THE System SHALL store metadata including api_endpoint, curl_command, status_code, timestamp, and source_file
3. WHEN duplicate tool_names appear across different CSV files, THE System SHALL create separate nodes with unique identifiers by prepending the CSV filename
4. WHEN the tool_name is empty or null, THE System SHALL skip that row and log a warning
5. THE System SHALL assign a node type of "tool" to all Tool Nodes

### Requirement 3

**User Story:** As a developer, I want the system to extract JSON keys from input payloads, so that I can see what parameters each API requires.

#### Acceptance Criteria

1. WHEN the System parses an input_payload JSON string, THE System SHALL extract all top-level keys
2. WHEN the input_payload contains nested JSON objects, THE System SHALL extract nested keys using dot notation (e.g., "slot.LM_FWD.date")
3. WHEN the input_payload contains arrays, THE System SHALL represent array elements with bracket notation (e.g., "items[0].id")
4. WHEN a JSON key is extracted from input_payload, THE System SHALL create a Parameter Node with node type "input_param"
5. WHEN the input_payload is empty, null, or invalid JSON, THE System SHALL handle gracefully without creating parameter nodes

### Requirement 4

**User Story:** As a developer, I want the system to extract JSON keys from output responses, so that I can see what data each API returns.

#### Acceptance Criteria

1. WHEN the System parses an output_response JSON string, THE System SHALL extract all top-level keys
2. WHEN the output_response contains nested JSON objects, THE System SHALL extract nested keys using dot notation
3. WHEN the output_response contains arrays of objects, THE System SHALL extract keys from array elements
4. WHEN a JSON key is extracted from output_response, THE System SHALL create a Parameter Node with node type "output_param"
5. WHEN the output_response is empty, null, or invalid JSON, THE System SHALL handle gracefully without creating parameter nodes

### Requirement 5

**User Story:** As a developer, I want the system to create edges between tools and their input parameters, so that I can understand what inputs each API requires.

#### Acceptance Criteria

1. WHEN a Parameter Node is created from input_payload, THE System SHALL create an Input Edge from the Tool Node to the Parameter Node
2. WHEN creating an Input Edge, THE System SHALL label the edge with relationship type "requires_input"
3. WHEN the same parameter name appears in multiple tools, THE System SHALL create separate edges for each tool-parameter relationship
4. THE System SHALL store edge metadata including the parameter data type if determinable from the JSON value
5. THE System SHALL ensure Input Edges are directed from Tool Node to Parameter Node

### Requirement 6

**User Story:** As a developer, I want the system to create edges between tools and their output parameters, so that I can understand what data each API produces.

#### Acceptance Criteria

1. WHEN a Parameter Node is created from output_response, THE System SHALL create an Output Edge from the Tool Node to the Parameter Node
2. WHEN creating an Output Edge, THE System SHALL label the edge with relationship type "produces_output"
3. WHEN the same output field name appears in multiple tools, THE System SHALL identify potential data flow connections
4. THE System SHALL store edge metadata including the parameter data type if determinable from the JSON value
5. THE System SHALL ensure Output Edges are directed from Tool Node to Parameter Node

### Requirement 7

**User Story:** As a developer, I want to export the graph in standard formats, so that I can visualize and analyze it with various tools.

#### Acceptance Criteria

1. WHEN the graph is constructed, THE System SHALL provide an export function to JSON format
2. WHEN exporting to JSON, THE System SHALL include all nodes with their properties and all edges with their relationships
3. WHEN the user requests GraphML format, THE System SHALL export the graph in valid GraphML XML format
4. WHEN the user requests DOT format, THE System SHALL export the graph in Graphviz DOT format
5. WHEN the user requests NetworkX format, THE System SHALL provide a Python NetworkX graph object

### Requirement 8

**User Story:** As a developer, I want to identify potential data flow between APIs, so that I can understand how APIs can be chained together.

#### Acceptance Criteria

1. WHEN one API's output parameter name matches another API's input parameter name, THE System SHALL create a potential_flow edge between the two Tool Nodes
2. WHEN identifying potential flows, THE System SHALL consider parameter name similarity (exact match and fuzzy match)
3. WHEN a potential flow is identified, THE System SHALL store metadata including the matching parameter name and confidence score
4. WHEN the user queries for API chains, THE System SHALL return sequences of APIs that can be connected via matching parameters
5. THE System SHALL allow users to filter potential flows by confidence threshold

### Requirement 9

**User Story:** As a developer, I want the system to use AI to find semantic relationships between parameters, so that I can discover connections that aren't obvious from parameter names alone.

#### Acceptance Criteria

1. WHEN the graph is constructed, THE System SHALL send parameter information to Gemini API for semantic analysis
2. WHEN Gemini identifies a semantic relationship between an output parameter and an input parameter, THE System SHALL create a semantic_flow edge with confidence score and reasoning
3. WHEN the Gemini API is unavailable or fails, THE System SHALL log a warning and continue with only exact and fuzzy matches
4. WHEN processing large graphs, THE System SHALL batch API requests to Gemini to respect rate limits and reduce costs
5. THE System SHALL cache Gemini responses to avoid redundant API calls for the same parameter pairs

### Requirement 10

**User Story:** As a developer, I want to visualize the graph, so that I can understand API relationships visually.

#### Acceptance Criteria

1. WHEN the user requests visualization, THE System SHALL generate an interactive graph visualization
2. WHEN displaying the graph, THE System SHALL use different colors or shapes for Tool Nodes vs Parameter Nodes
3. WHEN displaying edges, THE System SHALL use different styles for Input Edges vs Output Edges vs potential_flow edges vs semantic_flow edges
4. WHEN the graph is large, THE System SHALL provide zoom, pan, and filter capabilities
5. WHEN a user clicks on a node, THE System SHALL display detailed metadata including API endpoint, parameters, and sample curl command
