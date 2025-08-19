# api/app.py
"""
FastAPI application for the Dependency Graph Monitor.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from api.middleware import setup_middleware
from api.routes import graph, nodes, metrics, websocket
from src.graph import GraphBuilder
from src.core.config import get_settings
from src.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global graph instance (will be moved to dependency injection)
current_graph = None


def initialize_sample_graph():
    """Initialize with sample data for demo."""
    global current_graph

    builder = GraphBuilder()

    # API Gateway & Frontend
    builder.add_node("nginx-lb", "loadbalancer",
                     version="1.21", max_connections=10000, ssl_enabled=True)
    builder.add_node("web-app", "service",
                     framework="react", version="18.2", team="frontend")
    builder.add_node("mobile-app", "service",
                     platform="react-native", version="0.72", team="mobile")

    # Core Services
    builder.add_node("api-gateway", "api",
                     version="2.1.0", port=8080, team="platform", sla="99.99%")
    builder.add_node("auth-service", "service",
                     framework="fastapi", team="security", critical=True, replicas=3)
    builder.add_node("user-service", "service",
                     framework="fastapi", team="identity", database="postgres")
    builder.add_node("product-service", "service",
                     framework="spring-boot", team="catalog", cache_enabled=True)
    builder.add_node("order-service", "service",
                     framework="nodejs", team="commerce", queue="rabbitmq")
    builder.add_node("payment-service", "service",
                     framework="go", team="payments", compliance="PCI-DSS")
    builder.add_node("notification-service", "service",
                     framework="python", team="engagement")

    # Data Layer
    builder.add_node("users-db", "database",
                     engine="postgresql", version="14", size="500GB", replicas=2)
    builder.add_node("products-db", "database",
                     engine="mongodb", version="6.0", sharding=True)
    builder.add_node("orders-db", "database",
                     engine="postgresql", version="14", partitioning="monthly")

    # Infrastructure
    builder.add_node("redis-cache", "cache",
                     version="7.0", mode="cluster", memory="32GB")
    builder.add_node("rabbitmq", "queue",
                     version="3.11", cluster_size=3, durable=True)
    builder.add_node("kafka", "kafka",
                     version="3.4", brokers=5, topics=["events", "logs"])
    builder.add_node("elasticsearch", "storage",
                     version="8.0", purpose="logging", retention_days=30)
    builder.add_node("prometheus", "service",
                     version="2.45", retention="15d", scrape_interval="15s")
    builder.add_node("grafana", "service",
                     version="10.0", dashboards=["system", "application", "business"])

    # Build dependency graph
    # Frontend layer
    builder.add_dependency("web-app", "nginx-lb")
    builder.add_dependency("mobile-app", "nginx-lb")
    builder.add_dependency("nginx-lb", "api-gateway", load_balanced=True)

    # API Gateway to services
    builder.add_dependency("api-gateway", "auth-service", critical_path=True)
    builder.add_dependency("api-gateway", "user-service")
    builder.add_dependency("api-gateway", "product-service")
    builder.add_dependency("api-gateway", "order-service")
    builder.add_dependency("api-gateway", "payment-service")

    # Service to database
    builder.add_dependency("user-service", "users-db", connection_pool=20)
    builder.add_dependency("user-service", "redis-cache", ttl=300)
    builder.add_dependency("auth-service", "users-db", read_only=True)
    builder.add_dependency("auth-service", "redis-cache", ttl=600)
    builder.add_dependency("product-service", "products-db")
    builder.add_dependency("product-service", "redis-cache")
    builder.add_dependency("product-service", "elasticsearch")
    builder.add_dependency("order-service", "orders-db")
    builder.add_dependency("order-service", "rabbitmq")
    builder.add_dependency("order-service", "kafka")
    builder.add_dependency("payment-service", "order-service")
    builder.add_dependency("payment-service", "kafka")
    builder.add_dependency("notification-service", "rabbitmq")
    builder.add_dependency("notification-service", "kafka")

    # Monitoring
    builder.add_dependency("api-gateway", "prometheus")
    builder.add_dependency("auth-service", "prometheus")
    builder.add_dependency("user-service", "prometheus")
    builder.add_dependency("order-service", "prometheus")
    builder.add_dependency("prometheus", "grafana")

    # Logging
    builder.add_dependency("auth-service", "elasticsearch")
    builder.add_dependency("payment-service", "elasticsearch")
    builder.add_dependency("order-service", "elasticsearch")

    current_graph = builder.build()
    logger.info(f"Initialized graph with {len(current_graph.nodes)} nodes and {len(current_graph.edges)} edges")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting Dependency Graph Monitor API")
    initialize_sample_graph()

    yield

    # Shutdown
    logger.info("Shutting down Dependency Graph Monitor API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Dependency Graph Monitor",
        description="Service dependency graph visualization and monitoring",
        version="0.1.0",
        lifespan=lifespan
    )

    # Setup middleware
    setup_middleware(app)

    # Include routers
    app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
    app.include_router(nodes.router, prefix="/api/nodes", tags=["nodes"])
    app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
    app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Dependency Graph Monitor API",
            "version": "0.1.0",
            "status": "running",
            "endpoints": {
                "/api/graph": "Graph operations",
                "/api/nodes": "Node operations",
                "/api/metrics": "Prometheus metrics",
                "/ws": "WebSocket for real-time updates",
                "/docs": "API documentation",
                "/redoc": "Alternative API documentation"
            }
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "graph_loaded": current_graph is not None,
            "nodes": len(current_graph.nodes) if current_graph else 0,
            "edges": len(current_graph.edges) if current_graph else 0
        }

    return app


# Create app instance
app = create_app()


# Make current_graph accessible to routes
def get_current_graph():
    """Dependency injection for current graph."""
    return current_graph


# Export for routes to use
__all__ = ['app', 'get_current_graph']

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
