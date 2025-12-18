"""Integration tests for end-to-end workflows."""

import tempfile
from pathlib import Path

import pytest

from src.csv_parser import CSVParser
from src.export_engine import ExportEngine
from src.flow_detector import FlowDetector
from src.graph_builder import GraphBuilder


class TestIntegration:
    """Test end-to-end workflows."""
    
    def test_csv_to_graph_to_json(self) -> None:
        """Test complete workflow: CSV -> Graph -> JSON export."""
        # Create test CSV
        csv_content = """tool_name,api_endpoint,input_payload,output_response,status_code
get_user,/api/users,"{""user_id"": 1}","{""name"": ""John"", ""email"": ""john@example.com""}",200
send_email,/api/email,"{""email"": ""test@example.com"", ""subject"": ""Test""}","{""message_id"": ""123""}",200
"""
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            # Parse CSV
            parser = CSVParser()
            records = parser.parse_file(csv_path)
            assert len(records) == 2
            
            # Build graph
            builder = GraphBuilder()
            graph = builder.build_from_records(records)
            
            # Verify graph structure
            assert graph.number_of_nodes() > 0
            assert graph.number_of_edges() > 0
            
            # Verify tool nodes exist
            tool_nodes = builder.get_tool_nodes()
            assert len(tool_nodes) == 2
            
            # Export to JSON
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json_path = f.name
            
            exporter = ExportEngine()
            exporter.export_json(graph, json_path)
            
            # Verify JSON file was created
            assert Path(json_path).exists()
            assert Path(json_path).stat().st_size > 0
            
            Path(json_path).unlink()
        
        finally:
            Path(csv_path).unlink()
    
    def test_flow_detection(self) -> None:
        """Test flow detection between APIs."""
        # Create test CSV with matching parameters
        csv_content = """tool_name,api_endpoint,input_payload,output_response
get_user,/api/users,"{}","{""user_id"": 1, ""email"": ""test@example.com""}"
send_email,/api/email,"{""email"": ""test@example.com""}","{""status"": ""sent""}"
"""
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            csv_path = f.name
        
        try:
            # Parse and build graph
            parser = CSVParser()
            records = parser.parse_file(csv_path)
            
            builder = GraphBuilder()
            graph = builder.build_from_records(records)
            
            # Detect flows
            detector = FlowDetector()
            flows = detector.detect_flows(graph)
            
            # Should detect email parameter match
            assert len(flows) > 0
            
            # Verify flow properties
            email_flows = [f for f in flows if "email" in f.matching_param]
            assert len(email_flows) > 0
            assert email_flows[0].confidence == 1.0  # Exact match
            assert email_flows[0].match_type == "exact"
        
        finally:
            Path(csv_path).unlink()
