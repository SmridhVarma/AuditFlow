"""
Service D: Audit Reporter
FastAPI service for generating professional PDF audit reports
"""

import logging
import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from schemas import ReportRequest, HealthResponse
from pdf_generator import AuditPDFGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global PDF generator
pdf_generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize PDF generator on startup"""
    global pdf_generator
    
    logger.info("Initializing Audit Reporter...")
    pdf_generator = AuditPDFGenerator()
    logger.info("Audit Reporter initialized")
    
    yield
    
    logger.info("Audit Reporter shutdown complete")


app = FastAPI(
    title="AuditFlow Audit Reporter",
    description="Service D: Generate professional PDF audit reports",
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
        service="reporter",
    )


@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    """
    Generate a professional PDF audit report from the reasoning trace.
    
    The report includes:
    - Claim summary and metadata
    - Evidence section with policy clauses
    - Full reasoning trace with step-by-step analysis
    - Final decision with confidence score
    
    Returns:
    - PDF file as binary stream
    """
    if pdf_generator is None:
        raise HTTPException(status_code=503, detail="PDF generator not initialized")
    
    try:
        logger.info(f"Generating report for claim: {request.claim_id}")
        
        pdf_bytes = pdf_generator.generate(
            claim_id=request.claim_id,
            claim_text=request.claim_text,
            region=request.region,
            category=request.category,
            decision=request.decision,
            confidence=request.confidence,
            summary=request.summary,
            reasoning_trace=request.reasoning_trace,
            evidence=request.evidence,
            exclusions=request.exclusions_found,
            limits=request.limits_found,
        )
        
        logger.info(f"Report generated successfully: {len(pdf_bytes)} bytes")
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=audit_report_{request.claim_id[:8]}.pdf"
            },
        )
        
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.post("/generate-report/preview")
async def preview_report(request: ReportRequest):
    """
    Generate a preview of the report (returns metadata only, not PDF).
    Useful for validation before full PDF generation.
    """
    return {
        "claim_id": request.claim_id,
        "sections": [
            "Claim Summary",
            "Evidence",
            "Reasoning Trace",
            "Exclusions & Limits",
            "Decision",
        ],
        "estimated_pages": max(1, len(request.reasoning_trace) // 3 + 1),
        "decision": request.decision,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
