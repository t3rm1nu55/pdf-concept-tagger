"""
API v1 Router

MVP: Main API router for v1 endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import analyze, concepts

router = APIRouter()

router.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
router.include_router(concepts.router, prefix="/concepts", tags=["concepts"])
