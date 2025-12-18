"""Data models for API Graph Builder."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class APIRecord:
    """Represents a single API operation from CSV."""
    
    tool_name: str
    api_endpoint: str
    input_payload: str  # JSON string
    output_response: str  # JSON string
    status_code: Optional[int] = None
    success: Optional[bool] = None
    curl_command: Optional[str] = None
    timestamp: Optional[str] = None
    source_file: str = ""  # CSV filename without extension


@dataclass
class GraphNode:
    """Represents a node in the graph."""
    
    node_id: str  # Format: "{csv_file}.{tool_name}" or parameter name
    node_type: str  # "tool", "input_param", "output_param"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Represents an edge in the graph."""
    
    source: str  # Node ID
    target: str  # Node ID
    edge_type: str  # "requires_input", "produces_output", "potential_flow", "semantic_flow"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PotentialFlow:
    """Represents a detected data flow between APIs."""
    
    source_tool: str  # Tool that produces output
    target_tool: str  # Tool that consumes input
    matching_param: str  # Parameter name that matches
    confidence: float  # 0.0 to 1.0
    match_type: str  # "exact", "fuzzy", "semantic"


@dataclass
class SemanticMatch:
    """Represents a semantic relationship found by AI."""
    
    output_param: str  # Output parameter name
    input_param: str  # Input parameter name
    source_tool: str  # Tool producing the output
    target_tool: str  # Tool consuming the input
    confidence: float  # 0.0 to 1.0 from Gemini
    reasoning: str  # Gemini's explanation for the match


@dataclass
class ParameterInfo:
    """Information about a parameter for semantic analysis."""
    
    name: str  # Parameter name
    data_type: str  # Inferred type
    sample_value: Optional[Any]  # Example value from CSV
    tool_name: str  # Associated tool
    param_type: str  # "input" or "output"
