"""
Pydantic schemas for the RAG service
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PolicyChunk(BaseModel):
    """A chunk of policy document with metadata"""
    id: Optional[int] = None
    content: str = Field(..., description="The text content of the chunk")
    region: str = Field(..., description="Region code: SG or AU")
    category: str = Field(..., description="Category: Home or Business")
    policy_name: str = Field(..., description="Name of the source policy")
    section: Optional[str] = Field(None, description="Section within the policy")
    subsection: Optional[str] = Field(None, description="Subsection within the policy")
    page_number: Optional[int] = Field(None, description="Page number in source PDF")
    chunk_index: Optional[int] = Field(None, description="Index of chunk in document")
    similarity_score: Optional[float] = Field(None, description="Similarity score from search")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    """Request schema for semantic search"""
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The search query text",
        examples=["water damage from burst pipe"],
    )
    region: Optional[str] = Field(
        None,
        description="Filter by region: SG or AU",
        examples=["SG"],
    )
    category: Optional[str] = Field(
        None,
        description="Filter by category: Home or Business",
        examples=["Home"],
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of results to return",
    )
    min_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "water damage from burst pipe",
                    "region": "SG",
                    "category": "Home",
                    "top_k": 5,
                    "min_score": 0.5,
                }
            ]
        }
    }


class SearchResponse(BaseModel):
    """Response schema for semantic search"""
    chunks: List[PolicyChunk] = Field(
        ..., description="List of matching policy chunks"
    )
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="The original query")
    filters: Dict[str, Optional[str]] = Field(
        ..., description="Applied filters"
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Processing time in milliseconds"
    )


class ChunkInput(BaseModel):
    """Input schema for a chunk to be ingested"""
    content: str
    region: str
    category: str
    policy_name: str
    section: Optional[str] = None
    subsection: Optional[str] = None
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class IngestRequest(BaseModel):
    """Request schema for chunk ingestion"""
    policy_name: str = Field(..., description="Name of the policy being ingested")
    chunks: List[ChunkInput] = Field(..., description="List of chunks to ingest")


class IngestResponse(BaseModel):
    """Response schema for chunk ingestion"""
    success: bool
    chunks_ingested: int
    policy_name: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    database_connected: bool
    embedding_model_loaded: bool
