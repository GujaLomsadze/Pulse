from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from api.schemas import GraphResponse, GraphStatsResponse, PathResponse, ImpactAnalysisResponse
from api.dependencies import get_graph_service

router = APIRouter()

@router.get("/", response_model=GraphResponse)
async def get_graph(graph_service = Depends(get_graph_service)):
    """Get the complete graph structure."""
    try:
        return graph_service.get_graph_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=GraphStatsResponse)
async def get_graph_stats(graph_service = Depends(get_graph_service)):
    """Get graph statistics and analysis."""
    try:
        return graph_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/path")
async def find_path(
    source: str,
    target: str,
    graph_service = Depends(get_graph_service)
) -> PathResponse:
    """Find shortest path between two nodes."""
    path = graph_service.find_path(source, target)
    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"No path found from {source} to {target}"
        )
    return PathResponse(
        source=source,
        target=target,
        path=path,
        length=len(path) - 1
    )

@router.get("/impact/{node_id}")
async def analyze_impact(
    node_id: str,
    max_depth: Optional[int] = None,
    graph_service = Depends(get_graph_service)
) -> ImpactAnalysisResponse:
    """Analyze impact of node failure."""
    try:
        return graph_service.analyze_impact(node_id, max_depth)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/cycles")
async def detect_cycles(graph_service = Depends(get_graph_service)):
    """Detect cycles in the graph."""
    cycles = graph_service.find_cycles()
    return {
        "has_cycles": len(cycles) > 0,
        "cycles": cycles,
        "count": len(cycles)
    }

@router.get("/topology")
async def get_topology(graph_service = Depends(get_graph_service)):
    """Get topological sort of the graph."""
    order = graph_service.topological_sort()
    if not order:
        return {
            "is_dag": False,
            "order": None,
            "message": "Graph contains cycles"
        }
    return {
        "is_dag": True,
        "order": order,
        "levels": graph_service.calculate_levels()
    }
