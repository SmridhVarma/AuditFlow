"""
Pydantic schemas for the Router service
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RegionEnum(str, Enum):
    SG = "SG"  # Singapore
    AU = "AU"  # Australia


class CategoryEnum(str, Enum):
    HOME = "Home"
    BUSINESS = "Business"


class ClassifyRequest(BaseModel):
    """Request schema for claim classification"""
    claim_text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The claim description text to classify",
        examples=["Water leak from my air-con unit in Bedok."],
    )
    include_reasoning: bool = Field(
        default=True,
        description="Whether to include classification reasoning in response",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "claim_text": "Water leak from my air-con unit in Bedok.",
                    "include_reasoning": True,
                },
                {
                    "claim_text": "Machinery breakdown at my Sydney warehouse.",
                    "include_reasoning": True,
                },
            ]
        }
    }


class ClassifyResponse(BaseModel):
    """Response schema for claim classification"""
    region: RegionEnum = Field(
        ..., description="Classified region: SG (Singapore) or AU (Australia)"
    )
    category: CategoryEnum = Field(
        ..., description="Classified category: Home or Business"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Classification confidence score (0-1)",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Explanation of why this classification was made",
    )
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Processing time in milliseconds",
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    model_loaded: bool
