"""
Fast Experimentation Backend for PDF Concept Tagger

Quick setup for prompt/model/technique experimentation.

This module follows PROJECT_RULES.md standards:
- Incremental & modular development
- No mocks in production code
- Documented complex logic
- Error handling for external APIs
- Environment-based configuration

See PROJECT_RULES.md for development guidelines.
"""

import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Import shared models
import sys
sys.path.append(str(Path(__file__).parent.parent))
from shared.models import (
    Concept, Domain, Relationship, Taxonomy, AgentPacket,
    AnalyzeRequest, ExperimentRequest
)

load_dotenv()

app = FastAPI(
    title="PDF Concept Tagger Experiment",
    description="Experimentation backend for prompt/model/technique testing",
    version="0.1.0-experiment"
)

# CORS Configuration
# Decision: Allow all origins for experimentation (pragmatic for demo)
# In production, specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Specify origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM Configuration
# Decision: Environment-based provider selection (pragmatic: easy switching)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, google


def get_llm():
    """
    Get configured LLM instance based on environment configuration.
    
    Returns:
        LLM instance (ChatOpenAI, ChatAnthropic, or ChatGoogleGenerativeAI)
        
    Raises:
        ValueError: If LLM_PROVIDER is not recognized
        ValueError: If required API key is missing
        
    Examples:
        >>> llm = get_llm()
        >>> response = await llm.ainvoke([HumanMessage(content="test")])
    """
    if LLM_PROVIDER == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            temperature=0.1,
            api_key=api_key
        )
    elif LLM_PROVIDER == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            temperature=0.1,
            api_key=api_key
        )
    elif LLM_PROVIDER == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment")
        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "gemini-pro"),
            temperature=0.1,
            google_api_key=api_key
        )
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}. Use: openai, anthropic, google")

# Use shared models (imported above)

# Load prompt templates from files
# Decision: File-based prompts for easy experimentation (pragmatic: no DB needed)
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """
    Load prompt template from file.
    
    Args:
        name: Prompt name (e.g., "harvester", "architect")
        
    Returns:
        Prompt template string, or default message if file not found
        
    Note:
        Prompt files should be in prompts/ directory with .txt extension
    """
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text()
    return f"Default prompt for {name}"


# Load prompt templates
# Decision: Load at module level for performance (pragmatic: prompts don't change often)
HARVESTER_PROMPT = load_prompt("harvester")
ARCHITECT_PROMPT = load_prompt("architect")
CURATOR_PROMPT = load_prompt("curator")

# In-memory storage for demo
# Decision: Simple in-memory storage for experimentation (pragmatic: no DB setup needed)
# TODO: Replace with real databases (PostgreSQL, Neo4j) in production
concepts_store: List[Dict[str, Any]] = []
relationships_store: List[Dict[str, Any]] = []

