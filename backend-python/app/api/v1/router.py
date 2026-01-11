"""
API v1 Router

MVP: Main API router for v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import analyze, concepts, graph, websocket, agents

router = APIRouter()

router.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
router.include_router(concepts.router, prefix="/concepts", tags=["concepts"])
router.include_router(graph.router, prefix="/graph", tags=["graph"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
