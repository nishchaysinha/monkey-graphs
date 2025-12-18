# Product Overview

## API Graph Builder

A Python tool that automatically builds graph representations and GraphRAGs from OpenAPI specifications and API documentation stored in CSV format.

## Purpose

Transforms CSV-based API documentation into queryable graph structures where:
- Nodes represent API tools and their JSON parameters
- Edges represent input/output relationships and data flows
- Semantic analysis identifies hidden connections between APIs

## Key Capabilities

- Parse CSV files containing API metadata (endpoints, payloads, responses)
- Extract and flatten nested JSON structures from API inputs/outputs
- Build directed graphs showing API dependencies and parameter relationships
- Detect potential API chains where one API's output feeds another's input
- Use AI (Gemini) to find semantic relationships between parameters
- Export graphs in multiple formats (JSON, GraphML, DOT, Neo4j Cypher)
- Generate interactive visualizations for exploring API relationships

## Target Users

Developers working with complex API ecosystems who need to:
- Understand API dependencies and data flows
- Discover which APIs can be chained together
- Document API relationships visually
- Query API capabilities programmatically
