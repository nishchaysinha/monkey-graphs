"""CSV parsing utilities for API documentation."""

import logging
from pathlib import Path
from typing import List

import pandas as pd

from .models import APIRecord

logger = logging.getLogger(__name__)


class CSVParser:
    """Parse CSV files containing API documentation."""
    
    REQUIRED_COLUMNS = {"tool_name", "api_endpoint", "input_payload", "output_response"}
    OPTIONAL_COLUMNS = {"status_code", "success", "curl_command", "timestamp"}
    
    def parse_file(self, file_path: str) -> List[APIRecord]:
        """
        Parse a single CSV file and return list of API records.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of APIRecord objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV file {file_path}: {e}")
            raise ValueError(f"Malformed CSV file: {file_path}") from e
        
        # Validate schema
        if not self.validate_schema(df):
            missing = self.REQUIRED_COLUMNS - set(df.columns)
            raise ValueError(f"Missing required columns in {file_path}: {missing}")
        
        # Extract source filename without extension
        source_file = path.stem
        
        # Convert to APIRecord objects
        records: List[APIRecord] = []
        
        for _, row in df.iterrows():
            # Skip rows with empty tool_name
            if pd.isna(row.get("tool_name")) or not str(row.get("tool_name")).strip():
                logger.warning(f"Skipping row with empty tool_name in {file_path}")
                continue
            
            record = APIRecord(
                tool_name=str(row["tool_name"]).strip(),
                api_endpoint=str(row["api_endpoint"]).strip(),
                input_payload=str(row["input_payload"]) if pd.notna(row["input_payload"]) else "",
                output_response=str(row["output_response"]) if pd.notna(row["output_response"]) else "",
                status_code=int(row["status_code"]) if pd.notna(row.get("status_code")) else None,
                success=bool(row["success"]) if pd.notna(row.get("success")) else None,
                curl_command=str(row["curl_command"]) if pd.notna(row.get("curl_command")) else None,
                timestamp=str(row["timestamp"]) if pd.notna(row.get("timestamp")) else None,
                source_file=source_file
            )
            records.append(record)
        
        logger.info(f"Parsed {len(records)} API records from {file_path}")
        return records
    
    def parse_multiple(self, file_paths: List[str]) -> List[APIRecord]:
        """
        Parse multiple CSV files and return combined records.
        
        Args:
            file_paths: List of CSV file paths
            
        Returns:
            Combined list of APIRecord objects
        """
        all_records: List[APIRecord] = []
        
        for file_path in file_paths:
            try:
                records = self.parse_file(file_path)
                all_records.extend(records)
            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Skipping file {file_path}: {e}")
                continue
        
        logger.info(f"Parsed total of {len(all_records)} API records from {len(file_paths)} files")
        return all_records
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        Validate that CSV has required columns.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if all required columns present, False otherwise
        """
        return self.REQUIRED_COLUMNS.issubset(set(df.columns))
