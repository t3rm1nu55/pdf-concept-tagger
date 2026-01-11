"""
FastAPI Main Application

MVP backend for PDF Concept Tagger.
Uses Cognizant proxy for all LLM calls.

See PROJECT_RULES.md for development guidelines.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.v1.router import router as api_v1_router

load_dotenv()

app = FastAPI(
    title="PDF Concept Tagger MVP",
    description="MVP backend with Cognizant proxy integration",
    version="0.1.0-mvp"
)

# Log startup
logger.info("Starting PDF Concept Tagger MVP")

# CORS Configuration
# Decision: Allow all origins for MVP (pragmatic for development)
# In production, specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Specify origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0-mvp",
        "proxy_configured": bool(os.getenv("COGNIZANT_PROXY_ENDPOINT"))
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PDF Concept Tagger MVP API",
        "version": "0.1.0-mvp",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "concepts": "/api/v1/concepts"
        }
    }
