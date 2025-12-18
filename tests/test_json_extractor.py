"""Tests for JSON extraction functionality."""

import pytest

from src.json_extractor import JSONExtractor


class TestJSONExtractor:
    """Test JSON extraction and flattening."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.extractor = JSONExtractor()
    
    def test_extract_flat_json(self) -> None:
        """Test extraction from flat JSON."""
        json_str = '{"name": "test", "age": 30, "active": true}'
        keys = self.extractor.extract_keys(json_str)
        
        assert "name" in keys
        assert "age" in keys
        assert "active" in keys
        assert len(keys) == 3
    
    def test_extract_nested_json(self) -> None:
        """Test extraction from nested JSON with dot notation."""
        json_str = '{"user": {"name": "test", "address": {"city": "NYC"}}}'
        keys = self.extractor.extract_keys(json_str)
        
        assert "user" in keys
        assert "user.name" in keys
        assert "user.address" in keys
        assert "user.address.city" in keys
    
    def test_extract_array_json(self) -> None:
        """Test extraction from JSON with arrays."""
        json_str = '{"items": [{"id": 1, "name": "item1"}]}'
        keys = self.extractor.extract_keys(json_str)
        
        assert "items" in keys
        assert "items[0].id" in keys
        assert "items[0].name" in keys
    
    def test_extract_empty_json(self) -> None:
        """Test handling of empty JSON."""
        assert self.extractor.extract_keys("") == []
        assert self.extractor.extract_keys("null") == []
        assert self.extractor.extract_keys("{}") == []
    
    def test_extract_invalid_json(self) -> None:
        """Test handling of invalid JSON."""
        assert self.extractor.extract_keys("not json") == []
        assert self.extractor.extract_keys("{invalid}") == []
    
    def test_infer_type(self) -> None:
        """Test type inference."""
        assert self.extractor.infer_type(None) == "null"
        assert self.extractor.infer_type(True) == "boolean"
        assert self.extractor.infer_type(42) == "integer"
        assert self.extractor.infer_type(3.14) == "number"
        assert self.extractor.infer_type("text") == "string"
        assert self.extractor.infer_type([1, 2, 3]) == "array"
        assert self.extractor.infer_type({"key": "value"}) == "object"
    
    def test_flatten_json(self) -> None:
        """Test JSON flattening."""
        obj = {"user": {"name": "test", "age": 30}}
        flattened = self.extractor.flatten_json(obj)
        
        assert "user.name" in flattened
        assert "user.age" in flattened
        assert flattened["user.name"] == "test"
        assert flattened["user.age"] == 30
