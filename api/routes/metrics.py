from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

router = APIRouter()

# Define metrics
request_count = Counter(
    'graph_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'graph_api_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

graph_nodes = Gauge('graph_nodes_total', 'Total number of nodes in the graph')
graph_edges = Gauge('graph_edges_total', 'Total number of edges in the graph')
graph_components = Gauge('graph_components_total', 'Number of connected components')


@router.get("/")
async def get_metrics():
    """Expose Prometheus metrics."""
    # Update graph metrics
    from api.app import get_current_graph
    graph = get_current_graph()

    if graph:
        graph_nodes.set(len(graph.nodes))
        graph_edges.set(len(graph.edges))
        stats = graph.stats()
        graph_components.set(stats.get('connected_components', 0))

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/health")
async def metrics_health():
    """Health check for metrics endpoint."""
    return {"status": "healthy", "timestamp": time.time()}