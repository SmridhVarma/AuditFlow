# 🔍 AuditFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Deployed on Railway](https://img.shields.io/badge/Deployed-Railway-0B0D0E.svg)](https://railway.app/)

**Agentic & Explainable Claims Processing System**

An enterprise-grade microservice architecture for automated regional claims triage with **100% decision transparency** — solving the "Black Box AI" problem in insurance.

---

## 🎯 The Problem We're Solving

### The Black Box Crisis in Insurance AI

Traditional AI systems in insurance operate as opaque "black boxes," making critical decisions about claims without providing explanations. This creates serious real-world consequences:

> **⚠️ UnitedHealthcare Lawsuit (2023)**: Plaintiffs alleged an AI model with a **90% error rate** was used to deny care to elderly patients, even when physicians deemed treatment medically necessary. Employees were reportedly disciplined for approving services the algorithm flagged for denial.
> — *Source: Federal Class Action Lawsuit*

> **⚠️ Industry-Wide Litigation**: Major insurers including Cigna, Humana, and UnitedHealth face class-action lawsuits alleging AI-driven tools deny claims based on statistical predictions rather than individual medical necessity.
> — *Forbes, 2024*

> **⚠️ Algorithmic Bias**: AI systems trained on historical data can perpetuate discriminatory patterns, with some demographic groups experiencing longer wait times and additional hurdles for claim approvals.
> — *Insurance Research Council*

### Why Explainability Matters

| Impact Area | Black Box AI Problem | AuditFlow Solution |
|-------------|---------------------|-------------------|
| **Compliance** | Cannot prove GDPR/CCPA adherence | Full reasoning trace for every decision |
| **Trust** | Claimants don't understand denials | Downloadable PDF audit reports |
| **Oversight** | Auditors can't verify logic | Step-by-step agent thought process |
| **Fairness** | Hidden bias goes undetected | Transparent policy citation |

---

## 💡 Our Solution

AuditFlow tackles the black box problem through a **three-pillar architecture**:

```
┌──────────────────────────────────────────────────────────────────┐
│  1️⃣ TRANSPARENT ROUTING                                          │
│     Hybrid DistilBERT + keyword classifier                       │
│     → Explains WHY a claim routes to Singapore vs Australia      │
├──────────────────────────────────────────────────────────────────┤
│  2️⃣ GROUNDED RETRIEVAL                                           │
│     Metadata-filtered RAG with pgvector                          │
│     → Cites EXACTLY which policy clauses apply                   │
├──────────────────────────────────────────────────────────────────┤
│  3️⃣ TRACED DECISIONS                                             │
│     LangGraph ReAct agent with Gemini 2.0 Flash                  │
│     → Records EVERY reasoning step: Think → Act → Observe        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         Frontend (Streamlit)            │
                    │      Claims Command Center - :8501      │
                    │          Dark Mode • Real-time          │
                    └─────────────────┬───────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  🔀 Router      │       │  🔍 RAG Engine  │       │  🤖 Agent       │
│     :8001       │       │     :8002       │       │     :8003       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ DistilBERT +    │       │ pgvector +      │       │ LangGraph +     │
│ Keyword Rules   │       │ Sentence-       │       │ Gemini 2.0      │
│                 │       │ Transformers    │       │ Flash           │
│ Hybrid Multi-   │       │ Metadata-       │       │ ReAct Pattern   │
│ Class Classifier│       │ Filtered Search │       │ Think→Act→Decide│
└─────────────────┘       └────────┬────────┘       └─────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │     📊 Neon Serverless PostgreSQL       │
                    │           + pgvector Extension          │
                    │         384-dim Embeddings (IVFFlat)    │
                    └─────────────────────────────────────────┘

                    ┌─────────────────────────────────────────┐
                    │           📄 Reporter :8004             │
                    │     ReportLab PDF Audit Generation      │
                    └─────────────────────────────────────────┘
```

