-- Ticket Analytics Platform - Database Schema
-- Run this in Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'analyst',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Schema mappings table
CREATE TABLE schema_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    source_column VARCHAR(255) NOT NULL,
    canonical_field VARCHAR(100) NOT NULL,
    transform VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(org_id, source_column)
);

-- Uploads table
CREATE TABLE uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500),
    row_count INTEGER DEFAULT 0,
    status VARCHAR(100) DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tickets table
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    upload_id UUID REFERENCES uploads(id) ON DELETE CASCADE,
    ticket_id VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(255),
    subcategory VARCHAR(255),
    priority VARCHAR(50),
    raw_data JSONB,
    embedding vector(384),  -- Dimension for all-MiniLM-L6-v2
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Clusters table
CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    upload_id UUID REFERENCES uploads(id) ON DELETE CASCADE,
    auto_name VARCHAR(255) NOT NULL,
    sme_name VARCHAR(255),
    summary TEXT,
    ticket_count INTEGER DEFAULT 0,
    centroid vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cluster-Ticket mapping
CREATE TABLE cluster_tickets (
    cluster_id UUID NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    PRIMARY KEY (cluster_id, ticket_id)
);


-- Knowledge entries table (SME feedback)
CREATE TABLE knowledge_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    cluster_id UUID REFERENCES clusters(id) ON DELETE SET NULL,
    category VARCHAR(255) NOT NULL,
    subcategory VARCHAR(255),
    current_process TEXT,
    automation_level VARCHAR(50) NOT NULL,
    tools_used JSONB DEFAULT '[]',
    blockers TEXT,
    resolution_steps JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'pending',
    submitted_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_id UUID REFERENCES knowledge_entries(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    actor_id UUID REFERENCES users(id),
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_tickets_org ON tickets(org_id);
CREATE INDEX idx_tickets_upload ON tickets(upload_id);
CREATE INDEX idx_clusters_org ON clusters(org_id);
CREATE INDEX idx_clusters_upload ON clusters(upload_id);
CREATE INDEX idx_knowledge_org_status ON knowledge_entries(org_id, status);
CREATE INDEX idx_schema_mappings_org ON schema_mappings(org_id);

-- Vector similarity search function for RAG
CREATE OR REPLACE FUNCTION search_knowledge(
    query_embedding vector(384),
    match_org_id UUID,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 3
)
RETURNS TABLE (
    id UUID,
    org_id UUID,
    category VARCHAR,
    subcategory VARCHAR,
    current_process TEXT,
    automation_level VARCHAR,
    tools_used JSONB,
    blockers TEXT,
    resolution_steps JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ke.id,
        ke.org_id,
        ke.category,
        ke.subcategory,
        ke.current_process,
        ke.automation_level,
        ke.tools_used,
        ke.blockers,
        ke.resolution_steps,
        1 - (ke.embedding <=> query_embedding) AS similarity
    FROM knowledge_entries ke
    WHERE ke.org_id = match_org_id
      AND ke.status = 'approved'
      AND ke.embedding IS NOT NULL
      AND 1 - (ke.embedding <=> query_embedding) > match_threshold
    ORDER BY ke.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Row Level Security (RLS) policies for multi-tenant isolation
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE schema_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE clusters ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Note: In production, add RLS policies based on your auth setup
-- For development with service key, RLS is bypassed
