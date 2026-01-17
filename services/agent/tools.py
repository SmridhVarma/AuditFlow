"""
RAG Tools for the Agent to call
Wraps the RAG service API
"""

import logging
from typing import List, Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)


class RAGTools:
    """Tools for interacting with the RAG service"""
    
    def __init__(self, rag_service_url: str):
        self.rag_service_url = rag_service_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_clauses(
        self,
        query: str,
        region: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant policy clauses.
        
        Args:
            query: The search query
            region: Filter by region (SG/AU)
            category: Filter by category (Home/Business)
            top_k: Number of results to return
            
        Returns:
            List of matching policy chunks
        """
        try:
            response = await self.client.post(
                f"{self.rag_service_url}/search",
                json={
                    "query": query,
                    "region": region,
                    "category": category,
                    "top_k": top_k,
                    "min_score": 0.4,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("chunks", [])
            else:
                logger.error(f"RAG search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            # Return mock data for development/testing
            return self._mock_clauses(query, region, category)
    
    async def search_exclusions(
        self,
        query: str,
        region: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for exclusion clauses.
        
        Args:
            query: The search query
            region: Filter by region
            category: Filter by category
            
        Returns:
            List of exclusion clauses
        """
        try:
            response = await self.client.post(
                f"{self.rag_service_url}/search/exclusions",
                json={
                    "query": query,
                    "region": region,
                    "category": category,
                    "top_k": 5,
                    "min_score": 0.3,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("chunks", [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Exclusion search error: {e}")
            return self._mock_exclusions(region, category)
    
    async def search_limits(
        self,
        query: str,
        region: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for coverage limits.
        
        Args:
            query: The search query
            region: Filter by region
            category: Filter by category
            
        Returns:
            List of limit clauses
        """
        try:
            response = await self.client.post(
                f"{self.rag_service_url}/search/limits",
                json={
                    "query": query,
                    "region": region,
                    "category": category,
                    "top_k": 3,
                    "min_score": 0.3,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("chunks", [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Limits search error: {e}")
            return self._mock_limits(region, category)
    
    def _mock_clauses(
        self,
        query: str,
        region: Optional[str],
        category: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Return mock clauses for development/testing"""
        if region == "SG" and category == "Home":
            return [
                {
                    "content": "Section 1: Loss or Damage to Building and Contents. We will pay for loss or damage to the building and contents caused by water damage from bursting, leaking or overflowing of water tanks, apparatus or pipes.",
                    "policy_name": "MSIG Enhanced HomePlus",
                    "section": "Section 1",
                    "similarity_score": 0.85,
                },
                {
                    "content": "Cover includes damage caused by air-conditioning units including water leakage. This covers repair costs to affected areas including flooring, walls, and ceiling.",
                    "policy_name": "MSIG Enhanced HomePlus",
                    "section": "Section 1.3",
                    "similarity_score": 0.82,
                },
            ]
        elif region == "AU" and category == "Business":
            return [
                {
                    "content": "Property Damage Cover: We will cover physical loss or damage to insured property at the premises described in the schedule. This includes buildings, plant, machinery, and stock.",
                    "policy_name": "Zurich Business Insurance",
                    "section": "Section 2",
                    "similarity_score": 0.80,
                },
                {
                    "content": "Machinery Breakdown: Cover is provided for sudden and unforeseen physical damage to machinery caused by mechanical or electrical breakdown.",
                    "policy_name": "Zurich Business Insurance",
                    "section": "Section 2.4",
                    "similarity_score": 0.78,
                },
            ]
        return []
    
    def _mock_exclusions(
        self,
        region: Optional[str],
        category: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Return mock exclusions for development/testing"""
        if region == "SG" and category == "Home":
            return [
                {
                    "content": "Exclusion: Loss or damage caused by wear and tear, gradual deterioration, rust, or corrosion of pipes and apparatus.",
                    "policy_name": "MSIG Enhanced HomePlus",
                    "section": "Exclusions",
                    "similarity_score": 0.70,
                },
            ]
        elif region == "AU" and category == "Business":
            return [
                {
                    "content": "Exclusion: We do not cover loss or damage caused by faulty workmanship, defective design, or failure to maintain equipment in proper working order.",
                    "policy_name": "Zurich Business Insurance",
                    "section": "General Exclusions",
                    "similarity_score": 0.72,
                },
            ]
        return []
    
    def _mock_limits(
        self,
        region: Optional[str],
        category: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Return mock limits for development/testing"""
        if region == "SG" and category == "Home":
            return [
                {
                    "content": "Maximum Limit: Water damage claims are subject to a maximum limit of SGD 50,000 per occurrence with a deductible of SGD 500.",
                    "policy_name": "MSIG Enhanced HomePlus",
                    "section": "Limits",
                    "similarity_score": 0.75,
                },
            ]
        elif region == "AU" and category == "Business":
            return [
                {
                    "content": "Sum Insured: Property damage is covered up to the sum insured stated in the schedule. Machinery breakdown has a sub-limit of AUD 100,000 per item.",
                    "policy_name": "Zurich Business Insurance",
                    "section": "Limits of Liability",
                    "similarity_score": 0.73,
                },
            ]
        return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