### 🔧 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit | Claims Command Center with dark mode UI |
| **Router** | DistilBERT + Keywords | Hybrid region/category classification |
| **RAG** | pgvector + sentence-transformers | Semantic search with metadata filtering |
| **Agent** | LangGraph + Gemini 2.0 Flash | ReAct reasoning with tool use |
| **Reporter** | ReportLab | Professional PDF audit reports |
| **Database** | Neon Serverless PostgreSQL | Vector storage with pgvector |
| **Deployment** | Railway.app | Production microservice hosting |

---

## 📊 Performance Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Routing Accuracy** | >95% | Tested on 15 synthetic claims (SG/AU × Home/Business) |
| **RAG Precision@5** | >90% | Metadata-filtered retrieval accuracy |
| **Decision Explainability** | 100% | Every claim includes full reasoning trace |
| **End-to-End Latency** | <5s | From submission to decision |
| **PDF Generation** | 100% | Audit-ready reports for all processed claims |
| **Regional Precision** | 100% | Keywords like "Bedok" always route to SG |

### Evaluation Dataset

The system is tested against **15 synthetic claims** covering:
- **7 Singapore Home Claims** (water damage, pipe burst, theft, fire, etc.)
- **8 Australia Business Claims** (machinery, liability, storm damage, etc.)
- Mix of COVERED, NOT_COVERED, PARTIAL, and NEEDS_REVIEW outcomes

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google API key (for Gemini 2.0 Flash reasoning agent)

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/auditflow.git
cd auditflow
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 2. Start All Services (Local Development)

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

---

## 📁 Project Structure

```
auditflow/
├── docker-compose.yml              # Local orchestration
├── railway.json                    # Railway deployment config
├── .env.example                    # Environment template
│
├── frontend/                       # Streamlit UI
│   ├── app.py                      # Claims Command Center (46KB, dark mode)
│   ├── hero.png                    # Hero image asset
│   └── Dockerfile
│
├── services/
│   ├── router/                     # Service A: Intent Router
│   │   ├── main.py                 # FastAPI app with /classify endpoint
│   │   ├── models/classifier.py   # Hybrid DistilBERT + keyword classifier
│   │   └── schemas.py              # Pydantic models
│   │
│   ├── rag/                        # Service B: RAG Engine
│   │   ├── main.py                 # FastAPI app with /search endpoint
│   │   ├── database.py             # pgvector async operations
│   │   ├── embeddings.py           # Sentence-transformer embeddings
│   │   └── schemas.py              # Pydantic models
│   │
│   ├── agent/                      # Service C: Reasoning Agent
│   │   ├── main.py                 # FastAPI app with /analyze endpoint
│   │   ├── graph.py                # LangGraph ReAct implementation
│   │   ├── tools.py                # RAG API tool wrappers
│   │   └── schemas.py              # Pydantic models
│   │
│   └── reporter/                   # Service D: PDF Generator
│       ├── main.py                 # FastAPI app with /generate-report
│       ├── pdf_generator.py        # ReportLab PDF creation
│       └── schemas.py              # Pydantic models
│
├── data/
│   ├── evaluation/
│   │   └── synthetic_claims.json   # 15 test claims with expected outcomes
│   └── ingestion/
│       └── ingest.py               # Policy document ingestion pipeline
│
└── scripts/
    ├── init_db.sql                 # PostgreSQL + pgvector schema
    ├── seed_data.py                # Data seeding utilities
    └── evaluate_routing.py         # Routing accuracy testing
```

---

## 🌐 API Endpoints

| Service | Port | Endpoint | Description |
|---------|------|----------|-------------|
| Router | 8001 | `POST /classify` | Classify claim region + category |
| Router | 8001 | `POST /batch-classify` | Batch classification |
| RAG | 8002 | `POST /search` | Semantic policy search |
| RAG | 8002 | `POST /search/exclusions` | Search exclusion clauses |
| RAG | 8002 | `POST /search/limits` | Search coverage limits |
| RAG | 8002 | `GET /stats` | Database statistics |
| Agent | 8003 | `POST /analyze` | Full claim analysis |
| Agent | 8003 | `POST /analyze/stream` | Streaming analysis |
| Reporter | 8004 | `POST /generate-report` | PDF generation |
| All | - | `GET /health` | Health check |

