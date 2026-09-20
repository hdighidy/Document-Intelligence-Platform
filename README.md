PHASE 1
PDF INGESTION
        ✅

PHASE 2
DOCUMENT UNDERSTANDING
        ✅

PHASE 3
DOCUMENT INTELLIGENCE
        ✅
Tables
Images
Structure
Normalization
Persistence
Content Units
Semantic Chunks

PHASE 3.3
RETRIEVAL ENGINE
        🔵 CURRENT
        │
        ├── 3.3.1 RetrievalDocument       ✅
        ├── 3.3.2 RetrievalChunk/Pipeline 🔜
        ├── 3.3.3 Index Abstraction
        ├── 3.3.4 BM25
        ├── 3.3.5 Dense Retrieval
        ├── 3.3.6 Hybrid Retrieval
        ├── 3.3.7 Reranking
        ├── 3.3.8 Provenance/Citations
        └── 3.3.9 Retrieval Evaluation

PHASE 3.4
RAG ENGINE
        │
        ├── Query Processing
        ├── Context Assembly
        ├── Prompt Management
        ├── Local LLM
        ├── Answer Generation
        ├── Citation Resolution
        └── RAG Evaluation

PHASE 3.5
MULTIMODAL RAG
        │
        ├── Tables
        ├── Images
        ├── OCR
        ├── Image Embeddings
        └── Multimodal Retrieval

PHASE 4
APPLICATION/API
        │
        ├── FastAPI
        ├── Document API
        ├── Search API
        ├── Chat API
        └── Conversation API

PHASE 5
SAAS CORE
        │
        ├── PostgreSQL
        ├── Multi-tenancy
        ├── Authentication
        ├── Authorization
        ├── Projects
        ├── Users
        └── Document isolation

PHASE 6
ASYNC PROCESSING
        │
        ├── Job system
        ├── Workers
        ├── Queue
        ├── Embedding jobs
        └── Document processing pipeline

PHASE 7
PRODUCTION
        │
        ├── Observability
        ├── Logging
        ├── Metrics
        ├── Security
        ├── Rate limiting
        ├── Testing
        └── Deployment

PHASE 8
SAAS BUSINESS
        │
        ├── Usage metering
        ├── Plans
        ├── Quotas
        ├── Billing
        └── Admin portal




                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │ SaaS Web UI │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           │
              ┌────────────┴─────────────┐
              ▼                          ▼
       Document Service             Chat Service
              │                          │
              ▼                          ▼
       Document Pipeline            RAG Pipeline
              │                          │
              ▼                          ▼
     StructuredDocument              Query
              │                          │
              ▼                          ▼
       ContentUnits                 Retrieval
              │                          │
              ▼                    ┌─────┴─────┐
      SemanticChunks               │           │
              │                   BM25       Dense
              ▼                    │           │
      RetrievalChunks              └─────┬─────┘
              │                          ▼
              ▼                      Reranker
      ┌───────────────┐                 │
      │ Retrieval     │                 ▼
      │ Indexes       │              Context
      └───────────────┘                 │
                                        ▼
                                      LLM
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                           Answer             Citations


              ┌─────────────────────────────┐
              │        SaaS Control         │
              │                             │
              │ Tenant │ User │ Role        │
              │ Usage  │ Plan │ Security    │
              │ Audit  │ Monitoring          │
              └─────────────────────────────┘

| Area                           |        Current status | Assessment                 |
| ------------------------------ | --------------------: | -------------------------- |
| PDF ingestion                  |            ✅ Complete | Strong                     |
| Document text extraction       |            ✅ Complete | Strong                     |
| Reading order / structure      |            ✅ Complete | Strong                     |
| Header/footer handling         |            ✅ Complete | Strong                     |
| Table extraction               |            ✅ Complete | Strong                     |
| Table cleaning / normalization |            ✅ Complete | Strong                     |
| Table semantic structure       |            ✅ Complete | Strong                     |
| Table quality scoring          |            ✅ Complete | Strong                     |
| Image extraction               |            ✅ Complete | Foundation ready           |
| Canonical StructuredDocument   |            ✅ Complete | **Very important**         |
| Persistence                    |            ✅ Complete | Strong                     |
| Atomic writes / recovery       |            ✅ Complete | Good production foundation |
| ContentUnit architecture       |            ✅ Complete | Strong                     |
| Semantic chunking              |            ✅ Complete | Strong                     |
| RetrievalDocument              |            🟡 Started | Needs completion           |
| Sparse retrieval / BM25        |                     ❌ | Not started                |
| Dense retrieval / embeddings   |                     ❌ | Not started                |
| Hybrid retrieval               |                     ❌ | Not started                |
| Reranking                      |                     ❌ | Not started                |
| Retrieval evaluation           |                     ❌ | Not started                |
| RAG orchestration              |                     ❌ | Not started                |
| LLM integration                |                     ❌ | Not started                |
| Citation generation            |  🟡 Foundation exists | Needs implementation       |
| Conversation/session memory    |                     ❌ | Not started                |
| Multi-tenant SaaS architecture |                     ❌ | Not started                |
| Authentication / authorization |                     ❌ | Not started                |
| API product layer              | 🟡 FastAPI foundation | Needs expansion            |
| Background processing          |                     ❌ | Not started                |
| Job/queue architecture         |                     ❌ | Not started                |
| Usage metering                 |                     ❌ | Not started                |
| SaaS billing                   |                     ❌ | Not started                |
| Observability                  |                     ❌ | Not started                |
| Security / tenant isolation    |                     ❌ | Not started                |
| Deployment architecture        |                     ❌ | Not started                |


PDF
 ↓
Ingestion
 ↓
Extraction
 ↓
Document Structure
 ↓
Tables / Images
 ↓
Normalization
 ↓
Quality Control
 ↓
Canonical StructuredDocument
 ↓
ContentUnits
 ↓
SemanticChunks
 ↓
Retrieval Layer


SemanticChunk
      │
      ▼
RetrievalDocument
      │
      ├── retrieval_id
      ├── document_id
      ├── chunk_id
      ├── text
      ├── section
      ├── page_numbers
      ├── content_unit_ids
      ├── chunk_index
      ├── reading_order
      └── retrieval metadata