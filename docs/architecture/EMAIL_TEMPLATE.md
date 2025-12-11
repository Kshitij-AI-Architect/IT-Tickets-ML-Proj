# Email Template for Platform Team

---

**Subject**: Platform Services Request - Ticket Analytics Platform (AI/ML Project)

---

Hi [Platform Team],

I'm working on building an internal **Ticket Analytics Platform** that will help our support teams identify patterns in tickets, generate AI-powered insights, and learn from SME feedback over time.

## What We're Building

A web application that:
- **Clusters similar tickets** automatically using ML to identify recurring issues
- **Generates AI assessments** answering questions about ticket clusters (RAG-based)
- **Learns from SME corrections** to improve accuracy over time
- **Provides approval workflows** for Product Owners to review cluster resolutions

## Services We Need

I'd like to understand what's available in our organization and the process to get access:

### 1. Database
- **Need**: PostgreSQL with pgvector extension (for combined relational + vector storage)
- **Alternative**: Any SQL database + separate vector store
- **Size**: ~10GB initially, growing ~1GB/month

### 2. LLM Access
- **Need**: Azure OpenAI (GPT-4 or GPT-4o) for text generation
- **Usage**: ~1000 calls/day, ~50K tokens/day
- **Questions**: 
  - Do we have Azure OpenAI provisioned?
  - What models/deployments are available?
  - Is there an internal LLM gateway?

### 3. Embedding Service
- **Need**: Azure OpenAI Embeddings (text-embedding-3-small) OR ability to run Sentence Transformers locally
- **Usage**: ~1000 embeddings/day after initial bulk load

### 4. Vector Store
- **Preferred**: pgvector (PostgreSQL extension)
- **Alternative**: Azure AI Search, Pinecone, or other approved solution
- **Size**: ~100K vectors (1536 dimensions)

### 5. File Storage
- **Need**: Blob storage for uploaded CSV/Excel files
- **Size**: ~10GB with 90-day retention

### 6. Authentication
- **Need**: Integration with Azure AD/Entra ID for SSO
- **Alternative**: Existing auth service

### 7. Hosting
- **Need**: App Service or Container Apps for backend (Python/FastAPI) + frontend (React)
- **Resources**: 2 vCPU, 4GB RAM for backend

## Questions for You

1. **Which of these services are already available** that we can use?
2. **What's the provisioning process** for services we need to request?
3. **Are there any architectural patterns** or standards we should follow?
4. **Security/Compliance**: Any specific requirements for handling support ticket data?
5. **Cost allocation**: How does chargeback work for these services?

## Attached

I've attached a detailed architecture document with:
- High-level architecture diagram
- Data flow diagrams
- Detailed service requirements
- Multi-tenancy approach
- Security considerations

## Timeline

We're in the design phase and would like to start development in [X weeks]. An initial call to discuss would be very helpful.

Please let me know a good time to connect, or feel free to reply with any questions.

Thanks!
[Your Name]

---

## Follow-up Questions to Ask in Meeting

### Database
- [ ] Is pgvector available on our PostgreSQL instances?
- [ ] What's the process to provision a new database?
- [ ] Any existing multi-tenant patterns we should follow?
- [ ] Backup/DR policies?

### LLM/AI
- [ ] Which Azure OpenAI models are deployed?
- [ ] Rate limits and quotas?
- [ ] Is there prompt logging/monitoring?
- [ ] Any content filtering policies?

### Vector Store
- [ ] Approved vector database solutions?
- [ ] If not pgvector, what's recommended?
- [ ] Performance expectations for similarity search?

### Security
- [ ] Data classification for ticket data?
- [ ] Network requirements (internal only vs external)?
- [ ] Encryption requirements?
- [ ] Audit logging requirements?
- [ ] PII handling guidelines?

### DevOps
- [ ] Standard CI/CD pipeline?
- [ ] Container registry to use?
- [ ] Monitoring/alerting setup?
- [ ] Log aggregation solution?

### Cost
- [ ] How is Azure OpenAI usage charged back?
- [ ] Database cost model?
- [ ] Any budget approval needed?