@app.get("/")
async def root():
    return {
        "status": "running",
        "llm_provider": LLM_PROVIDER,
        "version": "0.1.0-experiment"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analyze PDF page and extract concepts.
    
    This endpoint processes a PDF page image and extracts concepts using LLM.
    Returns streaming response with AgentPacket objects.
    
    Args:
        request: AnalyzeRequest with image_base64, page_number, etc.
        
    Returns:
        StreamingResponse with Server-Sent Events containing AgentPacket objects
        
    Raises:
        HTTPException: If LLM configuration is invalid or API call fails
        
    Example:
        POST /api/v1/analyze
        {
            "image_base64": "data:image/png;base64,...",
            "page_number": 1,
            "exclude_terms": []
        }
    """
    try:
        # Get LLM instance
        # Decision: Allow model override for experimentation (pragmatic: easy testing)
        llm = get_llm()
        if request.model_override:
            llm.model_name = request.model_override
        
        # Build prompt
        # Decision: Allow prompt override for experimentation (pragmatic: easy testing)
        prompt_text = request.prompt_override or HARVESTER_PROMPT.format(
            page_number=request.page_number,
            exclude_terms=", ".join(request.exclude_terms[:10]) if request.exclude_terms else "None"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # For vision models, include image
    if LLM_PROVIDER == "google":
        # Google Gemini supports vision
        messages = [
            {
                "role": "user",
                "parts": [
                    {"text": prompt_text},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": request.image_base64.split(",")[1] if "," in request.image_base64 else request.image_base64
                        }
                    }
                ]
            }
        ]
    else:
        # For text-only models, use text extraction
        messages = [HumanMessage(content=prompt_text)]
    
    async def generate():
        """
        Generate streaming response with concept extraction results.
        
        Yields:
            Server-Sent Events with AgentPacket objects or error messages
        """
        try:
            # Stream response if supported
            # Decision: Stream for better UX (pragmatic: shows progress)
            if hasattr(llm, "astream"):
                async for chunk in llm.astream(messages):
                    if hasattr(chunk, "content"):
                        yield f"data: {json.dumps({'text': chunk.content})}\n\n"
                    else:
                        yield f"data: {json.dumps({'text': str(chunk)})}\n\n"
            
            # Get final response
            response = await llm.ainvoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            
            # Parse JSON response
            # Decision: Try multiple parsing strategies (pragmatic: handle various LLM outputs)
            concepts = []
            try:
                # Try direct JSON parse
                parsed = json.loads(content)
                concepts = parsed if isinstance(parsed, list) else [parsed]
            except json.JSONDecodeError:
                # Try extracting JSON from text (some LLMs wrap JSON in text)
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    try:
                        concepts = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        # If still fails, create error packet
                        yield f"data: {json.dumps({'sender': 'SYSTEM', 'intent': 'ERROR', 'content': {'error': 'Failed to parse LLM response as JSON'}})}\n\n"
                        return
            
            # Emit concepts as AgentPacket objects
            # Decision: Use AgentPacket protocol for consistency (see shared/models.py)
            for concept in concepts:
                packet = AgentPacket(
                    sender="HARVESTER",
                    intent="GRAPH_UPDATE",
                    content={"concept": concept}
                )
                concepts_store.append(concept)
                yield f"data: {json.dumps(packet.dict())}\n\n"
            
            # Completion packet
            completion = AgentPacket(
                sender="SYSTEM",
                intent="TASK_COMPLETE",
                content={}
            )
            yield f"data: {json.dumps(completion.dict())}\n\n"
            
        except Exception as e:
            # Error handling: Always yield error packet, don't raise
            # Decision: Return error in stream rather than HTTP error (pragmatic: client can handle)
            error_packet = AgentPacket(
                sender="SYSTEM",
                intent="ERROR",
                content={"error": str(e)}
            )
            yield f"data: {json.dumps(error_packet.dict())}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/v1/prompts/experiment")
async def experiment_prompt(request: ExperimentRequest):
    """
    Experiment with custom prompts and model configurations.
    
    This endpoint allows testing different prompts, models, and providers
    for experimentation purposes.
    
    Args:
        request: ExperimentRequest with prompt, optional model/provider/temperature
        
    Returns:
        Dict with prompt, response, model, provider, temperature
        
    Raises:
        HTTPException: If LLM configuration is invalid
        
    Example:
        POST /api/v1/prompts/experiment
        {
            "prompt": "Extract all dates from this text...",
            "model": "gpt-4-turbo-preview",
            "provider": "openai",
            "temperature": 0.1
        }
    """
    try:
        # Get LLM instance
        llm = get_llm()
        
        # Allow provider override for experimentation
        # Decision: Runtime provider switching (pragmatic: easy comparison)
        if request.provider:
            global LLM_PROVIDER
            LLM_PROVIDER = request.provider
            llm = get_llm()
        
        # Allow model override
        if request.model:
            llm.model_name = request.model
        
        # Allow temperature override
        if request.temperature is not None:
            llm.temperature = request.temperature
        
        # Build messages
        messages = [HumanMessage(content=request.prompt)]
        
        # Handle vision for Google Gemini
        # Decision: Special handling for Google vision API (pragmatic: different format)
        if LLM_PROVIDER == "google" and request.image_base64:
            # Extract base64 data (remove data:image/png;base64, prefix if present)
            image_data = request.image_base64.split(",")[1] if "," in request.image_base64 else request.image_base64
            messages = [{
                "role": "user",
                "parts": [
                    {"text": request.prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_data
                        }
                    }
                ]
            }]
        
        # Invoke LLM
        response = await llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        
        return {
            "prompt": request.prompt,
            "response": content,
            "model": llm.model_name,
            "provider": LLM_PROVIDER,
            "temperature": request.temperature
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")

@app.get("/api/v1/concepts")
async def get_concepts():
    """
    Get all extracted concepts from in-memory store.
    
    Returns:
        Dict with concepts list and count
        
    Note:
        This uses in-memory storage. In production, query from database.
    """
    return {"concepts": concepts_store, "count": len(concepts_store)}

@app.get("/api/v1/models")
async def get_models():
    """Get available models"""
    return {
        "current_provider": LLM_PROVIDER,
        "available_providers": ["openai", "anthropic", "google"],
        "models": {
            "openai": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
            "google": ["gemini-pro", "gemini-pro-vision"]
        }
    }

@app.post("/api/v1/models/switch")
async def switch_model(provider: str, model: Optional[str] = None):
    """Switch LLM provider/model"""
    global LLM_PROVIDER
    if provider in ["openai", "anthropic", "google"]:
        LLM_PROVIDER = provider
        if model:
            os.environ[f"{provider.upper()}_MODEL"] = model
        return {"status": "switched", "provider": LLM_PROVIDER, "model": model}
    return {"error": "Invalid provider"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Currently implements basic echo functionality.
    TODO: Implement real-time concept extraction updates
    
    Args:
        websocket: WebSocket connection
        
    Note:
        This is a placeholder. Full implementation will stream AgentPacket objects.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back (placeholder)
            # TODO: Process and send real-time updates
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        # Client disconnected, clean up if needed
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
