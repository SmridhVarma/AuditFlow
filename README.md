# 🔍 AuditFlow

**Agentic & Explainable Claims Processing System**

An enterprise-grade microservice architecture for automated regional claims triage with 100% decision transparency.

## 🎯 Overview

AuditFlow solves the "Black Box AI" problem in insurance claims processing by:
- **Enforcing Regional Routing**: Claims are classified to the correct region (Singapore/Australia) before policy lookup
- **Metadata-Filtered RAG**: Semantic search is scoped to the correct policy documents
- **Transparent Reasoning**: Every decision includes a downloadable "Reasoning Trace" PDF

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                      │
│                 Claims Command Center - :8501                │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│  Router   │ │    RAG    │ │   Agent   │ │ Reporter  │
│ :8001     │ │   :8002   │ │  :8003    │ │  :8004    │
│ DistilBERT│ │ pgvector  │ │ LangGraph │ │ ReportLab │
└───────────┘ └─────┬─────┘ └───────────┘ └───────────┘
                    │
              ┌─────▼─────┐
              │ PostgreSQL│
              │ + pgvector│
              │   :5432   │
              └───────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (for the reasoning agent)

### 1. Clone and Configure

```bash
cd auditflow
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start All Services

```bash
docker-compose up --build
```

### 3. Seed the Database

```bash
# In a new terminal
docker-compose exec rag python -c "
import asyncio
from data.ingestion.ingest import PolicyIngester
asyncio.run(PolicyIngester().ingest_mock_policies())
"
```

### 4. Access the Application

Open http://localhost:8501 in your browser.

## 📁 Project Structure

```
auditflow/
├── docker-compose.yml          # Orchestration
├── .env.example                # Environment template
├── frontend/                   # Streamlit UI
│   ├── app.py                  # Claims Command Center
│   └── Dockerfile
├── services/
│   ├── router/                 # Service A: Intent Router
│   │   ├── main.py             # FastAPI app
│   │   └── models/classifier.py # DistilBERT classifier
│   ├── rag/                    # Service B: RAG Engine
│   │   ├── main.py             # FastAPI app
│   │   ├── database.py         # pgvector operations
│   │   └── embeddings.py       # Sentence transformers
│   ├── agent/                  # Service C: Reasoning Agent
│   │   ├── main.py             # FastAPI app
│   │   ├── graph.py            # LangGraph ReAct agent
│   │   └── tools.py            # RAG API tools
│   └── reporter/               # Service D: PDF Generator
│       ├── main.py             # FastAPI app
│       └── pdf_generator.py    # ReportLab PDF
├── data/
│   ├── ingestion/ingest.py     # PDF parsing & ingestion
│   └── evaluation/             # Test claims
└── scripts/
    ├── init_db.sql             # Database schema
    ├── seed_data.py            # Data seeding
    └── evaluate_routing.py     # Accuracy testing
```

## 🧪 Testing

### Test with Sample Claims

**Singapore Home Claim:**
```
Water leak from my air-con unit in Bedok caused damage to my living room floor.
```

**Australia Business Claim:**
```
Machinery breakdown at my Sydney warehouse has caused production to halt.
```

### Run Routing Evaluation

```bash
python scripts/evaluate_routing.py
```

## 📊 API Endpoints

| Service | Port | Endpoints |
|---------|------|-----------|
| Router | 8001 | `POST /classify` - Classify claim region |
| RAG | 8002 | `POST /search` - Semantic search |
| Agent | 8003 | `POST /analyze` - Full analysis |
| Reporter | 8004 | `POST /generate-report` - PDF generation |

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Required for reasoning agent |
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password |
| `LLM_MODEL` | Model name (default: gpt-4o-mini) |

## 📝 Policy Documents

The system is pre-configured with mock policies for:
- **MSIG Enhanced HomePlus** (Singapore, Home)
- **Zurich Business Insurance** (Australia, Business)

To add real policies, place PDFs in `data/policies/` and run the ingestion script.

## 🏆 Success Metrics

| Metric | Target |
|--------|--------|
| Routing Accuracy | >95% |
| RAG Precision | >90% |
| PDF Generation | 100% |
| Response Time | <5s |

## 📚 Further Reading

- [Why Microservices for Production AI Agents](docs/microservices.md)
- [Enforcing Regional Logic with pgvector](docs/metadata-filtering.md)
- [Solving the Black-Box Problem](docs/explainability.md)

---

**Project Lead:** Smridh Varma  
**Version:** 1.0  
**License:** MIT
