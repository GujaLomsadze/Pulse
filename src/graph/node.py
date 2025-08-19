from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Enumeration of supported node types."""
    DATABASE = "database"
    API = "api"
    KAFKA = "kafka"
    CACHE = "cache"
    QUEUE = "queue"
    SERVICE = "service"
    STORAGE = "storage"
    LOADBALANCER = "loadbalancer"
    CUSTOM = "custom"


@dataclass
class Node:
    """
    Represents a service/component in the dependency graph.

    Attributes:
        id: Unique identifier for the node (e.g., "db01", "api-gateway")
        type: Type of the node (database, API, kafka, etc.)
        metadata: Optional key-value pairs for additional information
    """
    id: str
    type: NodeType
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize node data after initialization."""
        if not self.id:
            raise ValueError("Node id cannot be empty")

        # Convert string type to NodeType enum if necessary
        if isinstance(self.type, str):
            try:
                self.type = NodeType(self.type.lower())
            except ValueError:
                # If type doesn't match enum, use CUSTOM
                self.type = NodeType.CUSTOM
                if "original_type" not in self.metadata:
                    self.metadata["original_type"] = self.type

    def __hash__(self):
        """Make Node hashable for use in sets and as dict keys."""
        return hash(self.id)

    def __eq__(self, other):
        """Equality based on id."""
        if not isinstance(other, Node):
            return False
        return self.id == other.id

    def __repr__(self):
        return f"Node(id='{self.id}', type={self.type.value})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type.value,
            "metadata": self.metadata
        }