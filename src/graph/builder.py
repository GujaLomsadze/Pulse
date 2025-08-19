from typing import Dict, Union, List

from src.graph.edge import Edge
from src.graph.graph import Graph
from src.graph.node import Node


class GraphBuilder:
    """
    Fluent API for building graphs programmatically.

    Example:
        graph = (GraphBuilder()
                .add_node("api", "api")
                .add_node("db", "database")
                .add_dependency("api", "db")
                .build())
    """

    def __init__(self):
        """Initialize a new GraphBuilder."""
        self.graph = Graph()

    def add_node(self, node_id: str, node_type: str = "service",
                 **metadata) -> 'GraphBuilder':
        """
        Add a node to the graph.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node
            **metadata: Additional key-value pairs for metadata

        Returns:
            Self for method chaining
        """
        node = Node(id=node_id, type=node_type, metadata=metadata)
        self.graph.add_node(node)
        return self

    def add_nodes(self, *nodes: Union[str, Dict, Node]) -> 'GraphBuilder':
        """
        Add multiple nodes at once.

        Args:
            *nodes: Variable number of node definitions

        Returns:
            Self for method chaining
        """
        for node_def in nodes:
            if isinstance(node_def, Node):
                self.graph.add_node(node_def)
            elif isinstance(node_def, dict):
                self.add_node(**node_def)
            elif isinstance(node_def, str):
                self.add_node(node_def)
            else:
                raise ValueError(f"Invalid node definition: {node_def}")
        return self

    def add_dependency(self, source: str, target: str,
                       **metadata) -> 'GraphBuilder':
        """
        Add a dependency (edge) between two nodes.

        Args:
            source: ID of the source node
            target: ID of the target node
            **metadata: Additional key-value pairs for metadata

        Returns:
            Self for method chaining
        """
        edge = Edge(source=source, target=target, metadata=metadata)
        self.graph.add_edge(edge)
        return self

    def add_dependencies(self, *dependencies: Union[str, List, Dict, Edge]) -> 'GraphBuilder':
        """
        Add multiple dependencies at once.

        Args:
            *dependencies: Variable number of dependency definitions

        Returns:
            Self for method chaining
        """
        for dep_def in dependencies:
            if isinstance(dep_def, Edge):
                self.graph.add_edge(dep_def)
            elif isinstance(dep_def, dict):
                self.add_dependency(**dep_def)
            elif isinstance(dep_def, str) and '->' in dep_def:
                source, target = dep_def.split('->', 1)
                self.add_dependency(source.strip(), target.strip())
            elif isinstance(dep_def, (list, tuple)) and len(dep_def) == 2:
                self.add_dependency(dep_def[0], dep_def[1])
            else:
                raise ValueError(f"Invalid dependency definition: {dep_def}")
        return self

    def add_chain(self, *node_ids: str) -> 'GraphBuilder':
        """
        Add a chain of dependencies: n1 -> n2 -> n3 -> ...

        Args:
            *node_ids: Node IDs in dependency order

        Returns:
            Self for method chaining
        """
        for i in range(len(node_ids) - 1):
            self.add_dependency(node_ids[i], node_ids[i + 1])
        return self

    def add_fanout(self, source: str, *targets: str) -> 'GraphBuilder':
        """
        Add multiple dependencies from one source to many targets.

        Args:
            source: Source node ID
            *targets: Target node IDs

        Returns:
            Self for method chaining
        """
        for target in targets:
            self.add_dependency(source, target)
        return self

    def add_fanin(self, target: str, *sources: str) -> 'GraphBuilder':
        """
        Add multiple dependencies from many sources to one target.

        Args:
            target: Target node ID
            *sources: Source node IDs

        Returns:
            Self for method chaining
        """
        for source in sources:
            self.add_dependency(source, target)
        return self

    def validate(self) -> 'GraphBuilder':
        """
        Validate the graph and raise an exception if invalid.

        Returns:
            Self for method chaining

        Raises:
            ValueError: If validation fails
        """
        errors = self.graph.validate()
        if errors:
            raise ValueError(f"Graph validation failed:\n" + "\n".join(errors))
        return self

    def build(self) -> Graph:
        """
        Build and return the final graph.

        Returns:
            The constructed Graph object
        """
        return self.graph
