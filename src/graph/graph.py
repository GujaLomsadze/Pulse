from collections import defaultdict, deque
from typing import Dict, List, Set, Optional, Any

import networkx as nx

from src.graph.edge import Edge
from src.graph.node import Node

from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque
import networkx as nx


class Graph:
    """
    Main graph structure holding nodes and edges with validation and query capabilities.
    """

    def __init__(self):
        """Initialize an empty graph."""
        self.nodes: Dict[str, Node] = {}
        self.edges: Set[Edge] = set()
        self._adjacency: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)
        self._nx_graph: Optional[nx.DiGraph] = None
        self._dirty = True  # Flag to rebuild NetworkX graph when needed

    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.

        Args:
            node: The Node object to add

        Raises:
            ValueError: If a node with the same ID already exists
        """
        if node.id in self.nodes:
            raise ValueError(f"Node with id '{node.id}' already exists")
        self.nodes[node.id] = node
        self._dirty = True

    def add_edge(self, edge: Edge) -> None:
        """
        Add an edge to the graph.

        Args:
            edge: The Edge object to add

        Raises:
            ValueError: If source or target node doesn't exist
        """
        if edge.source not in self.nodes:
            raise ValueError(f"Source node '{edge.source}' does not exist")
        if edge.target not in self.nodes:
            raise ValueError(f"Target node '{edge.target}' does not exist")

        if edge not in self.edges:
            self.edges.add(edge)
            self._adjacency[edge.source].add(edge.target)
            self._reverse_adjacency[edge.target].add(edge.source)
            self._dirty = True

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by its ID."""
        return self.nodes.get(node_id)

    def get_dependencies(self, node_id: str) -> Set[str]:
        """
        Get all nodes that the given node depends on (outgoing edges).

        Args:
            node_id: The ID of the node

        Returns:
            Set of node IDs that this node depends on
        """
        return self._adjacency.get(node_id, set())

    def get_dependents(self, node_id: str) -> Set[str]:
        """
        Get all nodes that depend on the given node (incoming edges).

        Args:
            node_id: The ID of the node

        Returns:
            Set of node IDs that depend on this node
        """
        return self._reverse_adjacency.get(node_id, set())

    def validate(self) -> List[str]:
        """
        Validate the graph for consistency issues.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check for orphaned edges
        for edge in self.edges:
            if edge.source not in self.nodes:
                errors.append(f"Edge references non-existent source node: {edge.source}")
            if edge.target not in self.nodes:
                errors.append(f"Edge references non-existent target node: {edge.target}")

        # Check for cycles
        cycles = self.find_cycles()
        if cycles:
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                errors.append(f"Cycle detected: {cycle_str}")

        return errors

    def find_cycles(self) -> List[List[str]]:
        """
        Find all cycles in the graph using DFS.

        Returns:
            List of cycles, where each cycle is a list of node IDs
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node_id: str) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for neighbor in self._adjacency[node_id]:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return cycles

    def topological_sort(self) -> Optional[List[str]]:
        """
        Perform topological sort on the graph.

        Returns:
            List of node IDs in topological order, or None if cycles exist
        """
        # Check for cycles first
        if self.find_cycles():
            return None

        # Kahn's algorithm
        in_degree = {node_id: len(self._reverse_adjacency[node_id])
                     for node_id in self.nodes}

        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            node_id = queue.popleft()
            result.append(node_id)

            for neighbor in self._adjacency[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result if len(result) == len(self.nodes) else None

    def get_impact_radius(self, node_id: str, max_depth: Optional[int] = None) -> Set[str]:
        """
        Get all nodes that would be impacted if the given node fails.
        Uses BFS to traverse dependents.

        Args:
            node_id: The ID of the node
            max_depth: Maximum depth to traverse (None for unlimited)

        Returns:
            Set of node IDs that would be impacted
        """
        if node_id not in self.nodes:
            return set()

        impacted = set()
        queue = deque([(node_id, 0)])
        visited = {node_id}

        while queue:
            current, depth = queue.popleft()

            if max_depth is not None and depth >= max_depth:
                continue

            for dependent in self._reverse_adjacency[current]:
                if dependent not in visited:
                    visited.add(dependent)
                    impacted.add(dependent)
                    queue.append((dependent, depth + 1))

        return impacted

    def get_critical_path(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find the shortest path between two nodes.

        Args:
            start: Starting node ID
            end: Ending node ID

        Returns:
            List of node IDs representing the path, or None if no path exists
        """
        if start not in self.nodes or end not in self.nodes:
            return None

        # BFS for shortest path
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path

            for neighbor in self._adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def to_networkx(self) -> nx.DiGraph:
        """
        Convert to NetworkX DiGraph for advanced algorithms.

        Returns:
            NetworkX directed graph representation
        """
        if self._dirty or self._nx_graph is None:
            self._nx_graph = nx.DiGraph()

            # Add nodes with attributes
            for node in self.nodes.values():
                # Combine node type and metadata, avoiding conflicts
                node_attrs = {
                    'node_type': node.type.value,  # Renamed from 'type' to avoid conflicts
                    **node.metadata
                }
                self._nx_graph.add_node(node.id, **node_attrs)

            # Add edges with attributes
            for edge in self.edges:
                self._nx_graph.add_edge(
                    edge.source,
                    edge.target,
                    **edge.metadata
                )

            self._dirty = False

        return self._nx_graph

    def stats(self) -> Dict[str, Any]:
        """
        Get basic statistics about the graph.

        Returns:
            Dictionary with graph statistics
        """
        nx_graph = self.to_networkx()

        stats = {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "is_dag": nx.is_directed_acyclic_graph(nx_graph),
            "connected_components": nx.number_weakly_connected_components(nx_graph),
            "density": nx.density(nx_graph) if len(self.nodes) > 0 else 0,
        }

        # Node type distribution
        type_dist = defaultdict(int)
        for node in self.nodes.values():
            type_dist[node.type.value] += 1
        stats["node_types"] = dict(type_dist)

        # In/out degree statistics
        if self.nodes:
            in_degrees = [len(self._reverse_adjacency[n]) for n in self.nodes]
            out_degrees = [len(self._adjacency[n]) for n in self.nodes]

            stats["avg_in_degree"] = sum(in_degrees) / len(in_degrees)
            stats["avg_out_degree"] = sum(out_degrees) / len(out_degrees)
            stats["max_in_degree"] = max(in_degrees)
            stats["max_out_degree"] = max(out_degrees)

        return stats

    def __repr__(self):
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.edges)})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "stats": self.stats()
        }