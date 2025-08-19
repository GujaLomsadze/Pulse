"""WebSocket routes for real-time updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import asyncio
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove connection."""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        if not self.active_connections:
            return

        message_text = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        self.active_connections -= disconnected


manager = ConnectionManager()


@router.websocket("/graph")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time graph updates."""
    await manager.connect(websocket)

    try:
        # Send initial graph data
        from api.app import get_current_graph
        graph = get_current_graph()

        if graph:
            initial_data = {
                "type": "initial",
                "data": {
                    "nodes": [node.to_dict() for node in graph.nodes.values()],
                    "edges": [edge.to_dict() for edge in graph.edges],
                    "stats": graph.stats()
                }
            }
            await websocket.send_json(initial_data)

        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for any message from client (ping/pong)
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)