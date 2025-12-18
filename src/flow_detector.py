"""Detect potential data flows between APIs."""

import logging
from difflib import SequenceMatcher
from typing import List, Set, Tuple

import networkx as nx

from .models import PotentialFlow

logger = logging.getLogger(__name__)


class FlowDetector:
    """Identify potential data flows between APIs based on parameter matching."""
    
    def __init__(self, fuzzy_threshold: float = 0.8, enable_fuzzy: bool = False) -> None:
        """
        Initialize flow detector.
        
        Args:
            fuzzy_threshold: Minimum similarity score for fuzzy matching (0.0 to 1.0)
            enable_fuzzy: Enable fuzzy matching (disabled by default due to false positives)
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.enable_fuzzy = enable_fuzzy
    
    def detect_flows(self, graph: nx.DiGraph) -> List[PotentialFlow]:
        """
        Detect all potential flows in the graph.
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            List of detected potential flows
        """
        logger.info("Detecting potential flows between APIs")
        
        flows: List[PotentialFlow] = []
        tool_nodes = self._get_tool_nodes(graph)
        
        # For each pair of tools, check if outputs match inputs
        for source_tool in tool_nodes:
            output_params = self._get_output_params(graph, source_tool)
            
            for target_tool in tool_nodes:
                if source_tool == target_tool:
                    continue
                
                input_params = self._get_input_params(graph, target_tool)
                matches = self.find_matching_params(output_params, input_params)
                
                for param, confidence, match_type in matches:
                    flow = PotentialFlow(
                        source_tool=source_tool,
                        target_tool=target_tool,
                        matching_param=param,
                        confidence=confidence,
                        match_type=match_type
                    )
                    flows.append(flow)
        
        logger.info(f"Detected {len(flows)} potential flows")
        return flows
    
    def find_matching_params(
        self,
        output_params: Set[str],
        input_params: Set[str]
    ) -> List[Tuple[str, float, str]]:
        """
        Find matching parameter names between outputs and inputs.
        
        Args:
            output_params: Set of output parameter names
            input_params: Set of input parameter names
            
        Returns:
            List of tuples (param_name, confidence, match_type)
        """
        matches: List[Tuple[str, float, str]] = []
        
        # Exact matches only (fuzzy matching disabled by default)
        exact_matches = output_params & input_params
        for param in exact_matches:
            matches.append((param, 1.0, "exact"))
        
        # Fuzzy matches (only if explicitly enabled)
        if self.enable_fuzzy:
            remaining_outputs = output_params - exact_matches
            remaining_inputs = input_params - exact_matches
            
            for out_param in remaining_outputs:
                for in_param in remaining_inputs:
                    similarity = self._calculate_similarity(out_param, in_param)
                    if similarity >= self.fuzzy_threshold:
                        matches.append((f"{out_param}~{in_param}", similarity, "fuzzy"))
        
        return matches
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize strings (lowercase, remove underscores)
        s1 = str1.lower().replace("_", "").replace("-", "")
        s2 = str2.lower().replace("_", "").replace("-", "")
        
        return SequenceMatcher(None, s1, s2).ratio()
    
    def add_flow_edges(self, graph: nx.DiGraph, flows: List[PotentialFlow]) -> None:
        """
        Add potential_flow edges to the graph.
        
        Args:
            graph: NetworkX directed graph
            flows: List of potential flows to add
        """
        for flow in flows:
            graph.add_edge(
                flow.source_tool,
                flow.target_tool,
                edge_type="potential_flow",
                matching_param=flow.matching_param,
                confidence=flow.confidence,
                match_type=flow.match_type
            )
        
        logger.info(f"Added {len(flows)} potential_flow edges to graph")
    
    def _get_tool_nodes(self, graph: nx.DiGraph) -> List[str]:
        """Get all tool node IDs from graph."""
        return [
            node for node, data in graph.nodes(data=True)
            if data.get("node_type") == "tool"
        ]
    
    def _get_output_params(self, graph: nx.DiGraph, tool_id: str) -> Set[str]:
        """Get output parameters for a tool."""
        params: Set[str] = set()
        
        for _, target, data in graph.out_edges(tool_id, data=True):
            if data.get("edge_type") == "produces_output":
                params.add(target)
        
        return params
    
    def _get_input_params(self, graph: nx.DiGraph, tool_id: str) -> Set[str]:
        """Get input parameters for a tool."""
        params: Set[str] = set()
        
        for _, target, data in graph.out_edges(tool_id, data=True):
            if data.get("edge_type") == "requires_input":
                params.add(target)
        
        return params
