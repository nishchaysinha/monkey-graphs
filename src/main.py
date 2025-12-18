"""CLI entry point for API Graph Builder."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .csv_parser import CSVParser
from .export_engine import ExportEngine
from .flow_detector import FlowDetector
from .graph_builder import GraphBuilder
from .visualizer import Visualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="API Graph Builder - Transform CSV API documentation into graph representations"
    )
    
    parser.add_argument(
        "--input",
        "-i",
        nargs="+",
        required=True,
        help="Input CSV file(s) containing API documentation"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        default="graph.json",
        help="Output file path (default: graph.json)"
    )
    
    parser.add_argument(
        "--export",
        "-e",
        choices=["json", "graphml", "dot", "neo4j"],
        default="json",
        help="Export format (default: json)"
    )
    
    parser.add_argument(
        "--detect-flows",
        action="store_true",
        help="Detect potential data flows between APIs"
    )
    
    parser.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=0.8,
        help="Fuzzy matching threshold for flow detection (0.0-1.0, default: 0.8)"
    )
    
    parser.add_argument(
        "--enable-fuzzy",
        action="store_true",
        help="Enable fuzzy parameter matching (disabled by default to avoid false positives)"
    )
    
    parser.add_argument(
        "--semantic-matching",
        action="store_true",
        help="Enable AI-powered semantic parameter matching using Gemini (requires GEMINI_API_KEY)"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate interactive HTML visualization"
    )
    
    parser.add_argument(
        "--viz-output",
        default="graph.html",
        help="Visualization output path (default: graph.html)"
    )
    
    parser.add_argument(
        "--viz-layout",
        choices=["spring", "circular", "kamada_kawai"],
        default="spring",
        help="Visualization layout algorithm (default: spring)"
    )
    
    parser.add_argument(
        "--flow-viz",
        action="store_true",
        help="Create flow-focused visualization (tool-to-tool connections only)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Parse CSV files
        logger.info(f"Parsing {len(args.input)} CSV file(s)")
        parser = CSVParser()
        records = parser.parse_multiple(args.input)
        
        if not records:
            logger.error("No API records found in input files")
            return 1
        
        # Build graph
        logger.info("Building graph structure")
        builder = GraphBuilder()
        graph = builder.build_from_records(records)
        
        # Detect flows if requested
        if args.detect_flows:
            logger.info("Detecting potential data flows (exact matches only)")
            detector = FlowDetector(
                fuzzy_threshold=args.fuzzy_threshold,
                enable_fuzzy=args.enable_fuzzy
            )
            flows = detector.detect_flows(graph)
            detector.add_flow_edges(graph, flows)
        
        # Semantic matching with Gemini AI
        if args.semantic_matching:
            logger.info("Running semantic analysis with Gemini AI")
            from .semantic_matcher import SemanticMatcher
            
            matcher = SemanticMatcher()
            semantic_matches = matcher.analyze_graph(graph)
            matcher.add_semantic_edges(graph, semantic_matches)
            
            logger.info(f"Found {len(semantic_matches)} semantic matches")
        
        # Export graph
        logger.info(f"Exporting graph in {args.export} format")
        exporter = ExportEngine()
        
        if args.export == "json":
            exporter.export_json(graph, args.output)
        elif args.export == "graphml":
            exporter.export_graphml(graph, args.output)
        elif args.export == "dot":
            exporter.export_dot(graph, args.output)
        elif args.export == "neo4j":
            exporter.export_neo4j_cypher(graph, args.output)
        
        logger.info(f"Successfully exported graph to {args.output}")
        logger.info(
            f"Graph statistics: {graph.number_of_nodes()} nodes, "
            f"{graph.number_of_edges()} edges"
        )
        
        # Generate visualization if requested
        if args.visualize or args.flow_viz:
            from .visualizer import Visualizer
            visualizer = Visualizer()
            
            if args.flow_viz:
                logger.info("Generating PyVis flow visualization (better for directed graphs)")
                visualizer.create_pyvis_flow_visualization(graph, args.viz_output)
            else:
                logger.info("Generating interactive visualization")
                visualizer.create_interactive_plot(
                    graph,
                    args.viz_output,
                    layout=args.viz_layout
                )
            
            logger.info(f"Visualization saved to {args.viz_output}")
            
            # Print statistics
            stats = visualizer.get_graph_statistics(graph)
            logger.info(f"Graph statistics:")
            logger.info(f"  - Tool nodes: {stats['tool_nodes']}")
            logger.info(f"  - Parameter nodes: {stats['parameter_nodes']}")
            logger.info(f"  - Flow connections: {stats['flow_connections']}")
            logger.info(f"  - Graph density: {stats['density']:.4f}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
