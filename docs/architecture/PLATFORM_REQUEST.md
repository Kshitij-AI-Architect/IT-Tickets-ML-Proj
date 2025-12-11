# Ticket Analytics Platform - Platform Services Request

## Executive Summary

We're building an internal **Ticket Analytics Platform** that uses AI/ML to:
1. Automatically cluster similar support tickets to identify patterns
2. Generate AI-powered assessments/answers grounded in ticket data
3. Learn from SME (Subject Matter Expert) feedback to improve over time
4. Provide PO (Product Owner) approval workflow for cluster resolutions

This document outlines the platform services required and questions for the platform team.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USERS                                          │
│         (SMEs, Product Owners, Analysts, Admins)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React SPA)                                │
│   • Dashboard & Analytics    • Ticket Upload    • Cluster Management       │
│   • Assessment Q&A           • Approval Workflow • Knowledge Base          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY / LOAD BALANCER                         │
│                    (Authentication, Rate Limiting, SSL)                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND API (FastAPI/Python)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Auth      │  │   Upload    │  │  Clustering │  │ Assessment  │       │
│  │   Service   │  │   Service   │  │   Service   │  │  (RAG)      │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                        │
│  │  Feedback   │  │  Approval   │  │  Analytics  │                        │
│  │  Service    │  │  Workflow   │  │   Service   │                        │
│  └─────────────┘  └─────────────┘  └─────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                       │                    │
        ┌───────────┴───────────┐          │          ┌─────────┴─────────┐
        ▼                       ▼          ▼          ▼                   ▼
┌───────────────┐    ┌───────────────┐  ┌─────────────────┐    ┌───────────────┐
│   DATABASE    │    │ VECTOR STORE  │  │   LLM SERVICE   │    │    STORAGE    │
│  (PostgreSQL) │    │  (pgvector/   │  │ (Azure OpenAI / │    │ (Blob/S3/     │
│               │    │   Pinecone)   │  │  Bedrock/etc)   │    │  Local)       │
│ • Users       │    │               │  │                 │    │               │
│ • Tickets     │    │ • Ticket      │  │ • GPT-4/Claude  │    │ • Uploaded    │
│ • Clusters    │    │   Embeddings  │  │ • Text Gen      │    │   Files       │
│ • Knowledge   │    │ • Knowledge   │  │ • Summarization │    │ • Exports     │
│ • Feedback    │    │   Embeddings  │  │                 │    │               │
│ • Approvals   │    │               │  │                 │    │               │
└───────────────┘    └───────────────┘  └─────────────────┘    └───────────────┘
                              │                   │
                              ▼                   │
                    ┌───────────────┐             │
                    │  EMBEDDING    │◄────────────┘
                    │   SERVICE     │
                    │ (Azure OpenAI │
                    │  Embeddings / │
                    │  Sentence     │
                    │  Transformers)│
                    └───────────────┘
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW                                       │
└──────────────────────────────────────────────────────────────────────────┘

1. TICKET INGESTION FLOW
   ┌─────────┐    ┌─────────┐    ┌───────────┐    ┌──────────┐
   │ Upload  │───▶│ Parse & │───▶│ Generate  │───▶│  Store   │
   │ CSV/JSON│    │ Validate│    │ Embedding │    │ in DB +  │
   └─────────┘    └─────────┘    └───────────┘    │ Vector   │
                                                   └──────────┘

2. CLUSTERING FLOW
   ┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
   │ Fetch    │───▶│ Cluster   │───▶│ Generate  │───▶│ Store    │
   │ Ticket   │    │ by Vector │    │ Cluster   │    │ Clusters │
   │ Vectors  │    │ Similarity│    │ Summary   │    │          │
   └──────────┘    └───────────┘    └───────────┘    └──────────┘

3. RAG ASSESSMENT FLOW
   ┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
   │ User     │───▶│ Embed     │───▶│ Retrieve  │───▶│ Generate │
   │ Question │    │ Question  │    │ Relevant  │    │ Answer   │
   └──────────┘    └───────────┘    │ Context   │    │ via LLM  │
                                    └───────────┘    └──────────┘

4. FEEDBACK LEARNING FLOW
   ┌──────────┐    ┌───────────┐    ┌───────────┐
   │ SME      │───▶│ Store     │───▶│ Add to    │
   │ Feedback │    │ Correction│    │ Knowledge │
   └──────────┘    └───────────┘    │ Base      │
                                    └───────────┘
