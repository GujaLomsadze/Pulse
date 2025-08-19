from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Edge:
    """
    Represents a dependency relationship between two nodes.

    Attributes:
        source: ID of the origin node
        target: ID of the destination node
        metadata: Optional key-value pairs (for future: latency, throughput, etc.)
    """
    source: str
    target: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate edge data after initialization."""
        if not self.source:
            raise ValueError("Edge source cannot be empty")
        if not self.target:
            raise ValueError("Edge target cannot be empty")
        if self.source == self.target:
            raise ValueError(f"Self-loops not allowed: {self.source} -> {self.target}")

    def __hash__(self):
        """Make Edge hashable for use in sets."""
        return hash((self.source, self.target))

    def __eq__(self, other):
        """Equality based on source and target."""
        if not isinstance(other, Edge):
            return False
        return self.source == other.source and self.target == other.target

    def __repr__(self):
        return f"Edge({self.source} -> {self.target})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary representation."""
        return {
            "source": self.source,
            "target": self.target,
            "metadata": self.metadata
        }
