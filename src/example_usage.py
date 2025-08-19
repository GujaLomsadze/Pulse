# example_usage.py
"""
Example usage of the graph module showing different ways to define
and work with dependency graphs.
"""

from graph import Graph, Node, Edge, GraphBuilder, YAMLParser
from graph.node import NodeType
import json


def example_1_manual_construction():
    """Example 1: Manual graph construction using basic objects."""
    print("=" * 60)
    print("Example 1: Manual Construction")
    print("=" * 60)

    # Create a graph
    graph = Graph()

    # Add nodes
    api_gateway = Node(id="api-gateway", type=NodeType.API,
                       metadata={"version": "2.1.0", "port": 8080})
    auth_service = Node(id="auth-service", type=NodeType.SERVICE,
                        metadata={"team": "security"})
    user_db = Node(id="user-db", type=NodeType.DATABASE,
                   metadata={"engine": "postgres", "version": "14"})
    cache = Node(id="redis-cache", type=NodeType.CACHE,
                 metadata={"max_memory": "2GB"})

    graph.add_node(api_gateway)
    graph.add_node(auth_service)
    graph.add_node(user_db)
    graph.add_node(cache)

    # Add edges (dependencies)
    graph.add_edge(Edge("api-gateway", "auth-service"))
    graph.add_edge(Edge("auth-service", "user-db"))
    graph.add_edge(Edge("auth-service", "redis-cache",
                        metadata={"cache_ttl": 300}))

    # Query the graph
    print(f"Graph: {graph}")
    print(f"Dependencies of auth-service: {graph.get_dependencies('auth-service')}")
    print(f"Services depending on auth-service: {graph.get_dependents('auth-service')}")
    print(f"Impact radius of user-db failure: {graph.get_impact_radius('user-db')}")
    print()


