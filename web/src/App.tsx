import React, { useEffect, useState } from 'react';
import Graph from './components/Graph';
import NodeDetails from './components/NodeDetails';
import MetricsPanel from './components/MetricsPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { GraphData, NodeDetail } from './types';
import { fetchGraph } from './services/api';
import './App.css';

const App: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<NodeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showMetrics, setShowMetrics] = useState(false);

  // WebSocket for real-time updates
  const { metrics, connected } = useWebSocket('ws://localhost:8000/ws/graph');

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const data = await fetchGraph();
      setGraphData(data);
    } catch (error) {
      console.error('Failed to load graph:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeSelect = (nodeDetail: NodeDetail | null) => {
    setSelectedNode(nodeDetail);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dependency graph...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>🔗 Dependency Graph Monitor</h1>
          <div className="connection-status">
            <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
            {connected ? 'Real-time Connected' : 'Disconnected'}
          </div>
        </div>
        <div className="header-right">
          {graphData && (
            <div className="stats">
              <div className="stat">
                <span className="stat-value">{graphData.stats.node_count}</span>
                <span className="stat-label">Nodes</span>
              </div>
              <div className="stat">
                <span className="stat-value">{graphData.stats.edge_count}</span>
                <span className="stat-label">Edges</span>
              </div>
              <div className="stat">
                <span className="stat-value">
                  {graphData.stats.is_dag ? '✓' : '✗'}
                </span>
                <span className="stat-label">Acyclic</span>
              </div>
            </div>
          )}
          <button
            className="metrics-toggle"
            onClick={() => setShowMetrics(!showMetrics)}
          >
            {showMetrics ? '📊 Hide Metrics' : '📊 Show Metrics'}
          </button>
        </div>
      </header>

      <main className="app-main">
        {graphData && (
          <>
            <Graph
              data={graphData}
              onNodeSelect={handleNodeSelect}
              metrics={metrics}
            />
            <NodeDetails
              node={selectedNode}
              onClose={() => setSelectedNode(null)}
            />
            {showMetrics && (
              <MetricsPanel
                metrics={metrics}
                onClose={() => setShowMetrics(false)}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default App;