"""
Seed the database with mock policy data
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.ingestion.ingest import PolicyIngester


async def main():
    """Seed the database with mock policies"""
    rag_url = os.getenv("RAG_SERVICE_URL", "http://localhost:8002")
    
    print("="*60)
    print("AuditFlow Database Seeding")
    print("="*60)
    
    ingester = PolicyIngester(rag_url)
    
    try:
        await ingester.ingest_mock_policies()
        print("\n✅ Database seeded successfully!")
        print("\nPolicies ingested:")
        print("  - MSIG Enhanced HomePlus (Singapore, Home)")
        print("  - Zurich Business Insurance (Australia, Business)")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        print("\nMake sure the RAG service is running:")
        print("  docker-compose up rag")


if __name__ == "__main__":
    asyncio.run(main())