def example_2_builder_pattern():
    """Example 2: Using the GraphBuilder fluent API."""
    print("=" * 60)
    print("Example 2: GraphBuilder Pattern")
    print("=" * 60)

    graph = (GraphBuilder()
             # Add nodes with metadata
             .add_node("frontend", "service", framework="react", port=3000)
             .add_node("api", "api", framework="fastapi", port=8000)
             .add_node("worker", "service", type="celery")
             .add_node("postgres", "database", version="14")
             .add_node("redis", "cache")
             .add_node("kafka", "kafka", partitions=10)

             # Add dependencies
             .add_dependency("frontend", "api")
             .add_dependency("api", "postgres")
             .add_dependency("api", "redis")
             .add_dependency("api", "kafka")
             .add_dependency("worker", "kafka")
             .add_dependency("worker", "postgres")

             # Build the graph
             .build())

    # Display statistics
    stats = graph.stats()
    print("Graph Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Check for cycles
    cycles = graph.find_cycles()
    print(f"\nCycles detected: {cycles if cycles else 'None'}")

    # Topological sort
    topo_order = graph.topological_sort()
    if topo_order:
        print(f"Topological order: {' -> '.join(topo_order)}")
    print()


def example_3_yaml_simple():
    """Example 3: Simple YAML format."""
    print("=" * 60)
    print("Example 3: Simple YAML Format")
    print("=" * 60)

    yaml_content = """
    nodes:
      - web-app:service
      - api-gateway:api
      - user-service:service
      - order-service:service
      - payment-service:service
      - user-db:database
      - order-db:database
      - payment-db:database
      - message-queue:kafka
      - cache:cache

    dependencies:
      - web-app -> api-gateway
      - api-gateway -> user-service
      - api-gateway -> order-service
      - api-gateway -> payment-service
      - user-service -> user-db
      - user-service -> cache
      - order-service -> order-db
      - order-service -> message-queue
      - payment-service -> payment-db
      - payment-service -> message-queue
    """

    graph = YAMLParser.parse_string(yaml_content)

    print(f"Loaded graph: {graph}")
    print("\nNodes by type:")
    for node in graph.nodes.values():
        print(f"  - {node.id} ({node.type.value})")

    print("\nCritical path from web-app to user-db:")
    path = graph.get_critical_path("web-app", "user-db")
    if path:
        print(f"  {' -> '.join(path)}")
    print()


def example_4_yaml_extended():
    """Example 4: Extended YAML format with metadata."""
    print("=" * 60)
    print("Example 4: Extended YAML Format")
    print("=" * 60)

    yaml_content = """
    nodes:
      - id: nginx-lb
        type: loadbalancer
        metadata:
          version: "1.21"
          max_connections: 10000
          ssl_enabled: true

      - id: api-server-1
        type: api
        metadata:
          region: "us-east-1"
          instance_type: "t3.large"
          health_check: "/health"

      - id: api-server-2
        type: api
        metadata:
          region: "us-east-1"
          instance_type: "t3.large"
          health_check: "/health"

      - id: postgres-primary
        type: database
        metadata:
          role: "primary"
          max_connections: 200
          replication_enabled: true

      - id: postgres-replica
        type: database
        metadata:
          role: "replica"
          max_connections: 100
          lag_threshold_ms: 1000

      - id: redis-sentinel
        type: cache
        metadata:
          mode: "sentinel"
          masters: 3
          replicas: 2

    dependencies:
      - source: nginx-lb
        target: api-server-1
        metadata:
          weight: 0.5
          health_check_interval: 5

      - source: nginx-lb
        target: api-server-2
        metadata:
          weight: 0.5
          health_check_interval: 5

      - source: api-server-1
        target: postgres-primary
        metadata:
          connection_pool_size: 20
          timeout_ms: 5000

      - source: api-server-2
        target: postgres-primary
        metadata:
          connection_pool_size: 20
          timeout_ms: 5000

      - source: api-server-1
        target: redis-sentinel
        metadata:
          cache_ttl: 300
          max_retries: 3

      - source: api-server-2
        target: redis-sentinel
        metadata:
          cache_ttl: 300
          max_retries: 3

      - source: postgres-primary
        target: postgres-replica
        metadata:
          replication_type: "streaming"
          sync_mode: "async"
    """

    graph = YAMLParser.parse_string(yaml_content)

    print("Loaded complex infrastructure graph")
    print("\nNode details:")
    for node in graph.nodes.values():
        print(f"  {node.id}:")
        print(f"    Type: {node.type.value}")
        if node.metadata:
            print(f"    Metadata: {json.dumps(node.metadata, indent=6)}")

    print("\nEdge details:")
    for edge in graph.edges:
        print(f"  {edge.source} -> {edge.target}")
        if edge.metadata:
            print(f"    Metadata: {json.dumps(edge.metadata, indent=6)}")

    print("\nImpact analysis:")
    for critical_node in ["postgres-primary", "redis-sentinel", "nginx-lb"]:
        impact = graph.get_impact_radius(critical_node)
        print(f"  {critical_node} failure impacts: {impact if impact else 'No dependents'}")
    print()


def example_5_advanced_patterns():
    """Example 5: Advanced graph patterns using builder."""
    print("=" * 60)
    print("Example 5: Advanced Patterns")
    print("=" * 60)

    builder = GraphBuilder()

    # Create a microservices architecture
    # API Gateway
    builder.add_node("api-gateway", "api")

    # Service mesh
    services = ["user-service", "product-service", "order-service",
                "inventory-service", "payment-service", "notification-service"]
    for service in services:
        builder.add_node(service, "service")

    # Databases
    builder.add_node("user-db", "database")
    builder.add_node("product-db", "database")
    builder.add_node("order-db", "database")

    # Shared infrastructure
    builder.add_node("redis", "cache")
    builder.add_node("rabbitmq", "queue")
    builder.add_node("elasticsearch", "storage")

    # API Gateway fans out to all services
    builder.add_fanout("api-gateway", *services)

    # Service to database mappings
    builder.add_dependency("user-service", "user-db")
    builder.add_dependency("product-service", "product-db")
    builder.add_dependency("order-service", "order-db")
    builder.add_dependency("inventory-service", "product-db")

    # Services using cache
    builder.add_fanin("redis", "user-service", "product-service", "order-service")

    # Async messaging patterns
    builder.add_dependency("order-service", "rabbitmq")
    builder.add_dependency("payment-service", "rabbitmq")
    builder.add_dependency("notification-service", "rabbitmq")

    # Logging chain
    builder.add_chain("user-service", "elasticsearch")
    builder.add_chain("order-service", "elasticsearch")

    graph = builder.build()

    print(f"Built microservices graph: {graph}")
    print("\nGraph characteristics:")
    stats = graph.stats()
    print(f"  Nodes: {stats['node_count']}")
    print(f"  Edges: {stats['edge_count']}")
    print(f"  Is DAG: {stats['is_dag']}")
    print(f"  Average out-degree: {stats['avg_out_degree']:.2f}")
    print(f"  Max out-degree: {stats['max_out_degree']}")

    # Find most critical nodes (highest impact)
    critical_nodes = []
    for node_id in graph.nodes:
        impact_size = len(graph.get_impact_radius(node_id))
        if impact_size > 0:
            critical_nodes.append((node_id, impact_size))

    critical_nodes.sort(key=lambda x: x[1], reverse=True)
    print("\nMost critical nodes (by impact radius):")
    for node_id, impact_size in critical_nodes[:5]:
        print(f"  {node_id}: affects {impact_size} other nodes")
    print()


def example_6_validation_and_errors():
    """Example 6: Validation and error handling."""
    print("=" * 60)
    print("Example 6: Validation and Error Handling")
    print("=" * 60)

    # Example with missing nodes
    print("Testing edge with missing nodes:")
    graph = Graph()
    graph.add_node(Node("service-a", "service"))

    try:
        graph.add_edge(Edge("service-a", "service-b"))  # service-b doesn't exist
    except ValueError as e:
        print(f"  Error caught: {e}")

    # Example with cycles
    print("\nTesting cycle detection:")
    graph = Graph()
    graph.add_node(Node("a", "service"))
    graph.add_node(Node("b", "service"))
    graph.add_node(Node("c", "service"))

    graph.add_edge(Edge("a", "b"))
    graph.add_edge(Edge("b", "c"))
    graph.add_edge(Edge("c", "a"))  # Creates a cycle

    cycles = graph.find_cycles()
    print(f"  Cycles found: {cycles}")

    errors = graph.validate()
    print(f"  Validation errors: {errors}")

    # Example with self-loop
    print("\nTesting self-loop prevention:")
    try:
        edge = Edge("a", "a")  # Self-loop
    except ValueError as e:
        print(f"  Error caught: {e}")

    print()


def example_7_save_and_load():
    """Example 7: Saving and loading graphs."""
    print("=" * 60)
    print("Example 7: Import/Export")
    print("=" * 60)

    # Create a graph
    graph = (GraphBuilder()
             .add_node("frontend", "service", version="1.2.0")
             .add_node("backend", "api", port=8080)
             .add_node("database", "database", engine="postgres")
             .add_dependency("frontend", "backend", protocol="https")
             .add_dependency("backend", "database", pool_size=10)
             .build())

    # Export to dictionary
    graph_dict = graph.to_dict()
    print("Exported graph as dictionary:")
    print(json.dumps(graph_dict, indent=2))

    # You could save this to a file
    # with open('graph.json', 'w') as f:
    #     json.dump(graph_dict, f, indent=2)

    # Convert to YAML format for saving
    yaml_format = {
        'nodes': graph_dict['nodes'],
        'dependencies': graph_dict['edges']
    }

    print("\nYAML format for saving:")
    print("nodes:")
    for node in yaml_format['nodes']:
        print(f"  - id: {node['id']}")
        print(f"    type: {node['type']}")
        if node['metadata']:
            print(f"    metadata: {node['metadata']}")

    print("dependencies:")
    for edge in yaml_format['dependencies']:
        if edge['metadata']:
            print(f"  - source: {edge['source']}")
            print(f"    target: {edge['target']}")
            print(f"    metadata: {edge['metadata']}")
        else:
            print(f"  - {edge['source']} -> {edge['target']}")
    print()


def main():
    """Run all examples."""
    example_1_manual_construction()
    example_2_builder_pattern()
    example_3_yaml_simple()
    example_4_yaml_extended()
    example_5_advanced_patterns()
    example_6_validation_and_errors()
    example_7_save_and_load()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
