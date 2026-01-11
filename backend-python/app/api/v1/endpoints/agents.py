"""
Agent Status Endpoints

MVP: Get agent statuses for frontend display.
"""

from fastapi import APIRouter
from app.core.logging import logger

router = APIRouter()


@router.get("")
async def get_agents():
    """
    Get agent statuses.
    
    MVP: Returns static agent statuses.
    Future: Could query actual agent states from a coordinator.
    """
    logger.debug("Fetching agent statuses")
    
    # MVP: Return static statuses matching frontend expectations
    return {
        "agents": [
            {
                "name": "HARVESTER",
                "goal": "Standby",
                "status": "idle",
                "color": "text-emerald-400"
            },
            {
                "name": "CURATOR",
                "goal": "Organizing",
                "status": "idle",
                "color": "text-yellow-400"
            },
            {
                "name": "ARCHITECT",
                "goal": "Standby",
                "status": "idle",
                "color": "text-blue-400"
            },
            {
                "name": "OBSERVER",
                "goal": "Monitoring",
                "status": "idle",
                "color": "text-gray-400"
            },
            {
                "name": "CRITIC",
                "goal": "Standby",
                "status": "idle",
                "color": "text-pink-400"
            }
        ]
    }
