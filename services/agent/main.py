"""
Service C: Agentic Reasoning Core
FastAPI service with LangGraph ReAct agent for policy analysis
"""

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ReasoningStep,
    HealthResponse,
)
from graph import PolicyReasoningAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[PolicyReasoningAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on startup"""
    global agent
    
    logger.info("Initializing Reasoning Agent...")
    
    rag_service_url = os.getenv("RAG_SERVICE_URL", "http://localhost:8002")
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    llm_model = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    
    agent = PolicyReasoningAgent(
        rag_service_url=rag_service_url,
        google_api_key=google_api_key,
        model_name=llm_model,
    )
    
    logger.info(f"Reasoning Agent initialized with model: {llm_model}")
    
    yield
    
    logger.info("Reasoning Agent shutdown complete")


app = FastAPI(
    title="AuditFlow Reasoning Agent",
    description="Service C: LangGraph ReAct agent for policy analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="agent",
        agent_loaded=agent is not None,
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_claim(request: AnalyzeRequest):
    """
    Analyze an insurance claim using the ReAct reasoning agent.
    
    The agent will:
    1. Think about what information is needed
    2. Search for relevant policy clauses
    3. Check for exclusions
    4. Check coverage limits
    5. Make a coverage decision with reasoning
    
    Returns:
    - **claim_id**: Unique identifier for this analysis
    - **decision**: Coverage decision (COVERED, NOT_COVERED, PARTIAL, NEEDS_REVIEW)
    - **reasoning_trace**: Complete trace of agent's reasoning steps
    - **evidence**: Policy clauses supporting the decision
    - **summary**: Human-readable summary of the analysis
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    start_time = time.time()
    claim_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Starting analysis for claim {claim_id}")
        
        result = await agent.analyze(
            claim_id=claim_id,
            claim_text=request.claim_text,
            region=request.region,
            category=request.category,
        )
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"Analysis complete for claim {claim_id}: "
            f"decision={result['decision']}, "
            f"steps={len(result['reasoning_trace'])}, "
            f"time={processing_time:.2f}s"
        )
        
        return AnalyzeResponse(
            claim_id=claim_id,
            decision=result["decision"],
            reasoning_trace=result["reasoning_trace"],
            evidence=result["evidence"],
            summary=result["summary"],
            exclusions_found=result.get("exclusions_found", []),
            limits_found=result.get("limits_found", []),
            confidence=result.get("confidence", 0.0),
            processing_time_ms=int(processing_time * 1000),
        )
        
    except Exception as e:
        logger.error(f"Analysis error for claim {claim_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/stream")
async def analyze_claim_stream(request: AnalyzeRequest):
    """
    Stream the analysis process step by step.
    Useful for showing live "Agent Thinking" in the UI.
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate_steps():
        claim_id = str(uuid.uuid4())
        
        async for step in agent.analyze_stream(
            claim_id=claim_id,
            claim_text=request.claim_text,
            region=request.region,
            category=request.category,
        ):
            yield f"data: {json.dumps(step)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_steps(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
