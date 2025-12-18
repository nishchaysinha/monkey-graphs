"""Tests for CSV parsing functionality."""

import tempfile
from pathlib import Path

import pytest

from src.csv_parser import CSVParser


class TestCSVParser:
    """Test CSV parsing."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = CSVParser()
    
    def test_parse_valid_csv(self) -> None:
        """Test parsing a valid CSV file."""
        csv_content = """tool_name,api_endpoint,input_payload,output_response
get_user,/api/users,"{""id"": 1}","{""name"": ""John""}"
create_user,/api/users,"{""name"": ""Jane""}","{""id"": 2}"
"""
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            records = self.parser.parse_file(temp_path)
            
            assert len(records) == 2
            assert records[0].tool_name == "get_user"
            assert records[0].api_endpoint == "/api/users"
            assert records[1].tool_name == "create_user"
        finally:
            Path(temp_path).unlink()
    
    def test_parse_missing_file(self) -> None:
        """Test handling of missing file."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("nonexistent.csv")
    
    def test_parse_missing_columns(self) -> None:
        """Test handling of missing required columns."""
        csv_content = """tool_name,api_endpoint
get_user,/api/users
"""
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing required columns"):
                self.parser.parse_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_skip_empty_tool_name(self) -> None:
        """Test skipping rows with empty tool_name."""
        csv_content = """tool_name,api_endpoint,input_payload,output_response
get_user,/api/users,"{""id"": 1}","{""name"": ""John""}"
,/api/invalid,"{}","{}"
"""
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            records = self.parser.parse_file(temp_path)
            assert len(records) == 1
            assert records[0].tool_name == "get_user"
        finally:
            Path(temp_path).unlink()
