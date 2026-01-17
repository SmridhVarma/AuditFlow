-- AuditFlow Database Schema
-- PostgreSQL with pgvector extension

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Policy chunks table for RAG
CREATE TABLE IF NOT EXISTS policy_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),  -- sentence-transformers dimension
    region VARCHAR(10) NOT NULL CHECK (region IN ('SG', 'AU')),
    category VARCHAR(50) NOT NULL CHECK (category IN ('Home', 'Business', 'General')),
    policy_name VARCHAR(200) NOT NULL,
    section VARCHAR(200),
    subsection VARCHAR(200),
    page_number INTEGER,
    chunk_index INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Claims history table
CREATE TABLE IF NOT EXISTS claims (
    id SERIAL PRIMARY KEY,
    claim_id UUID DEFAULT gen_random_uuid(),
    claim_text TEXT NOT NULL,
    region VARCHAR(10),
    category VARCHAR(50),
    router_confidence FLOAT,
    status VARCHAR(50) DEFAULT 'pending',
    reasoning_trace JSONB,
    decision TEXT,
    pdf_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs for compliance
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    claim_id UUID,
    action VARCHAR(100) NOT NULL,
    service VARCHAR(50) NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_policy_chunks_region ON policy_chunks(region);
CREATE INDEX IF NOT EXISTS idx_policy_chunks_category ON policy_chunks(category);
CREATE INDEX IF NOT EXISTS idx_policy_chunks_region_category ON policy_chunks(region, category);
CREATE INDEX IF NOT EXISTS idx_claims_claim_id ON claims(claim_id);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_claim_id ON audit_logs(claim_id);

-- Create vector similarity search index (IVFFlat for approximate search)
CREATE INDEX IF NOT EXISTS idx_policy_chunks_embedding ON policy_chunks 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating timestamps
CREATE TRIGGER update_policy_chunks_updated_at 
    BEFORE UPDATE ON policy_chunks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_claims_updated_at 
    BEFORE UPDATE ON claims 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (for containerized setup)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO auditflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO auditflow;
