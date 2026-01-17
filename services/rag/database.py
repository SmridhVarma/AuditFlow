"""
Database manager for pgvector operations
"""

import logging
from typing import Optional, List, Dict, Any

import asyncpg
from asyncpg import Pool, Connection
import numpy as np

from schemas import PolicyChunk, ChunkInput

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL connections and vector operations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[Pool] = None
    
    async def initialize(self):
        """Initialize connection pool"""
        # Parse the database URL for asyncpg
        # Convert postgresql:// to match asyncpg format
        db_url = self.database_url.replace("postgresql://", "postgres://")
        
        self.pool = await asyncpg.create_pool(
            db_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        logger.info("Database connection pool initialized")
    
    async def close(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def is_connected(self) -> bool:
        """Check if database is connected"""
        if self.pool is None:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
    
    async def search_similar(
        self,
        embedding: List[float],
        region: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> List[PolicyChunk]:
        """
        Search for similar policy chunks using cosine similarity.
        Applies metadata filters for region and category.
        """
        if self.pool is None:
            raise RuntimeError("Database not initialized")
        
        # Build query with optional filters
        base_query = """
            SELECT 
                id,
                content,
                region,
                category,
                policy_name,
                section,
                subsection,
                page_number,
                chunk_index,
                metadata,
                1 - (embedding <=> $1::vector) as similarity_score
            FROM policy_chunks
            WHERE 1=1
        """
        
        params = [str(embedding)]
        param_idx = 2
        
        if region:
            base_query += f" AND region = ${param_idx}"
            params.append(region)
            param_idx += 1
        
        if category:
            base_query += f" AND category = ${param_idx}"
            params.append(category)
            param_idx += 1
        
        base_query += f" AND 1 - (embedding <=> $1::vector) >= ${param_idx}"
        params.append(min_score)
        param_idx += 1
        
        base_query += f"""
            ORDER BY embedding <=> $1::vector
            LIMIT ${param_idx}
        """
        params.append(top_k)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(base_query, *params)
        
        results = []
        for row in rows:
            chunk = PolicyChunk(
                id=row["id"],
                content=row["content"],
                region=row["region"],
                category=row["category"],
                policy_name=row["policy_name"],
                section=row["section"],
                subsection=row["subsection"],
                page_number=row["page_number"],
                chunk_index=row["chunk_index"],
                similarity_score=float(row["similarity_score"]),
                metadata=dict(row["metadata"]) if row["metadata"] else {},
            )
            results.append(chunk)
        
        return results
    
    async def insert_chunks(
        self,
        chunks: List[ChunkInput],
        embeddings: List[List[float]],
    ) -> int:
        """Insert policy chunks with their embeddings"""
        if self.pool is None:
            raise RuntimeError("Database not initialized")
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        insert_query = """
            INSERT INTO policy_chunks 
            (content, embedding, region, category, policy_name, section, subsection, page_number, chunk_index, metadata)
            VALUES ($1, $2::vector, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        inserted = 0
        async with self.pool.acquire() as conn:
            for chunk, embedding in zip(chunks, embeddings):
                try:
                    await conn.execute(
                        insert_query,
                        chunk.content,
                        str(embedding),
                        chunk.region,
                        chunk.category,
                        chunk.policy_name,
                        chunk.section,
                        chunk.subsection,
                        chunk.page_number,
                        chunk.chunk_index,
                        chunk.metadata or {},
                    )
                    inserted += 1
                except Exception as e:
                    logger.error(f"Failed to insert chunk: {e}")
        
        return inserted
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if self.pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self.pool.acquire() as conn:
            total_chunks = await conn.fetchval("SELECT COUNT(*) FROM policy_chunks")
            
            region_counts = await conn.fetch("""
                SELECT region, COUNT(*) as count 
                FROM policy_chunks 
                GROUP BY region
            """)
            
            category_counts = await conn.fetch("""
                SELECT category, COUNT(*) as count 
                FROM policy_chunks 
                GROUP BY category
            """)
            
            policy_counts = await conn.fetch("""
                SELECT policy_name, COUNT(*) as count 
                FROM policy_chunks 
                GROUP BY policy_name
            """)
        
        return {
            "total_chunks": total_chunks,
            "by_region": {row["region"]: row["count"] for row in region_counts},
            "by_category": {row["category"]: row["count"] for row in category_counts},
            "by_policy": {row["policy_name"]: row["count"] for row in policy_counts},
        }
    
    async def delete_policy(self, policy_name: str) -> int:
        """Delete all chunks for a specific policy"""
        if self.pool is None:
            raise RuntimeError("Database not initialized")
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM policy_chunks WHERE policy_name = $1",
                policy_name,
            )
            # Parse the DELETE count from result
            count = int(result.split()[-1]) if result else 0
        
        return count
