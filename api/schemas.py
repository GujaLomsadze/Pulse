"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum

class NodeType(str, Enum):
    """Node type enumeration."""
    DATABASE = "database"
    API = "api"
    SERVICE = "service"
    CACHE = "cache"
    QUEUE = "queue"
    KAFKA = "kafka"
    STORAGE = "storage"
    LOADBALANCER = "loadbalancer"
    CUSTOM = "custom"

class NodeBase(BaseModel):
    """Base node schema."""
    id: str = Field(..., description="Unique node identifier")
    type: NodeType = Field(..., description="Node type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Node metadata")

class NodeResponse(NodeBase):
    """Node response schema."""
    label: Optional[str] = None
    group: Optional[str] = None
    level: Optional[int] = None

class NodeCreateRequest(BaseModel):
    """Create node request schema."""
    id: str
    type: NodeType
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NodeUpdateRequest(BaseModel):
    """Update node request schema."""
    type: Optional[NodeType] = None
    metadata: Optional[Dict[str, Any]] = None

class NodeDetailResponse(NodeBase):
    """Detailed node response."""
    dependencies: List[str] = []
    dependents: List[str] = []
    impact_radius: List[str] = []
    metrics: Dict[str, Any] = {}

class EdgeBase(BaseModel):
    """Base edge schema."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Edge metadata")

class EdgeResponse(EdgeBase):
    """Edge response schema."""
    id: Optional[str] = None
    label: Optional[str] = None

class EdgeCreateRequest(BaseModel):
    """Create edge request schema."""
    source: str
    target: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphResponse(BaseModel):
    """Complete graph response."""
    nodes: List[NodeResponse]
    edges: List[EdgeResponse]
    stats: Dict[str, Any] = {}

class GraphStatsResponse(BaseModel):
    """Graph statistics response."""
    node_count: int
    edge_count: int
    is_dag: bool
    connected_components: int
    density: float
    node_types: Dict[str, int]
    avg_in_degree: float
    avg_out_degree: float
    max_in_degree: int
    max_out_degree: int
    critical_nodes: List[Dict[str, Any]]
    has_cycles: bool

class PathResponse(BaseModel):
    """Path query response."""
    source: str
    target: str
    path: Optional[List[str]]
    length: Optional[int]
    message: Optional[str] = None

class ImpactAnalysisResponse(BaseModel):
    """Impact analysis response."""
    source: str
    impacted_nodes: List[str]
    impact_count: int
    max_depth: Optional[int]
    severity: str

class GraphUpdateRequest(BaseModel):
    """Update graph from YAML."""
    yaml_content: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    graph_loaded: bool
    nodes: int
    edges: int