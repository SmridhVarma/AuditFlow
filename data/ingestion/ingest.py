"""
Policy Document Ingestion Script
Parses PDFs and ingests into pgvector database
"""

import os
import sys
import json
import asyncio
from typing import List, Dict, Any, Optional

import httpx

# Try to import PDF libraries
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("PyMuPDF not installed. Using mock data for development.")


class PolicyIngester:
    """Ingests policy documents into the RAG service"""
    
    def __init__(self, rag_service_url: str = "http://localhost:8002"):
        self.rag_service_url = rag_service_url.rstrip("/")
        self.chunk_size = 500  # characters per chunk
        self.chunk_overlap = 100  # overlap between chunks
    
    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Parse a PDF and extract text chunks with metadata"""
        if not HAS_PYMUPDF:
            return []
        
        chunks = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Split into chunks
            page_chunks = self._split_text(text, page_num + 1)
            chunks.extend(page_chunks)
        
        doc.close()
        return chunks
    
    def _split_text(self, text: str, page_number: int) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        chunks = []
        text = text.strip()
        
        if len(text) <= self.chunk_size:
            if text:
                chunks.append({
                    "content": text,
                    "page_number": page_number,
                    "chunk_index": 0,
                })
            return chunks
        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                for sep in ['. ', '.\n', '\n\n']:
                    pos = text.rfind(sep, start, end)
                    if pos > start:
                        end = pos + len(sep)
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "content": chunk_text,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1
            
            start = end - self.chunk_overlap
        
        return chunks
    
    async def ingest_policy(
        self,
        policy_name: str,
        region: str,
        category: str,
        chunks: List[Dict[str, Any]],
        section: Optional[str] = None,
    ) -> int:
        """Ingest policy chunks into the RAG service"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "policy_name": policy_name,
                "chunks": [
                    {
                        "content": chunk["content"],
                        "region": region,
                        "category": category,
                        "policy_name": policy_name,
                        "section": section,
                        "page_number": chunk.get("page_number"),
                        "chunk_index": chunk.get("chunk_index"),
                    }
                    for chunk in chunks
                ],
            }
            
            response = await client.post(
                f"{self.rag_service_url}/ingest",
                json=payload,
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("chunks_ingested", 0)
            else:
                print(f"Ingestion failed: {response.status_code}")
                print(response.text)
                return 0
    
    def get_mock_msig_sg_policy(self) -> List[Dict[str, Any]]:
        """Return mock MSIG Singapore HomePlus policy chunks"""
        return [
            {
                "content": """MSIG Enhanced HomePlus Policy - Section 1: Loss or Damage to Building and Contents

We will pay for loss or damage to the building and contents caused by:
1. Fire, lightning, explosion
2. Aircraft and other aerial devices
3. Impact by vehicles
4. Water damage from bursting, leaking or overflowing of water tanks, apparatus or pipes
5. Theft or attempted theft involving forcible and violent entry or exit
6. Riot, strike and malicious damage

This section covers sudden and accidental damage to your home and belongings.""",
                "page_number": 1,
                "chunk_index": 0,
                "section": "Section 1",
            },
            {
                "content": """Section 1.3: Water Damage Coverage

Cover includes damage caused by:
- Bursting of pipes within the insured premises
- Overflow from tanks, apparatus or pipes
- Water leakage from air-conditioning units
- Accidental discharge from fire sprinkler systems

This covers repair costs to affected areas including:
- Flooring (tiles, parquet, laminate)
- Walls and ceiling
- Electrical wiring if damaged
- Furniture and personal belongings

Maximum limit per occurrence: SGD 50,000
Deductible: SGD 500 per claim""",
                "page_number": 2,
                "chunk_index": 1,
                "section": "Section 1.3",
            },
            {
                "content": """Section 2: Personal Liability

We will pay all sums which you become legally liable to pay as damages for:
- Accidental bodily injury to any person
- Accidental damage to property belonging to others

Occurring during the period of insurance within Singapore and arising from:
- Your occupation of the insured premises
- Acts of your domestic servants

Maximum liability per occurrence: SGD 500,000""",
                "page_number": 3,
                "chunk_index": 2,
                "section": "Section 2",
            },
            {
                "content": """General Exclusions - MSIG Enhanced HomePlus

This policy does not cover:
1. Loss or damage caused by wear and tear, gradual deterioration, rust, mould or corrosion
2. Loss or damage caused by any process of cleaning, repairing, restoring or renovating
3. Loss or damage caused by insects, vermin or pests
4. Loss or damage caused by mechanical or electrical breakdown
5. Loss or damage caused by faulty workmanship or defective materials
6. Loss or damage caused by settling, shrinkage or expansion of buildings
7. Consequential loss of any kind including loss of use
8. Loss or damage whilst the premises are unoccupied for more than 60 consecutive days""",
                "page_number": 4,
                "chunk_index": 3,
                "section": "Exclusions",
            },
            {
                "content": """Claim Procedure - MSIG Singapore

To make a claim:
1. Report to us immediately, and in any event within 30 days
2. Report to the police within 24 hours if theft is involved
3. Provide all documentation including:
   - Completed claim form
   - Original receipts or valuations
   - Police report (if applicable)
   - Photos of damaged items

Do not dispose of damaged property until we have inspected it.

Claims hotline: 1800-888-8888 (24 hours)
Email: claims@msig.com.sg""",
                "page_number": 5,
                "chunk_index": 4,
                "section": "Claims",
            },
        ]
    
    def get_mock_zurich_au_policy(self) -> List[Dict[str, Any]]:
        """Return mock Zurich Australia Business Insurance policy chunks"""
        return [
            {
                "content": """Zurich Business Insurance - Section 2: Property Damage

We will cover physical loss or damage to insured property at the premises described in the schedule.

Insured property includes:
- Buildings owned by you
- Plant, machinery and equipment
- Stock and materials
- Office furniture and equipment
- Computer systems and data

Cover is provided on an agreed value or market value basis as stated in your schedule.""",
                "page_number": 1,
                "chunk_index": 0,
                "section": "Section 2",
            },
            {
                "content": """Section 2.4: Machinery Breakdown Coverage

Cover is provided for sudden and unforeseen physical damage to machinery caused by:
- Mechanical or electrical breakdown
- Short-circuiting, excessive electrical current
- Failure of safety devices
- Defects in materials or workmanship becoming apparent during the policy period

This includes:
- Repair or replacement costs
- Expediting expenses (overtime, express freight)
- Temporary hire of substitute machinery

Sub-limit: AUD 100,000 per item
Annual aggregate: AUD 500,000""",
                "page_number": 2,
                "chunk_index": 1,
                "section": "Section 2.4",
            },
            {
                "content": """Section 3: Business Interruption

We will pay for loss of gross profit resulting from interruption to your business caused by damage to property at your premises.

Cover includes:
- Reduction in turnover
- Increased cost of working
- Wages continuation (optional)

Indemnity period: 12 months (extendable to 24 or 36 months)

You must maintain adequate records of your business financial performance to support any claim.""",
                "page_number": 3,
                "chunk_index": 2,
                "section": "Section 3",
            },
            {
                "content": """Section 4: Public and Products Liability

We will pay all sums you become legally liable to pay for:
- Personal injury (including death, illness, disease)
- Property damage
- Advertising liability

Arising out of your business activities or your products.

Limit of liability: AUD 10,000,000 per occurrence
Annual aggregate: AUD 20,000,000

Includes defense costs up to the limit of liability.""",
                "page_number": 4,
                "chunk_index": 3,
                "section": "Section 4",
            },
            {
                "content": """General Exclusions - Zurich Business Insurance Australia

We do not cover loss or damage caused by or arising from:
1. War, invasion, hostilities, civil war, rebellion, revolution
2. Terrorism (terrorism cover available separately)
3. Nuclear reaction, radiation or contamination
4. Faulty workmanship, defective design, or failure to maintain equipment in proper working order
5. Gradual deterioration, wear and tear, rust, corrosion
6. Inherent vice or latent defect
7. Intentional acts by you or your employees
8. Pollution or contamination (unless sudden and accidental)
9. Cyber attack or data breach (cyber cover available separately)
10. Communicable disease or pandemic related closures""",
                "page_number": 5,
                "chunk_index": 4,
                "section": "General Exclusions",
            },
            {
                "content": """Making a Claim - Zurich Australia

In the event of a claim:
1. Notify us within 30 days of discovery
2. Take reasonable steps to mitigate further loss
3. Keep damaged property for inspection
4. Provide a detailed claim submission including:
   - Description of loss or damage
   - Cause and circumstances
   - Amount claimed with supporting evidence
   - Police report (if theft or malicious damage)

Claims line: 1800 611 116 (24/7)
Email: claims@zurich.com.au
Online: zurich.com.au/claims""",
                "page_number": 6,
                "chunk_index": 5,
                "section": "Claims",
            },
        ]
    
    async def ingest_mock_policies(self):
        """Ingest mock policy data for development/demo"""
        print("Ingesting MSIG Singapore HomePlus policy...")
        msig_chunks = self.get_mock_msig_sg_policy()
        count = await self.ingest_policy(
            policy_name="MSIG Enhanced HomePlus",
            region="SG",
            category="Home",
            chunks=msig_chunks,
        )
        print(f"  Ingested {count} chunks")
        
        print("Ingesting Zurich Australia Business policy...")
        zurich_chunks = self.get_mock_zurich_au_policy()
        count = await self.ingest_policy(
            policy_name="Zurich Business Insurance",
            region="AU",
            category="Business",
            chunks=zurich_chunks,
        )
        print(f"  Ingested {count} chunks")
        
        print("Done!")


async def main():
    """Main ingestion function"""
    rag_url = os.getenv("RAG_SERVICE_URL", "http://localhost:8002")
    
    ingester = PolicyIngester(rag_url)
    
    # Check for PDF files
    policies_dir = os.path.join(os.path.dirname(__file__), "..", "policies")
    
    if os.path.exists(policies_dir):
        for filename in os.listdir(policies_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(policies_dir, filename)
                print(f"Processing: {filename}")
                chunks = ingester.parse_pdf(pdf_path)
                print(f"  Extracted {len(chunks)} chunks")
    else:
        print("No policies directory found. Using mock data...")
        await ingester.ingest_mock_policies()


if __name__ == "__main__":
    asyncio.run(main())
