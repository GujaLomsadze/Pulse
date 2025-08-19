import yaml
from typing import Dict, Any, List, Union
from pathlib import Path

from src.graph.node import Node
from src.graph.edge import Edge
from src.graph.graph import Graph



class YAMLParser:
    """
    Parser for YAML-based graph definitions.

    Supports two formats:
    1. Simple format: Just nodes and dependencies lists
    2. Extended format: Full control over metadata
    """

    @staticmethod
    def parse_file(filepath: Union[str, Path]) -> Graph:
        """
        Parse a YAML file and build a graph.

        Args:
            filepath: Path to the YAML file

        Returns:
            Graph object built from the YAML definition
        """
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return YAMLParser.parse_dict(data)

    @staticmethod
    def parse_string(yaml_content: str) -> Graph:
        """
        Parse a YAML string and build a graph.

        Args:
            yaml_content: YAML content as a string

        Returns:
            Graph object built from the YAML definition
        """
        data = yaml.safe_load(yaml_content)
        return YAMLParser.parse_dict(data)

    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> Graph:
        """
        Parse a dictionary (from YAML) and build a graph.

        Args:
            data: Dictionary containing nodes and dependencies

        Returns:
            Graph object built from the definition
        """
        graph = Graph()

        # Parse nodes
        nodes_data = data.get('nodes', [])
        for node_def in nodes_data:
            node = YAMLParser._parse_node(node_def)
            graph.add_node(node)

        # Parse dependencies/edges
        dependencies = data.get('dependencies', data.get('edges', []))
        for dep_def in dependencies:
            edge = YAMLParser._parse_dependency(dep_def)
            graph.add_edge(edge)

        return graph

    @staticmethod
    def _parse_node(node_def: Union[Dict, str]) -> Node:
        """
        Parse a node definition.

        Supports:
        - String format: "id:type" or just "id" (defaults to service)
        - Dict format: {"id": "...", "type": "...", "metadata": {...}}
        """
        if isinstance(node_def, str):
            # Simple string format
            if ':' in node_def:
                node_id, node_type = node_def.split(':', 1)
            else:
                node_id = node_def
                node_type = 'service'

            return Node(id=node_id.strip(), type=node_type.strip())

        elif isinstance(node_def, dict):
            # Dictionary format
            node_id = node_def.get('id')
            if not node_id:
                raise ValueError("Node definition missing 'id' field")

            node_type = node_def.get('type', 'service')
            metadata = node_def.get('metadata', {})

            # Include any extra fields as metadata
            for key, value in node_def.items():
                if key not in ['id', 'type', 'metadata']:
                    metadata[key] = value

            return Node(id=node_id, type=node_type, metadata=metadata)

        else:
            raise ValueError(f"Invalid node definition: {node_def}")

    @staticmethod
    def _parse_dependency(dep_def: Union[Dict, str, List]) -> Edge:
        """
        Parse a dependency/edge definition.

        Supports:
        - String format: "source -> target"
        - List format: ["source", "target"]
        - Dict format: {"source": "...", "target": "...", "metadata": {...}}
        """
        if isinstance(dep_def, str):
            # String format with arrow
            if '->' in dep_def:
                source, target = dep_def.split('->', 1)
                return Edge(source=source.strip(), target=target.strip())
            else:
                raise ValueError(f"Invalid dependency string format: {dep_def}")

        elif isinstance(dep_def, list):
            # List format [source, target]
            if len(dep_def) != 2:
                raise ValueError(f"Dependency list must have exactly 2 elements: {dep_def}")
            return Edge(source=dep_def[0], target=dep_def[1])

        elif isinstance(dep_def, dict):
            # Dictionary format
            source = dep_def.get('source') or dep_def.get('from')
            target = dep_def.get('target') or dep_def.get('to')

            if not source or not target:
                raise ValueError(f"Dependency missing source or target: {dep_def}")

            metadata = dep_def.get('metadata', {})

            # Include any extra fields as metadata
            for key, value in dep_def.items():
                if key not in ['source', 'target', 'from', 'to', 'metadata']:
                    metadata[key] = value

            return Edge(source=source, target=target, metadata=metadata)

        else:
            raise ValueError(f"Invalid dependency definition: {dep_def}")
