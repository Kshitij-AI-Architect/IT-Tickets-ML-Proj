# Ticket Analytics Platform

A production-ready, scalable ticket analytics platform with RAG-based learning, multi-tenant support, and PO approval workflows.

## Features

- **Ticket Clustering**: Automatically groups similar tickets using ML
- **RAG-based Assessments**: AI-powered answers grounded in your ticket data
- **SME Feedback Loop**: Learn from expert corrections to improve over time
- **PO Approval Workflow**: Review and approve cluster resolutions
- **Multi-tenant**: Isolated data per organization
- **Modular Architecture**: Easily swap services (database, LLM, storage)

## Tech Stack

### Backend
- FastAPI (Python)
- Supabase (PostgreSQL + pgvector)
- Azure OpenAI
- Sentence Transformers (embeddings)

### Frontend
- React + TypeScript
- Vite
- TailwindCSS
- React Query
- Zustand

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Supabase account (free tier)
- Azure OpenAI access

### Setup

1. Clone and configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

2. Initialize database:
```bash
# Run database/schema.sql in your Supabase SQL editor
```

3. Start backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

4. Start frontend:
```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Business logic
│   │   │   ├── database/ # DB adapters
│   │   │   ├── embeddings/
│   │   │   ├── llm/
│   │   │   └── storage/
│   │   └── utils/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/          # API & queries
│   │   ├── stores/       # Zustand stores
│   │   └── types/
│   └── package.json
├── database/
│   └── schema.sql
└── docker-compose.yml
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | User authentication |
| `/api/upload/tickets` | POST | Upload ticket data |
| `/api/clusters` | GET | List clusters |
| `/api/clusters/run` | POST | Run clustering |
| `/api/assessments/generate` | POST | Generate AI assessment |
| `/api/feedback` | POST | Submit SME feedback |
| `/api/approval/{id}/approve` | POST | Approve cluster |
| `/api/knowledge` | GET/POST | Knowledge base |

## Configuration

### Swapping Services

The platform uses abstract interfaces for easy service swapping:

```python
# Use different database
from app.services.database import PostgresDatabase
db = PostgresDatabase(connection_string)

# Use different LLM
from app.services.llm import OpenAIService
llm = OpenAIService(api_key)
```

## License

MIT
