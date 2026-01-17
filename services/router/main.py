"""
Service A: Intent & Regional Router
FastAPI service for classifying claims by region (SG/AU) and category (Home/Business)
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    ClassifyRequest,
    ClassifyResponse,
    HealthResponse,
    RegionEnum,
    CategoryEnum,
)
from models.classifier import RegionalClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global classifier instance
classifier: Optional[RegionalClassifier] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize classifier on startup"""
    global classifier
    logger.info("Loading regional classifier model...")
    classifier = RegionalClassifier()
    logger.info("Classifier loaded successfully")
    yield
    logger.info("Shutting down router service")


app = FastAPI(
    title="AuditFlow Intent Router",
    description="Service A: Classifies insurance claims by region and category",
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
        service="router",
        model_loaded=classifier is not None,
    )


@app.post("/classify", response_model=ClassifyResponse)
async def classify_claim(request: ClassifyRequest):
    """
    Classify an insurance claim by region and category.
    
    - **claim_text**: The claim description text
    - **include_reasoning**: Whether to include classification reasoning
    
    Returns:
    - **region**: SG (Singapore) or AU (Australia)
    - **category**: Home or Business
    - **confidence**: Classification confidence score
    - **reasoning**: Optional explanation of classification
    """
    if classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")
    
    start_time = time.time()
    
    try:
        result = classifier.classify(
            text=request.claim_text,
            include_reasoning=request.include_reasoning,
        )
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"Classified claim: region={result['region']}, "
            f"category={result['category']}, "
            f"confidence={result['confidence']:.3f}, "
            f"time={processing_time:.3f}s"
        )
        
        return ClassifyResponse(
            region=RegionEnum(result["region"]),
            category=CategoryEnum(result["category"]),
            confidence=result["confidence"],
            reasoning=result.get("reasoning"),
            processing_time_ms=int(processing_time * 1000),
        )
        
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post("/batch-classify")
async def batch_classify(requests: list[ClassifyRequest]):
    """Classify multiple claims in batch"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")
    
    results = []
    for req in requests:
        try:
            result = classifier.classify(
                text=req.claim_text,
                include_reasoning=req.include_reasoning,
            )
            results.append(ClassifyResponse(
                region=RegionEnum(result["region"]),
                category=CategoryEnum(result["category"]),
                confidence=result["confidence"],
                reasoning=result.get("reasoning"),
            ))
        except Exception as e:
            results.append({"error": str(e)})
    
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
