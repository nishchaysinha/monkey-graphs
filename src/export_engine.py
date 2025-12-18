"""Export graph in multiple formats."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

import networkx as nx

logger = logging.getLogger(__name__)


class ExportEngine:
    """Export graph in various formats."""
    
    def export_json(self, graph: nx.DiGraph, output_path: str) -> None:
        """
        Export graph as JSON in node-link format.
        
        Args:
            graph: NetworkX directed graph
            output_path: Output file path
        """
        data = nx.node_link_data(graph)
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported graph to JSON: {output_path}")
    
    def export_graphml(self, graph: nx.DiGraph, output_path: str) -> None:
        """
        Export graph as GraphML XML format.
        
        Args:
            graph: NetworkX directed graph
            output_path: Output file path
        """
        nx.write_graphml(graph, output_path)
        logger.info(f"Exported graph to GraphML: {output_path}")
    
    def export_dot(self, graph: nx.DiGraph, output_path: str) -> None:
        """
        Export graph as Graphviz DOT format.
        
        Args:
            graph: NetworkX directed graph
            output_path: Output file path
        """
        # Convert to pydot and write
        try:
            from networkx.drawing.nx_pydot import write_dot
            write_dot(graph, output_path)
            logger.info(f"Exported graph to DOT: {output_path}")
        except ImportError:
            logger.error("pydot not installed. Install with: pip install pydot")
            raise
    
    def export_neo4j_cypher(self, graph: nx.DiGraph, output_path: str) -> None:
        """
        Export graph as Neo4j Cypher CREATE statements.
        
        Args:
            graph: NetworkX directed graph
            output_path: Output file path
        """
        statements: list[str] = []
        
        # Create nodes
        statements.append("// Create nodes")
        for node, data in graph.nodes(data=True):
            node_type = data.get("node_type", "Unknown")
            label = node_type.replace("_", "").title()
            
            # Escape node ID for Cypher
            safe_id = node.replace(".", "_").replace("[", "_").replace("]", "_")
            
            # Build properties
            props = []
            for key, value in data.items():
                if value is not None and key != "node_type":
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "\\'")
                        props.append(f"{key}: '{escaped_value}'")
                    elif isinstance(value, bool):
                        props.append(f"{key}: {str(value).lower()}")
                    elif isinstance(value, (int, float)):
                        props.append(f"{key}: {value}")
            
            props_str = ", ".join(props)
            stmt = f"CREATE (n_{safe_id}:{label} {{{props_str}}});"
            statements.append(stmt)
        
        statements.append("")
        statements.append("// Create relationships")
        
        # Create edges
        for source, target, data in graph.edges(data=True):
            edge_type = data.get("edge_type", "RELATED_TO").upper()
            
            safe_source = source.replace(".", "_").replace("[", "_").replace("]", "_")
            safe_target = target.replace(".", "_").replace("[", "_").replace("]", "_")
            
            # Build properties
            props = []
            for key, value in data.items():
                if value is not None and key != "edge_type":
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "\\'")
                        props.append(f"{key}: '{escaped_value}'")
                    elif isinstance(value, bool):
                        props.append(f"{key}: {str(value).lower()}")
                    elif isinstance(value, (int, float)):
                        props.append(f"{key}: {value}")
            
            props_str = f" {{{', '.join(props)}}}" if props else ""
            stmt = f"MATCH (a), (b) WHERE id(a) = id(n_{safe_source}) AND id(b) = id(n_{safe_target}) CREATE (a)-[:{edge_type}{props_str}]->(b);"
            statements.append(stmt)
        
        # Write to file
        with open(output_path, "w") as f:
            f.write("\n".join(statements))
        
        logger.info(f"Exported graph to Neo4j Cypher: {output_path}")
    
    def export_networkx(self, graph: nx.DiGraph) -> nx.DiGraph:
        """
        Return NetworkX graph object (for programmatic access).
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            The same graph object
        """
        return graph
    
    def to_dict(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Convert graph to dictionary representation.
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            Dictionary with nodes and edges
        """
        return {
            "nodes": [
                {"id": node, **data}
                for node, data in graph.nodes(data=True)
            ],
            "edges": [
                {"source": source, "target": target, **data}
                for source, target, data in graph.edges(data=True)
            ]
        }
