"""Graph construction from API records."""

import logging
from typing import Dict, List, Set

import networkx as nx

from .json_extractor import JSONExtractor
from .models import APIRecord

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Construct graph structure from parsed API records."""
    
    def __init__(self) -> None:
        """Initialize graph builder with empty directed graph."""
        self.graph = nx.DiGraph()
        self.json_extractor = JSONExtractor()
        self._parameter_nodes: Set[str] = set()
    
    def add_tool_node(self, tool_name: str, csv_file: str, metadata: Dict[str, any]) -> str:
        """
        Add a tool node with CSV filename prefix.
        
        Args:
            tool_name: Name of the API tool
            csv_file: Source CSV filename (without extension)
            metadata: Additional node properties
            
        Returns:
            Node ID in format "{csv_file}.{tool_name}"
        """
        node_id = f"{csv_file}.{tool_name}"
        
        self.graph.add_node(
            node_id,
            node_type="tool",
            tool_name=tool_name,
            csv_file=csv_file,
            **metadata
        )
        
        logger.debug(f"Added tool node: {node_id}")
        return node_id
    
    def add_parameter_node(self, param_name: str, param_type: str) -> str:
        """
        Add a parameter node (reuses existing if already present).
        
        Args:
            param_name: Parameter name
            param_type: "input_param" or "output_param"
            
        Returns:
            Node ID (parameter name)
        """
        if param_name not in self._parameter_nodes:
            self.graph.add_node(
                param_name,
                node_type=param_type,
                param_name=param_name
            )
            self._parameter_nodes.add(param_name)
            logger.debug(f"Added parameter node: {param_name} ({param_type})")
        
        return param_name
    
    def add_input_edge(self, tool_id: str, param_name: str, metadata: Dict[str, any]) -> None:
        """
        Create edge from tool to input parameter.
        
        Args:
            tool_id: Tool node ID
            param_name: Parameter node ID
            metadata: Edge properties
        """
        self.graph.add_edge(
            tool_id,
            param_name,
            edge_type="requires_input",
            **metadata
        )
        logger.debug(f"Added input edge: {tool_id} -> {param_name}")
    
    def add_output_edge(self, tool_id: str, param_name: str, metadata: Dict[str, any]) -> None:
        """
        Create edge from tool to output parameter.
        
        Args:
            tool_id: Tool node ID
            param_name: Parameter node ID
            metadata: Edge properties
        """
        self.graph.add_edge(
            tool_id,
            param_name,
            edge_type="produces_output",
            **metadata
        )
        logger.debug(f"Added output edge: {tool_id} -> {param_name}")
    
    def build_from_records(self, records: List[APIRecord]) -> nx.DiGraph:
        """
        Build complete graph from API records.
        
        Args:
            records: List of APIRecord objects
            
        Returns:
            Constructed NetworkX directed graph
        """
        logger.info(f"Building graph from {len(records)} API records")
        
        for record in records:
            # Extract parameters first
            input_keys = self.json_extractor.extract_keys(record.input_payload)
            output_keys = self.json_extractor.extract_keys(record.output_response)
            
            # Create tool node with parameter metadata
            tool_metadata = {
                "api_endpoint": record.api_endpoint,
                "status_code": record.status_code,
                "success": record.success,
                "curl_command": record.curl_command,
                "timestamp": record.timestamp,
                "source_file": record.source_file,
                "input_keys": input_keys,
                "output_keys": output_keys
            }
            
            tool_id = self.add_tool_node(
                record.tool_name,
                record.source_file,
                tool_metadata
            )
            
            # Process input parameters
            for key in input_keys:
                param_node = self.add_parameter_node(key, "input_param")
                self.add_input_edge(tool_id, param_node, {"parameter_name": key})
            
            # Process output parameters
            for key in output_keys:
                param_node = self.add_parameter_node(key, "output_param")
                self.add_output_edge(tool_id, param_node, {"parameter_name": key})
        
        logger.info(
            f"Graph built: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )
        
        return self.graph
    
    def get_tool_nodes(self) -> List[str]:
        """Get all tool node IDs."""
        return [
            node for node, data in self.graph.nodes(data=True)
            if data.get("node_type") == "tool"
        ]
    
    def get_parameter_nodes(self, param_type: str = None) -> List[str]:
        """
        Get parameter node IDs.
        
        Args:
            param_type: Filter by "input_param" or "output_param", or None for all
            
        Returns:
            List of parameter node IDs
        """
        if param_type:
            return [
                node for node, data in self.graph.nodes(data=True)
                if data.get("node_type") == param_type
            ]
        else:
            return [
                node for node, data in self.graph.nodes(data=True)
                if data.get("node_type") in ("input_param", "output_param")
            ]
