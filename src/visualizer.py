"""Graph visualization utilities."""

import logging
from typing import Dict, List, Tuple

import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network

logger = logging.getLogger(__name__)


class Visualizer:
    """Generate interactive graph visualizations."""
    
    # Color scheme for different node types
    NODE_COLORS = {
        "tool": "#FF6B6B",           # Red for API tools
        "input_param": "#4ECDC4",    # Teal for input parameters
        "output_param": "#95E1D3"    # Light teal for output parameters
    }
    
    # Edge colors for different relationship types
    EDGE_COLORS = {
        "requires_input": "#A8DADC",     # Light blue
        "produces_output": "#457B9D",    # Dark blue
        "potential_flow": "#E63946",     # Red
        "semantic_flow": "#F77F00"       # Orange
    }
    
    def create_interactive_plot(
        self,
        graph: nx.DiGraph,
        output_path: str = "graph.html",
        layout: str = "spring",
        show_labels: bool = True,
        filter_node_type: str = None
    ) -> None:
        """
        Create interactive HTML visualization using Plotly.
        
        Args:
            graph: NetworkX directed graph
            output_path: Output HTML file path
            layout: Layout algorithm ("spring", "circular", "kamada_kawai")
            show_labels: Whether to show node labels
            filter_node_type: Only show nodes of this type (None for all)
        """
        logger.info(f"Creating interactive visualization with {layout} layout")
        
        # Filter graph if requested
        if filter_node_type:
            filtered_nodes = [
                node for node, data in graph.nodes(data=True)
                if data.get("node_type") == filter_node_type
            ]
            graph = graph.subgraph(filtered_nodes).copy()
            logger.info(f"Filtered to {len(filtered_nodes)} {filter_node_type} nodes")
        
        # Calculate layout
        pos = self.apply_layout(graph, layout)
        
        # Create edge traces
        edge_traces = self._create_edge_traces(graph, pos)
        
        # Create node trace
        node_trace = self._create_node_trace(graph, pos, show_labels)
        
        # Create arrow annotations
        annotations = self._create_arrow_annotations(graph, pos)
        
        # Create figure
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=dict(
                    text=f"API Graph Visualization ({graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges)",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=True,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="white",
                height=800,
                annotations=annotations
            )
        )
        
        # Write to file
        fig.write_html(output_path)
        logger.info(f"Interactive visualization saved to {output_path}")
    
    def create_flow_visualization(
        self,
        graph: nx.DiGraph,
        output_path: str = "flows.html"
    ) -> None:
        """
        Create visualization focused on API flows (tool-to-tool connections).
        Only shows APIs that have at least one flow connection.
        
        Args:
            graph: NetworkX directed graph
            output_path: Output HTML file path
        """
        logger.info("Creating flow-focused visualization")
        
        # Extract only tool nodes
        tool_nodes = [
            node for node, data in graph.nodes(data=True)
            if data.get("node_type") == "tool"
        ]
        
        # Create subgraph with only tools and their flow connections
        flow_graph = nx.DiGraph()
        
        # First, add all flow edges
        for source, target, data in graph.edges(data=True):
            if data.get("edge_type") in ("potential_flow", "semantic_flow"):
                if source in tool_nodes and target in tool_nodes:
                    # Add nodes if not already present
                    if not flow_graph.has_node(source):
                        flow_graph.add_node(source, **graph.nodes[source])
                    if not flow_graph.has_node(target):
                        flow_graph.add_node(target, **graph.nodes[target])
                    # Add edge
                    flow_graph.add_edge(source, target, **data)
        
        logger.info(
            f"Flow graph: {flow_graph.number_of_nodes()} tools with flows, "
            f"{flow_graph.number_of_edges()} flows (filtered from {len(tool_nodes)} total tools)"
        )
        
        # Use hierarchical layout for flows
        pos = self._hierarchical_layout(flow_graph)
        
        # Create visualization
        edge_traces = self._create_edge_traces(flow_graph, pos)
        node_trace = self._create_node_trace(flow_graph, pos, show_labels=True)
        annotations = self._create_arrow_annotations(flow_graph, pos)
        
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=dict(
                    text=f"API Flow Visualization ({flow_graph.number_of_edges()} flows detected)",
                    x=0.5,
                    xanchor="center"
                ),
                showlegend=True,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="white",
                height=800,
                annotations=annotations
            )
        )
        
        fig.write_html(output_path)
        logger.info(f"Flow visualization saved to {output_path}")
    
    def create_pyvis_flow_visualization(
        self,
        graph: nx.DiGraph,
        output_path: str = "flows_pyvis.html"
    ) -> None:
        """
        Create flow visualization using PyVis (better for directed graphs).
        
        Args:
            graph: NetworkX directed graph
            output_path: Output HTML file path
        """
        logger.info("Creating PyVis flow visualization")
        
        # Extract only tool nodes with flows
        tool_nodes = [
            node for node, data in graph.nodes(data=True)
            if data.get("node_type") == "tool"
        ]
        
        # Create subgraph with only tools and their flow connections
        flow_graph = nx.DiGraph()
        
        for source, target, data in graph.edges(data=True):
            if data.get("edge_type") in ("potential_flow", "semantic_flow"):
                if source in tool_nodes and target in tool_nodes:
                    if not flow_graph.has_node(source):
                        flow_graph.add_node(source, **graph.nodes[source])
                    if not flow_graph.has_node(target):
                        flow_graph.add_node(target, **graph.nodes[target])
                    flow_graph.add_edge(source, target, **data)
        
        logger.info(
            f"PyVis flow graph: {flow_graph.number_of_nodes()} tools, "
            f"{flow_graph.number_of_edges()} flows"
        )
        
        # Create PyVis network
        net = Network(
            height="900px",
            width="100%",
            directed=True,
            notebook=False,
            bgcolor="#ffffff",
            font_color="#000000"
        )
        
        # Configure physics for hierarchical layout
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "hierarchicalRepulsion": {
              "centralGravity": 0.2,
              "springLength": 100,
              "springConstant": 0.02,
              "nodeDistance": 120,
              "damping": 0.09
            },
            "solver": "hierarchicalRepulsion"
          },
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "LR",
              "sortMethod": "directed",
              "levelSeparation": 150,
              "nodeSpacing": 80,
              "treeSpacing": 100
            }
          },
          "edges": {
            "smooth": {
              "type": "cubicBezier",
              "forceDirection": "horizontal",
              "roundness": 0.4
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 1.0
              }
            },
            "width": 2
          },
          "nodes": {
            "shape": "box",
            "margin": 8
          }
        }
        """)
        
        # Identify source nodes
        source_nodes = self._identify_source_nodes(flow_graph)
        
        # System colors
        system_colors = {
            "fms": "#3498DB",    # Blue
            "hq": "#E74C3C",     # Red
            "wms": "#F39C12",    # Orange
            "hrms": "#9B59B6"    # Purple
        }
        
        # Add nodes
        for node, data in flow_graph.nodes(data=True):
            tool_name = data.get("tool_name", node)
            source_file = data.get("source_file", "unknown")
            
            # Color based on system
            base_color = system_colors.get(source_file, "#95A5A6")
            
            # Make source nodes brighter
            if node in source_nodes:
                color = base_color
                title_prefix = f"🟢 SOURCE [{source_file.upper()}]"
                border_color = "#2ECC71"
                border_width = 4
            else:
                color = base_color
                title_prefix = f"[{source_file.upper()}]"
                border_color = "#34495E"
                border_width = 2
            
            # Create hover title
            input_keys = data.get("input_keys", [])
            output_keys = data.get("output_keys", [])
            
            title = f"{title_prefix} {tool_name}\n"
            title += f"System: {source_file}\n"
            title += f"Endpoint: {data.get('api_endpoint', 'N/A')}\n"
            
            if input_keys:
                title += f"\nInputs ({len(input_keys)}): {', '.join(input_keys[:5])}"
                if len(input_keys) > 5:
                    title += f"... +{len(input_keys)-5} more"
            
            if output_keys:
                title += f"\nOutputs ({len(output_keys)}): {', '.join(output_keys[:5])}"
                if len(output_keys) > 5:
                    title += f"... +{len(output_keys)-5} more"
            
            net.add_node(
                node,
                label=tool_name[:30],
                title=title,
                color={"background": color, "border": border_color},
                borderWidth=border_width,
                size=25,
                font={"size": 11, "color": "#000000"}
            )
        
        # Add edges
        for source, target, data in flow_graph.edges(data=True):
            edge_type = data.get("edge_type", "unknown")
            matching_param = data.get("matching_param", "")
            confidence = data.get("confidence", 0.0)
            
            # Edge color based on type
            if edge_type == "semantic_flow":
                color = "#F77F00"  # Orange
            else:
                color = "#E63946"  # Red
            
            title = f"{edge_type}\nParameter: {matching_param}\nConfidence: {confidence:.2f}"
            
            net.add_edge(
                source,
                target,
                title=title,
                color=color,
                width=2
            )
        
        # Save
        net.save_graph(output_path)
        logger.info(f"PyVis flow visualization saved to {output_path}")
    
    def apply_layout(
        self,
        graph: nx.DiGraph,
        layout: str = "spring"
    ) -> Dict[str, Tuple[float, float]]:
        """
        Apply graph layout algorithm.
        
        Args:
            graph: NetworkX directed graph
            layout: Layout algorithm name
            
        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        if layout == "spring":
            return nx.spring_layout(graph, k=0.5, iterations=50)
        elif layout == "circular":
            return nx.circular_layout(graph)
        elif layout == "kamada_kawai":
            return nx.kamada_kawai_layout(graph)
        else:
            logger.warning(f"Unknown layout '{layout}', using spring")
            return nx.spring_layout(graph)
    
    def _hierarchical_layout(self, graph: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """Create hierarchical layout with layers based on flow depth."""
        pos = {}
        
        # Identify source nodes (no incoming flows)
        source_nodes = self._identify_source_nodes(graph)
        
        # Perform topological sort to get layers
        layers = self._compute_layers(graph, source_nodes)
        
        # Assign positions based on layers
        max_nodes_in_layer = max(len(nodes) for nodes in layers.values()) if layers else 1
        
        for layer_idx, nodes in sorted(layers.items()):
            num_nodes = len(nodes)
            
            # Center nodes vertically with more spacing
            start_y = -(num_nodes - 1) * 4.0 / 2
            
            for i, node in enumerate(sorted(nodes)):
                x = layer_idx * 15.0  # Much larger horizontal spacing
                y = start_y + i * 4.0  # Much larger vertical spacing
                pos[node] = (x, y)
        
        logger.info(f"Hierarchical layout: {len(layers)} layers, max {max_nodes_in_layer} nodes per layer")
        return pos
    
    def _compute_layers(self, graph: nx.DiGraph, source_nodes: set) -> Dict[int, List[str]]:
        """Compute layers for hierarchical layout based on flow depth."""
        layers = {}
        visited = set()
        
        # BFS to assign layers
        current_layer = list(source_nodes)
        layer_idx = 0
        
        while current_layer:
            layers[layer_idx] = []
            next_layer = []
            
            for node in current_layer:
                if node not in visited:
                    visited.add(node)
                    layers[layer_idx].append(node)
                    
                    # Add successors to next layer
                    for _, target, data in graph.out_edges(node, data=True):
                        if data.get("edge_type") in ("potential_flow", "semantic_flow"):
                            if target not in visited:
                                next_layer.append(target)
            
            current_layer = next_layer
            layer_idx += 1
        
        # Handle any disconnected nodes
        all_nodes = set(graph.nodes())
        unvisited = all_nodes - visited
        if unvisited:
            layers[layer_idx] = list(unvisited)
        
        return layers
    
    def _create_edge_traces(
        self,
        graph: nx.DiGraph,
        pos: Dict[str, Tuple[float, float]]
    ) -> List[go.Scatter]:
        """Create Plotly traces for edges grouped by type."""
        edge_traces = []
        edge_groups: Dict[str, List[Tuple[str, str, Dict]]] = {}
        
        # Group edges by type
        for source, target, data in graph.edges(data=True):
            edge_type = data.get("edge_type", "unknown")
            if edge_type not in edge_groups:
                edge_groups[edge_type] = []
            edge_groups[edge_type].append((source, target, data))
        
        # Create trace for each edge type
        for edge_type, edges in edge_groups.items():
            edge_x = []
            edge_y = []
            
            for source, target, data in edges:
                if source in pos and target in pos:
                    x0, y0 = pos[source]
                    x1, y1 = pos[target]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            color = self.EDGE_COLORS.get(edge_type, "#888888")
            
            trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=1, color=color),
                hoverinfo="none",
                name=edge_type.replace("_", " ").title(),
                showlegend=True
            )
            edge_traces.append(trace)
        
        return edge_traces
    
    def _create_arrow_annotations(
        self,
        graph: nx.DiGraph,
        pos: Dict[str, Tuple[float, float]]
    ) -> List[Dict]:
        """Create arrow annotations for directed edges."""
        annotations = []
        
        for source, target, data in graph.edges(data=True):
            if source in pos and target in pos:
                x0, y0 = pos[source]
                x1, y1 = pos[target]
                
                # Calculate arrow position (90% along the edge, closer to target)
                arrow_x = x0 + 0.9 * (x1 - x0)
                arrow_y = y0 + 0.9 * (y1 - y0)
                
                edge_type = data.get("edge_type", "unknown")
                color = self.EDGE_COLORS.get(edge_type, "#888888")
                
                # Smaller arrows for flow edges only
                if edge_type in ("potential_flow", "semantic_flow"):
                    annotation = dict(
                        x=arrow_x,
                        y=arrow_y,
                        ax=x0,
                        ay=y0,
                        xref="x",
                        yref="y",
                        axref="x",
                        ayref="y",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=0.5,
                        arrowwidth=1.0,
                        arrowcolor=color,
                        opacity=0.4
                    )
                    annotations.append(annotation)
        
        return annotations
    
    def _create_node_trace(
        self,
        graph: nx.DiGraph,
        pos: Dict[str, Tuple[float, float]],
        show_labels: bool
    ) -> go.Scatter:
        """Create Plotly trace for nodes."""
        node_x = []
        node_y = []
        node_colors = []
        node_text = []
        node_hover = []
        
        # Identify source nodes (nodes with no incoming flow edges)
        source_nodes = self._identify_source_nodes(graph)
        
        for node, data in graph.nodes(data=True):
            if node in pos:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Color by node type and source status
                node_type = data.get("node_type", "unknown")
                if node_type == "tool" and node in source_nodes:
                    # Source nodes are green
                    color = "#2ECC71"
                else:
                    color = self.NODE_COLORS.get(node_type, "#999999")
                node_colors.append(color)
                
                # Label - truncate long names
                if show_labels and node_type == "tool":
                    label = data.get("tool_name", node)
                    # Truncate if too long
                    if len(label) > 25:
                        label = label[:22] + "..."
                    node_text.append(label)
                else:
                    node_text.append("")
                
                # Hover info
                hover_info = self._create_hover_text(node, data, node in source_nodes)
                node_hover.append(hover_info)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text" if show_labels else "markers",
            text=node_text,
            textposition="middle right",  # Position text to the right of nodes
            textfont=dict(size=9),
            hovertext=node_hover,
            hoverinfo="text",
            marker=dict(
                size=12,
                color=node_colors,
                line=dict(width=2, color="white")
            ),
            name="Nodes",
            showlegend=False
        )
        
        return node_trace
    
    def _identify_source_nodes(self, graph: nx.DiGraph) -> set:
        """Identify source nodes (no incoming flow edges)."""
        source_nodes = set()
        
        for node, data in graph.nodes(data=True):
            if data.get("node_type") == "tool":
                # Check if node has any incoming flow edges
                has_incoming_flow = False
                for _, target, edge_data in graph.in_edges(node, data=True):
                    if edge_data.get("edge_type") in ("potential_flow", "semantic_flow"):
                        has_incoming_flow = True
                        break
                
                if not has_incoming_flow:
                    source_nodes.add(node)
        
        return source_nodes
    
    def _create_hover_text(self, node_id: str, data: Dict, is_source: bool = False) -> str:
        """Create hover text for a node."""
        node_type = data.get("node_type", "unknown")
        
        if node_type == "tool":
            lines = [
                f"<b>{data.get('tool_name', node_id)}</b>",
                f"Type: API Tool {'(SOURCE)' if is_source else ''}",
                f"Endpoint: {data.get('api_endpoint', 'N/A')}",
                f"Source: {data.get('source_file', 'N/A')}",
                f"Status: {data.get('status_code', 'N/A')}"
            ]
            
            # Add input/output keys if available
            input_keys = data.get("input_keys", [])
            output_keys = data.get("output_keys", [])
            
            if input_keys:
                lines.append(f"<br><b>Inputs ({len(input_keys)}):</b>")
                lines.append(", ".join(input_keys[:5]))  # Show first 5
                if len(input_keys) > 5:
                    lines.append(f"... and {len(input_keys) - 5} more")
            
            if output_keys:
                lines.append(f"<br><b>Outputs ({len(output_keys)}):</b>")
                lines.append(", ".join(output_keys[:5]))  # Show first 5
                if len(output_keys) > 5:
                    lines.append(f"... and {len(output_keys) - 5} more")
        else:
            lines = [
                f"<b>{data.get('param_name', node_id)}</b>",
                f"Type: {node_type.replace('_', ' ').title()}"
            ]
        
        return "<br>".join(lines)
    
    def get_graph_statistics(self, graph: nx.DiGraph) -> Dict[str, any]:
        """
        Get statistics about the graph.
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            Dictionary with graph statistics
        """
        tool_nodes = [
            node for node, data in graph.nodes(data=True)
            if data.get("node_type") == "tool"
        ]
        
        param_nodes = [
            node for node, data in graph.nodes(data=True)
            if data.get("node_type") in ("input_param", "output_param")
        ]
        
        flow_edges = [
            (s, t) for s, t, d in graph.edges(data=True)
            if d.get("edge_type") in ("potential_flow", "semantic_flow")
        ]
        
        return {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "tool_nodes": len(tool_nodes),
            "parameter_nodes": len(param_nodes),
            "flow_connections": len(flow_edges),
            "density": nx.density(graph),
            "is_connected": nx.is_weakly_connected(graph)
        }
