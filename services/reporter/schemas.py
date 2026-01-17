"""
Pydantic schemas for the Reporter service
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ReasoningStepInput(BaseModel):
    """Input schema for a reasoning step"""
    step_number: int
    step_type: str
    content: str
    tool_used: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[str] = None
    timestamp: Optional[str] = None


class EvidenceInput(BaseModel):
    """Input schema for policy evidence"""
    content: str
    policy_name: str
    section: Optional[str] = None
    relevance_score: float = 0.0


class ReportRequest(BaseModel):
    """Request schema for report generation"""
    claim_id: str = Field(..., description="Unique claim identifier")
    claim_text: str = Field(..., description="Original claim text")
    region: str = Field(..., description="Region: SG or AU")
    category: str = Field(..., description="Category: Home or Business")
    decision: str = Field(..., description="Coverage decision")
    confidence: float = Field(..., description="Confidence score")
    summary: str = Field(..., description="Decision summary")
    reasoning_trace: List[ReasoningStepInput] = Field(
        ..., description="Complete reasoning trace"
    )
    evidence: List[EvidenceInput] = Field(
        default_factory=list, description="Policy evidence"
    )
    exclusions_found: List[str] = Field(
        default_factory=list, description="Exclusions found"
    )
    limits_found: List[str] = Field(
        default_factory=list, description="Limits found"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
