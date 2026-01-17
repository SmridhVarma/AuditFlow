"""
Service B: Contextual RAG Engine
FastAPI service for metadata-filtered semantic search using pgvector
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    SearchRequest,
    SearchResponse,
    PolicyChunk,
    HealthResponse,
    IngestRequest,
    IngestResponse,
)
from database import DatabaseManager
from embeddings import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db_manager: Optional[DatabaseManager] = None
embedding_service: Optional[EmbeddingService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and embedding service on startup"""
    global db_manager, embedding_service
    
    logger.info("Initializing RAG Engine...")
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    logger.info("Embedding service initialized")
    
    # Initialize database connection
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://auditflow:auditflow_secret@localhost:5432/auditflow"
    )
    db_manager = DatabaseManager(database_url)
    await db_manager.initialize()
    logger.info("Database connection established")
    
    yield
    
    # Cleanup
    if db_manager:
        await db_manager.close()
    logger.info("RAG Engine shutdown complete")


app = FastAPI(
    title="AuditFlow RAG Engine",
    description="Service B: Contextual semantic search with metadata filtering",
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
    db_connected = db_manager is not None and await db_manager.is_connected()
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        service="rag",
        database_connected=db_connected,
        embedding_model_loaded=embedding_service is not None,
    )


@app.post("/search", response_model=SearchResponse)
async def search_policies(request: SearchRequest):
    """
    Perform semantic search on policy documents with metadata filtering.
    
    - **query**: The search query text
    - **region**: Filter by region (SG/AU)
    - **category**: Filter by category (Home/Business)
    - **top_k**: Number of results to return
    - **min_score**: Minimum similarity score threshold
    
    Returns relevant policy chunks with similarity scores.
    """
    if db_manager is None or embedding_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    start_time = time.time()
    
    try:
        # Generate query embedding
        query_embedding = embedding_service.embed_text(request.query)
        
        # Search with metadata filters
        results = await db_manager.search_similar(
            embedding=query_embedding,
            region=request.region,
            category=request.category,
            top_k=request.top_k,
            min_score=request.min_score,
        )
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"Search completed: query='{request.query[:50]}...', "
            f"region={request.region}, category={request.category}, "
            f"results={len(results)}, time={processing_time:.3f}s"
        )
        
        return SearchResponse(
            chunks=results,
            total_results=len(results),
            query=request.query,
            filters={
                "region": request.region,
                "category": request.category,
            },
            processing_time_ms=int(processing_time * 1000),
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/search/exclusions", response_model=SearchResponse)
async def search_exclusions(request: SearchRequest):
    """
    Search specifically for policy exclusion clauses.
    Automatically augments query with exclusion-related terms.
    """
    # Augment query to focus on exclusions
    augmented_query = f"exclusion clause: {request.query} NOT covered excluded from coverage"
    
    request_copy = request.model_copy(update={"query": augmented_query})
    return await search_policies(request_copy)


@app.post("/search/limits", response_model=SearchResponse)
async def search_limits(request: SearchRequest):
    """
    Search specifically for policy limits and coverage amounts.
    Automatically augments query with limit-related terms.
    """
    # Augment query to focus on limits
    augmented_query = f"coverage limit amount: {request.query} maximum limit sum insured"
    
    request_copy = request.model_copy(update={"query": augmented_query})
    return await search_policies(request_copy)


@app.post("/ingest", response_model=IngestResponse)
async def ingest_chunks(request: IngestRequest):
    """
    Ingest policy document chunks into the vector database.
    
    Used by the data ingestion pipeline to populate the database.
    """
    if db_manager is None or embedding_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Generate embeddings for all chunks
        embeddings = embedding_service.embed_batch([chunk.content for chunk in request.chunks])
        
        # Insert into database
        inserted_count = await db_manager.insert_chunks(
            chunks=request.chunks,
            embeddings=embeddings,
        )
        
        logger.info(f"Ingested {inserted_count} chunks for policy: {request.policy_name}")
        
        return IngestResponse(
            success=True,
            chunks_ingested=inserted_count,
            policy_name=request.policy_name,
        )
        
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/stats")
async def get_statistics():
    """Get database statistics"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    stats = await db_manager.get_stats()
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