---

## 🧪 Testing with Sample Claims

**Singapore Home Claim:**
```
Water leak from my air-con unit in Bedok caused damage to my living room floor.
```
→ Expected: Region=SG, Category=Home, Decision=COVERED

**Australia Business Claim:**
```
Machinery breakdown at my Sydney warehouse has caused production to halt.
```
→ Expected: Region=AU, Category=Business, Decision=COVERED

**Run Evaluation Suite:**
```bash
python scripts/evaluate_routing.py
```

---

## 🔮 Future Work Roadmap

### Phase 1: Email Integration Pipeline
- [ ] IMAP/Microsoft Exchange connector to read emails directly from inbox
- [ ] Claim flagging workflow (mark emails as "claim" before processing)
- [ ] Batch processing queue for high-volume intake
- [ ] Email thread tracking for follow-up claims

### Phase 2: Enhanced Dataset & Coverage
- [ ] Expand regions: UK, US, EU markets
- [ ] Expand categories: Auto, Health, Life insurance
- [ ] Real policy document ingestion (production PDF parsing)
- [ ] Larger synthetic claim corpus (100+ test cases)
- [ ] Multi-language claim support

### Phase 3: Process Optimization
- [ ] Streaming responses for real-time "Agent Thinking" UI
- [ ] Redis caching layer for repeated policy queries
- [ ] Async batch processing with Celery/RQ
- [ ] Cost optimization for LLM token usage

### Phase 4: Advanced Analytics Dashboard
- [ ] SLA compliance tracking (claims processed within target time)
- [ ] Trend analysis (claim types over time, approval rates)
- [ ] Anomaly detection for outlier claims
- [ ] Regional performance comparison

### Phase 5: Production Hardening
- [ ] Authentication & Role-Based Access Control (RBAC)
- [ ] API rate limiting & quota management
- [ ] Comprehensive logging with structured traces
- [ ] Monitoring & alerting (Prometheus/Grafana)
- [ ] Backup & disaster recovery procedures

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ | Google AI API key for Gemini 2.0 Flash |
| `DATABASE_URL` | ✅ | Neon PostgreSQL connection string |
| `LLM_MODEL` | ❌ | Model name (default: gemini-2.0-flash) |
| `LIGHTWEIGHT_MODE` | ❌ | Use keyword-only routing (default: true) |

---

## ☁️ Deployment

### Railway.app (Production)

All services are deployed on Railway.app as separate containers:
- **Frontend**: Streamlit web interface
- **Router**: Intent classification service
- **RAG**: Semantic search engine
- **Agent**: Reasoning core
- **Reporter**: PDF generation

Database is hosted on **Neon Serverless PostgreSQL** with pgvector extension.

### Local Development

```bash
docker-compose up --build
```

---

## 📝 Policy Documents

Pre-configured mock policies:
- **MSIG Enhanced HomePlus** (Singapore, Home) - Water damage, pipe burst, theft coverage
- **Zurich Business Insurance** (Australia, Business) - Machinery, liability, property damage

To add real policies:
1. Place PDFs in `data/policies/`
2. Run ingestion: `python data/ingestion/ingest.py`

---

## 📚 Technical Deep Dives

- **Hybrid Classification**: DistilBERT zero-shot + keyword rules ensure regional markers like "Bedok" or "Sydney" always route correctly
- **Metadata-Filtered RAG**: Queries are scoped to the correct region/category before semantic search
- **ReAct Agent Loop**: Think → Act (call RAG tools) → Observe → Decide pattern with full trace logging

---

## 👤 Author

**Smridh Varma**  
- Portfolio Project: Demonstrating enterprise AI explainability
- License: MIT

---

**Version:** 2.0.0  
**Last Updated:** January 2026
