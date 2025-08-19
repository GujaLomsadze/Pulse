from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from api.schemas import NodeResponse, NodeCreateRequest, NodeUpdateRequest, NodeDetailResponse
from api.dependencies import get_graph_service

router = APIRouter()

@router.get("/", response_model=List[NodeResponse])
async def list_nodes(
    node_type: Optional[str] = None,
    graph_service = Depends(get_graph_service)
):
    """List all nodes, optionally filtered by type."""
    nodes = graph_service.get_nodes(node_type)
    return nodes

@router.get("/{node_id}", response_model=NodeDetailResponse)
async def get_node(node_id: str, graph_service = Depends(get_graph_service)):
    """Get detailed information about a specific node."""
    node = graph_service.get_node_details(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return node

@router.post("/", response_model=NodeResponse)
async def create_node(
    node: NodeCreateRequest,
    graph_service = Depends(get_graph_service)
):
    """Create a new node."""
    try:
        return graph_service.create_node(node)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: str,
    update: NodeUpdateRequest,
    graph_service = Depends(get_graph_service)
):
    """Update an existing node."""
    try:
        return graph_service.update_node(node_id, update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{node_id}")
async def delete_node(node_id: str, graph_service = Depends(get_graph_service)):
    """Delete a node and its connections."""
    try:
        graph_service.delete_node(node_id)
        return {"message": f"Node {node_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{node_id}/dependencies")
async def get_node_dependencies(
    node_id: str,
    graph_service = Depends(get_graph_service)
):
    """Get all dependencies of a node."""
    deps = graph_service.get_dependencies(node_id)
    if deps is None:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return {"node_id": node_id, "dependencies": deps}

@router.get("/{node_id}/dependents")
async def get_node_dependents(
    node_id: str,
    graph_service = Depends(get_graph_service)
):
    """Get all nodes that depend on this node."""
    deps = graph_service.get_dependents(node_id)
    if deps is None:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return {"node_id": node_id, "dependents": deps}