```

---

## Services Required

### 1. DATABASE (Required)
**Purpose**: Store all application data - users, tickets, clusters, feedback, approvals

| Option | Notes |
|--------|-------|
| PostgreSQL (with pgvector extension) | Preferred - combines relational + vector in one DB |
| Azure SQL + separate vector store | If pgvector not available |
| Existing enterprise DB | Need vector store separately |

**Estimated Storage**: 
- Initial: ~10GB (100K tickets)
- Growth: ~1GB/month

**Questions for Platform Team**:
- Do we have PostgreSQL with pgvector extension available?
- What's the provisioning process for a new database?
- Is there an existing multi-tenant database pattern we should follow?
- What's the backup/DR policy?

---

### 2. VECTOR STORE (Required)
**Purpose**: Store and search embeddings for semantic similarity (clustering, RAG retrieval)

| Option | Notes |
|--------|-------|
| pgvector (PostgreSQL extension) | Simplest - same DB for everything |
| Azure AI Search | Enterprise option with hybrid search |
| Pinecone | Managed, scalable, but external |
| Qdrant / Weaviate | Self-hosted alternatives |

**Estimated Vectors**:
- ~100K ticket embeddings (1536 dimensions each)
- ~10K knowledge base embeddings
- Index size: ~500MB - 1GB

**Questions for Platform Team**:
- Is pgvector available on our PostgreSQL instances?
- Do we have Azure AI Search provisioned?
- Any approved vector database solutions?

---

### 3. LLM SERVICE (Required)
**Purpose**: Generate cluster summaries, answer questions, analyze tickets

| Option | Notes |
|--------|-------|
| Azure OpenAI (GPT-4 / GPT-4o) | Preferred if available |
| AWS Bedrock (Claude) | Alternative |
| Internal LLM Gateway | If org has one |

**Estimated Usage**:
- ~1000 API calls/day initially
- ~50K tokens/day average
- Batch processing for clustering (can be scheduled off-peak)

**Questions for Platform Team**:
- Do we have Azure OpenAI access? Which models/deployments?
- Is there an internal LLM gateway or API we should use?
- What are the rate limits and quotas?
- Is there a cost allocation/chargeback model?

---

### 4. EMBEDDING SERVICE (Required)
**Purpose**: Convert text to vectors for similarity search

| Option | Notes |
|--------|-------|
| Azure OpenAI Embeddings (text-embedding-ada-002 / text-embedding-3-small) | Best quality, requires API |
| Sentence Transformers (local) | Free, runs on CPU, good quality |
| Cohere Embeddings | Alternative managed service |

**Estimated Usage**:
- Initial bulk: ~100K embeddings
- Ongoing: ~1000 embeddings/day

**Questions for Platform Team**:
- Can we use Azure OpenAI embedding models?
- Is there compute available for running local embedding models?
- Any existing embedding service we should integrate with?

---

### 5. FILE STORAGE (Required)
**Purpose**: Store uploaded ticket files (CSV, Excel, JSON)

| Option | Notes |
|--------|-------|
| Azure Blob Storage | Preferred for Azure environment |
| AWS S3 | If AWS-based |
| Local/NFS | For on-prem |

**Estimated Storage**:
- ~10GB initially
- Files retained for 90 days (configurable)

**Questions for Platform Team**:
- What's our standard blob/object storage solution?
- Any existing storage accounts we can use?
- What's the retention policy?

---

### 6. AUTHENTICATION (Required)
**Purpose**: User authentication and authorization

| Option | Notes |
|--------|-------|
| Azure AD / Entra ID | SSO with corporate identity |
| Existing Auth Service | If org has one |
| JWT-based (standalone) | Fallback option |

**Questions for Platform Team**:
- Should we integrate with Azure AD/Entra ID?
- Is there an existing auth service or identity provider?
- What roles/permissions model should we follow?

---

### 7. HOSTING / COMPUTE (Required)
**Purpose**: Run the backend API and frontend

| Option | Notes |
|--------|-------|
| Azure App Service | Simple PaaS option |
| Azure Container Apps | Container-based, scalable |
| Kubernetes (AKS) | If org standard |
| VMs | Traditional option |

**Estimated Resources**:
- Backend: 2 vCPU, 4GB RAM (can scale)
- Frontend: Static hosting or 1 vCPU, 1GB RAM

**Questions for Platform Team**:
- What's our standard hosting platform?
- Is there a container registry we should use?
- CI/CD pipeline requirements?

---

## Security & Compliance Questions

1. **Data Classification**: What classification level for support ticket data?
2. **Network**: Should this be internal-only or accessible externally?
3. **Encryption**: Requirements for data at rest and in transit?
4. **Audit Logging**: What events need to be logged?
5. **Data Retention**: How long should we retain ticket data?
6. **PII Handling**: Any specific requirements for handling PII in tickets?

---

## Multi-Tenancy Approach

The platform supports multiple organizations/teams with data isolation:

```
┌─────────────────────────────────────────┐
│           MULTI-TENANT MODEL            │
├─────────────────────────────────────────┤
│  Organization A    │  Organization B    │
│  ┌─────────────┐  │  ┌─────────────┐   │
│  │ Users       │  │  │ Users       │   │
│  │ Tickets     │  │  │ Tickets     │   │
│  │ Clusters    │  │  │ Clusters    │   │
│  │ Knowledge   │  │  │ Knowledge   │   │
│  └─────────────┘  │  └─────────────┘   │
│  (org_id = A)     │  (org_id = B)      │
└─────────────────────────────────────────┘
```

All tables include `org_id` for row-level isolation.

---

## Summary of Required Services

| Service | Priority | Purpose |
|---------|----------|---------|
| PostgreSQL + pgvector | P0 | Data + Vector storage |
| Azure OpenAI (GPT-4) | P0 | LLM for summaries/Q&A |
| Azure OpenAI Embeddings | P0 | Text vectorization |
| Blob Storage | P1 | File uploads |
| Azure AD Integration | P1 | Authentication |
| App Service / Container Apps | P1 | Hosting |

---

## Next Steps

1. Platform team to confirm available services
2. Provision required resources
3. Share connection strings / API keys
4. Configure network access
5. Begin integration testing

