"""Semantic parameter matching using Gemini AI."""

import json
import logging
import os
from typing import List, Optional

import networkx as nx
from dotenv import load_dotenv
from google import genai
from google.genai import types

from .models import ParameterInfo, SemanticMatch

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """Use Gemini AI to find semantic relationships between parameters."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize semantic matcher with Gemini API.
        
        Args:
            api_key: Gemini API key (or use GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found. Semantic matching will be skipped.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini AI client initialized for semantic matching")
    
    def analyze_graph(self, graph: nx.DiGraph) -> List[SemanticMatch]:
        """
        Analyze entire graph to find semantic connections in a single shot.
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            List of semantic matches found by Gemini
        """
        if not self.client:
            logger.warning("Gemini client not initialized. Skipping semantic analysis.")
            return []
        
        logger.info("Starting single-shot semantic analysis with Gemini AI")
        
        # Extract all tools with their input/output keys
        tools_data = []
        for node, data in graph.nodes(data=True):
            if data.get("node_type") == "tool":
                tools_data.append({
                    "tool_id": node,
                    "tool_name": data.get("tool_name", node),
                    "system": data.get("csv_file", "unknown"),
                    "endpoint": data.get("api_endpoint", ""),
                    "input_keys": data.get("input_keys", []),
                    "output_keys": data.get("output_keys", [])
                })
        
        logger.info(f"Analyzing {len(tools_data)} APIs in single prompt")
        
        # Single shot analysis
        matches = self.find_semantic_matches_single_shot(tools_data)
        
        logger.info(f"Total semantic matches found: {len(matches)}")
        return matches
    
    def find_semantic_matches_single_shot(
        self,
        tools_data: List[dict]
    ) -> List[SemanticMatch]:
        """
        Use Gemini to find semantic matches in a single prompt.
        
        Args:
            tools_data: List of tool dictionaries with input/output keys
            
        Returns:
            List of semantic matches
        """
        if not self.client or not tools_data:
            return []
        
        # Build single-shot prompt
        prompt = self._build_single_shot_prompt(tools_data)
        
        try:
            # Call Gemini API
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,  # Deterministic for exact matching
                    response_mime_type="application/json"
                )
            )
            
            # Parse response
            matches = self._parse_gemini_response(response.text)
            return matches
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return []
    
    def _build_single_shot_prompt(self, tools_data: List[dict]) -> str:
        """Build single-shot prompt with all tools and their parameters."""
        prompt = """You are analyzing an API ecosystem to find EXACT semantic matches between parameters.

Your task: Identify which output parameters from one API represent THE SAME DATA as input parameters in another API.

CRITICAL RULES:
1. Only match parameters that represent THE EXACT SAME FIELD/DATA
2. Consider abbreviations (e.g., "id" = "identifier")
3. Consider synonyms (e.g., "customer_name" = "client_name")
4. Consider different naming conventions (e.g., "user_id" vs "userId")
5. DO NOT match similar but different fields
6. Confidence must be >= 0.8 for a match

API Tools and their parameters:

"""
        
        # Add all tools with their input/output keys
        for tool in tools_data:
            prompt += f"\n## {tool['tool_id']}\n"
            prompt += f"System: {tool['system']}\n"
            prompt += f"Endpoint: {tool['endpoint']}\n"
            
            if tool['input_keys']:
                prompt += f"Inputs: {', '.join(tool['input_keys'][:10])}"
                if len(tool['input_keys']) > 10:
                    prompt += f" ... +{len(tool['input_keys'])-10} more"
                prompt += "\n"
            
            if tool['output_keys']:
                prompt += f"Outputs: {', '.join(tool['output_keys'][:10])}"
                if len(tool['output_keys']) > 10:
                    prompt += f" ... +{len(tool['output_keys'])-10} more"
                prompt += "\n"
        
        prompt += """

Return ONLY a JSON array of matches. Format:
[
  {
    "output_param": "order_id",
    "output_tool": "system1.create_order",
    "input_param": "order_number",
    "input_tool": "system2.track_order",
    "confidence": 0.95,
    "reasoning": "order_id and order_number represent the same order identifier"
  }
]

Return empty array [] if no confident matches found.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[SemanticMatch]:
        """Parse Gemini's JSON response into SemanticMatch objects."""
        try:
            data = json.loads(response_text)
            
            if not isinstance(data, list):
                logger.warning("Gemini response is not a list")
                return []
            
            matches = []
            for item in data:
                try:
                    match = SemanticMatch(
                        output_param=item["output_param"],
                        input_param=item["input_param"],
                        source_tool=item["output_tool"],
                        target_tool=item["input_tool"],
                        confidence=float(item["confidence"]),
                        reasoning=item["reasoning"]
                    )
                    matches.append(match)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid match: {e}")
                    continue
            
            return matches
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return []
    
    def add_semantic_edges(
        self,
        graph: nx.DiGraph,
        matches: List[SemanticMatch]
    ) -> None:
        """
        Add semantic_flow edges to the graph.
        
        Args:
            graph: NetworkX directed graph
            matches: List of semantic matches to add
        """
        for match in matches:
            graph.add_edge(
                match.source_tool,
                match.target_tool,
                edge_type="semantic_flow",
                matching_param=f"{match.output_param}~{match.input_param}",
                confidence=match.confidence,
                match_type="semantic",
                reasoning=match.reasoning
            )
        
        logger.info(f"Added {len(matches)} semantic_flow edges to graph")
