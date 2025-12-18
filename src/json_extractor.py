"""JSON extraction and flattening utilities."""

import json
from typing import Any, Dict, List, Set


class JSONExtractor:
    """Extract and flatten JSON structures from API payloads."""
    
    def extract_keys(self, json_str: str, prefix: str = "") -> List[str]:
        """
        Extract all keys from JSON string with dot notation.
        
        Args:
            json_str: JSON string to parse
            prefix: Prefix for nested keys
            
        Returns:
            List of parameter names with dot notation for nested keys
        """
        if not json_str or json_str.strip() in ("", "null", "None"):
            return []
        
        try:
            obj = json.loads(json_str)
            return self._extract_keys_recursive(obj, prefix)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def _extract_keys_recursive(self, obj: Any, prefix: str = "") -> List[str]:
        """
        Recursively extract keys from nested structures.
        
        Args:
            obj: Python object (dict, list, or primitive)
            prefix: Current key path prefix
            
        Returns:
            List of flattened key paths
        """
        keys: List[str] = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                
                # Recursively process nested structures
                if isinstance(value, (dict, list)):
                    nested_keys = self._extract_keys_recursive(value, full_key)
                    keys.extend(nested_keys)
        
        elif isinstance(obj, list) and obj:
            # Process first element of array as representative
            if isinstance(obj[0], dict):
                array_prefix = f"{prefix}[0]" if prefix else "[0]"
                nested_keys = self._extract_keys_recursive(obj[0], array_prefix)
                keys.extend(nested_keys)
        
        return keys
    
    def flatten_json(self, obj: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        """
        Recursively flatten nested JSON objects.
        
        Args:
            obj: Dictionary to flatten
            parent_key: Parent key for nested structures
            
        Returns:
            Flattened dictionary with dot notation keys
        """
        items: List[tuple[str, Any]] = []
        
        for key, value in obj.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(self.flatten_json(value, new_key).items())
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Flatten first array element
                items.extend(self.flatten_json(value[0], f"{new_key}[0]").items())
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def infer_type(self, value: Any) -> str:
        """
        Infer data type from JSON value.
        
        Args:
            value: JSON value
            
        Returns:
            Type name as string
        """
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "unknown"
    
    def get_unique_keys(self, json_strings: List[str]) -> Set[str]:
        """
        Extract unique keys from multiple JSON strings.
        
        Args:
            json_strings: List of JSON strings
            
        Returns:
            Set of unique parameter names
        """
        all_keys: Set[str] = set()
        
        for json_str in json_strings:
            keys = self.extract_keys(json_str)
            all_keys.update(keys)
        
        return all_keys
