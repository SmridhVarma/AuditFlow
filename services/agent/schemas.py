"""
Pydantic schemas for the Agent service
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class DecisionEnum(str, Enum):
    COVERED = "COVERED"
    NOT_COVERED = "NOT_COVERED"
    PARTIAL = "PARTIAL"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class StepTypeEnum(str, Enum):
    THINK = "THINK"
    ACT = "ACT"
    OBSERVE = "OBSERVE"
    DECIDE = "DECIDE"


class ReasoningStep(BaseModel):
    """A single step in the agent's reasoning trace"""
    step_number: int = Field(..., description="Sequential step number")
    step_type: StepTypeEnum = Field(..., description="Type of reasoning step")
    content: str = Field(..., description="Content of the reasoning step")
    tool_used: Optional[str] = Field(None, description="Tool used in ACT step")
    tool_input: Optional[Dict[str, Any]] = Field(None, description="Input to the tool")
    tool_output: Optional[str] = Field(None, description="Output from the tool")
    timestamp: Optional[str] = Field(None, description="Timestamp of the step")


class PolicyEvidence(BaseModel):
    """Policy clause used as evidence"""
    content: str = Field(..., description="The policy clause text")
    policy_name: str = Field(..., description="Source policy name")
    section: Optional[str] = Field(None, description="Section in policy")
    relevance_score: float = Field(..., description="Relevance to the claim")


class AnalyzeRequest(BaseModel):
    """Request schema for claim analysis"""
    claim_text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The claim description to analyze",
        examples=["Water leak from my air-con unit in Bedok caused damage to my living room floor."],
    )
    region: str = Field(
        ...,
        description="Region classification from router: SG or AU",
        examples=["SG"],
    )
    category: str = Field(
        ...,
        description="Category classification from router: Home or Business",
        examples=["Home"],
    )
    additional_context: Optional[str] = Field(
        None,
        description="Additional context or documents",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "claim_text": "Water leak from my air-con unit in Bedok caused damage to my living room floor.",
                    "region": "SG",
                    "category": "Home",
                }
            ]
        }
    }


class AnalyzeResponse(BaseModel):
    """Response schema for claim analysis"""
    claim_id: str = Field(..., description="Unique claim identifier")
    decision: DecisionEnum = Field(..., description="Coverage decision")
    reasoning_trace: List[ReasoningStep] = Field(
        ..., description="Complete reasoning trace"
    )
    evidence: List[PolicyEvidence] = Field(
        ..., description="Policy clauses supporting decision"
    )
    summary: str = Field(..., description="Human-readable summary")
    exclusions_found: List[str] = Field(
        default_factory=list, description="Relevant exclusions found"
    )
    limits_found: List[str] = Field(
        default_factory=list, description="Coverage limits found"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in decision"
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Processing time in milliseconds"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    agent_loaded: bool
