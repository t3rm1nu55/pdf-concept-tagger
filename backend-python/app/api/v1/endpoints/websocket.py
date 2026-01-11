"""
WebSocket Endpoint

MVP: Real-time updates for concept extraction.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
import uuid

from app.database.postgres import get_db
from app.models.concept import Concept, Relationship
from app.models.agent_packet import AgentPacket, AgentPacketContent, ConceptContent

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[uuid.UUID, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, document_id: uuid.UUID):
        """Connect a WebSocket for a document."""
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = set()
        self.active_connections[document_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, document_id: uuid.UUID):
        """Disconnect a WebSocket."""
        if document_id in self.active_connections:
            self.active_connections[document_id].discard(websocket)
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific connection."""
        await websocket.send_json(message)
    
    async def broadcast_to_document(self, message: dict, document_id: uuid.UUID):
        """Broadcast message to all connections for a document."""
        if document_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[document_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[document_id].discard(conn)

manager = ConnectionManager()


@router.websocket("/ws/{document_id}")
async def websocket_endpoint(websocket: WebSocket, document_id: uuid.UUID):
    """
    WebSocket endpoint for real-time updates.
    
    MVP: Basic WebSocket connection for concept extraction updates.
    """
    await manager.connect(websocket, document_id)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connected",
            "document_id": str(document_id),
            "message": "Connected to document updates"
        }, websocket)
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            # MVP: Just keep connection alive
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong"
                    }, websocket)
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, document_id)


async def send_concept_update(document_id: uuid.UUID, concept: Concept):
    """Send concept update via WebSocket in AgentPacket format."""
    packet = AgentPacket(
        sender="HARVESTER",
        recipient="",
        intent="GRAPH_UPDATE",
        content=AgentPacketContent(
            concept=ConceptContent(
                id=str(concept.id),
                term=concept.term,
                type=concept.type,
                dataType=concept.data_type,
                category=concept.category or "",
                explanation=concept.explanation or "",
                confidence=concept.confidence,
                boundingBox=concept.source_location.get("boundingBox") if concept.source_location else None,
                ui_group=concept.ui_group or "General"
            ),
            log=f"Extracted concept: {concept.term}"
        )
    )
    
    await manager.broadcast_to_document(packet.model_dump(), document_id)


async def send_relationship_update(document_id: uuid.UUID, relationship: Relationship):
    """Send relationship update via WebSocket."""
    await manager.broadcast_to_document({
        "type": "relationship_created",
        "data": {
            "relationship_id": str(relationship.id),
            "source": str(relationship.source_concept_id),
            "target": str(relationship.target_concept_id),
            "type": relationship.type
        }
    }, document_id)
