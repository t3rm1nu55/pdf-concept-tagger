"""
Fast Experimentation Backend for PDF Concept Tagger
Quick setup for prompt/model/technique experimentation
"""

import os
import base64
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

load_dotenv()

app = FastAPI(title="PDF Concept Tagger Experiment")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, google

def get_llm():
    """Get configured LLM"""
    if LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif LLM_PROVIDER == "anthropic":
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            temperature=0.1,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    elif LLM_PROVIDER == "google":
        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "gemini-pro"),
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")

# Request/Response Models
class AnalyzeRequest(BaseModel):
    image_base64: str
    page_number: int
    exclude_terms: List[str] = []
    prompt_override: Optional[str] = None
    model_override: Optional[str] = None

class Concept(BaseModel):
    id: str
    term: str
    type: str
    dataType: Optional[str] = None
    category: str
    explanation: str
    confidence: float
    ui_group: str

class AgentPacket(BaseModel):
    sender: str
    intent: str
    content: Dict[str, Any]

# Prompt Templates (Experiment-friendly)
HARVESTER_PROMPT = """You are the HARVESTER agent extracting concepts from a PDF page.

Extract entities, concepts, and relationships from this document page.

Return a JSON array of concept objects. Each concept should have:
- id: unique identifier
- term: the actual text/name
- type: 'concept' or 'hypernode'
- dataType: 'entity' | 'date' | 'location' | 'organization' | 'person' | 'money' | 'legal' | 'condition'
- category: classification
- explanation: brief description
- confidence: 0.0-1.0
- ui_group: grouping category

Page: {page_number}
Exclude terms: {exclude_terms}

Output only valid JSON array."""

# In-memory storage for demo (replace with real DBs later)
concepts_store = []
relationships_store = []

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
    """Analyze PDF page and extract concepts"""
    
    # Get LLM
    llm = get_llm()
    
    # Build prompt
    prompt_text = request.prompt_override or HARVESTER_PROMPT.format(
        page_number=request.page_number,
        exclude_terms=", ".join(request.exclude_terms[:10])
    )
    
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
        try:
            # Stream response
            if hasattr(llm, "astream"):
                async for chunk in llm.astream(messages):
                    if hasattr(chunk, "content"):
                        yield f"data: {json.dumps({'text': chunk.content})}\n\n"
                    else:
                        yield f"data: {json.dumps({'text': str(chunk)})}\n\n"
            
            # Parse final response
            response = await llm.ainvoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            
            # Try to parse JSON
            try:
                concepts = json.loads(content)
                if not isinstance(concepts, list):
                    concepts = [concepts]
                
                # Emit concepts as packets
                for concept in concepts:
                    packet = {
                        "sender": "HARVESTER",
                        "intent": "GRAPH_UPDATE",
                        "content": {"concept": concept}
                    }
                    concepts_store.append(concept)
                    yield f"data: {json.dumps(packet)}\n\n"
                
            except json.JSONDecodeError:
                # If not JSON, try to extract JSON from text
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    concepts = json.loads(json_match.group())
                    for concept in concepts:
                        packet = {
                            "sender": "HARVESTER",
                            "intent": "GRAPH_UPDATE",
                            "content": {"concept": concept}
                        }
                        yield f"data: {json.dumps(packet)}\n\n"
            
            # Completion packet
            yield f"data: {json.dumps({'sender': 'SYSTEM', 'intent': 'TASK_COMPLETE', 'content': {}})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/v1/prompts/experiment")
async def experiment_prompt(
    prompt: str,
    image_base64: str,
    model: Optional[str] = None
):
    """Experiment with custom prompts"""
    llm = get_llm()
    if model:
        llm.model_name = model
    
    messages = [HumanMessage(content=prompt)]
    
    if LLM_PROVIDER == "google" and image_base64:
        # Handle vision for Google
        pass
    
    response = await llm.ainvoke(messages)
    return {
        "prompt": prompt,
        "response": response.content if hasattr(response, "content") else str(response),
        "model": llm.model_name,
        "provider": LLM_PROVIDER
    }

@app.get("/api/v1/concepts")
async def get_concepts():
    """Get all extracted concepts"""
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
    """WebSocket for real-time updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or process
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
