# Metago AI Marketing Automation Platform — Architecture Document

## 1. Existing Codebase Summary

The repository (`metago_sample`) is essentially empty — a single `.env` file containing an **OpenRouter API key** and an **OpenCode API key**. No prior code, framework, or dependency files exist. We start from a clean slate.

## 2. Proposed Architecture

### Overview

A **modular monolith** with clearly separated async background workers. Services are extracted only when scale demands it.

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (TypeScript)             │
│   Dashboard · Studio · Calendar · Analytics · Settings       │
└────────────────────────┬────────────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend (Python)                    │
│  Auth · RBAC · API Routes · Validation · Rate Limiting       │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼────────────────────┐   ┌───────────────────────────┐
│   Agent Orchestration      │   │   Background Workers       │
│   (LangGraph Workflows)    │   │   (ARQ / Celery)           │
│   · Trend Intelligence     │   │   · Trend ingestion        │
│   · Content Strategy       │   │   · Publishing jobs        │
│   · Content Creation       │   │   · Metric collection      │
│   · Medical Review         │   │   · Community polling      │
│   · Distribution           │   │   · Scheduled tasks        │
│   · Community Mgmt         │   └───────────────────────────┘
│   · Analytics              │
└──────┬────────────────────┘
       │
┌──────▼──────────────┐  ┌─────────────┐  ┌─────────────────┐
│  PostgreSQL + pgvec  │  │    Redis     │  │  S3/R2 Storage  │
│  (Primary DB)        │  │  (Cache/Q)   │  │  (Media/Assets) │
└─────────────────────┘  └─────────────┘  └─────────────────┘
       │
┌──────▼───────────────────────────────────────────────────┐
│              External Integrations (behind adapters)      │
│  OpenRouter LLM · YouTube · Instagram · X · Google Trends │
│  Medical Databases · RSS Feeds · Analytics Providers      │
└──────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI | Async-native, Pydantic built-in, OpenAPI out of the box |
| Agent orchestration | LangGraph | Stateful, branching workflows with human-in-the-loop gates |
| LLM provider | OpenRouter (abstracted) | Multi-model access via single API key already present |
| Background jobs | ARQ (async Redis Queue) | Lightweight, Python-native, Redis already needed |
| ORM | SQLAlchemy 2.x async | Modern async support, Alembic migrations |
| Vector store | pgvector extension | Avoids separate service for Phase 1-3 |
| Frontend | Next.js 14 (App Router) | TypeScript, RSC, excellent chart ecosystem |
| Auth | JWT + refresh tokens | Simple, stateless, no external auth service dependency |
| Operating mode default | Demo (mock integrations) | Never silently activates real publishing |

## 3. Project Structure

```
metago_sample/
├── .env                          # (existing) API keys
├── .env.example                  # Template without secrets
├── .gitignore
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   └── app/
│       ├── main.py               # FastAPI app entry
│       ├── config.py             # Settings (Pydantic)
│       ├── api/
│       │   ├── deps.py           # Auth dependencies
│       │   └── v1/
│       │       ├── auth.py
│       │       ├── trends.py
│       │       ├── content.py
│       │       ├── accounts.py
│       │       ├── publishing.py
│       │       ├── community.py
│       │       └── analytics.py
│       ├── core/
│       │   ├── security.py       # JWT, password hashing
│       │   ├── permissions.py    # RBAC
│       │   └── exceptions.py
│       ├── db/
│       │   ├── base.py           # SQLAlchemy base
│       │   ├── session.py        # Async session factory
│       │   └── init_db.py        # Seed data
│       ├── models/               # SQLAlchemy ORM models
│       ├── schemas/              # Pydantic request/response schemas
│       ├── services/             # Business logic services
│       ├── agents/               # LangGraph agent workflows
│       │   ├── trend_intelligence/
│       │   ├── content_strategy/
│       │   ├── content_creation/
│       │   ├── medical_review/
│       │   ├── distribution/
│       │   ├── community/
│       │   └── analytics/
│       ├── workflows/            # Cross-agent orchestration
│       ├── integrations/         # External API adapters
│       │   ├── llm/              # OpenRouter abstraction
│       │   ├── trends/
│       │   ├── youtube/
│       │   ├── instagram/
│       │   ├── x/
│       │   └── storage/
│       ├── workers/              # ARQ background jobs
│       └── observability/        # Logging, metrics
├── frontend/
│   ├── package.json
│   └── app/
│       ├── layout.tsx
│       ├── page.tsx              # Overview dashboard
│       ├── trends/
│       ├── content/
│       ├── calendar/
│       ├── publishing/
│       ├── community/
│       └── analytics/
├── docs/
│   ├── architecture/
│   ├── adr/
│   └── compliance/
└── tests/
    ├── unit/
    └── integration/
```

## 4. Core Database Entities (Phase 1)

```
users → roles → permissions
organizations → brand_configs
social_accounts (encrypted tokens)
content_pillars
campaigns
content_ideas → canonical_assets → platform_variants
media_assets
claim_verifications
approval_decisions
publication_schedules → published_posts → publishing_attempts
metric_observations
community_messages → response_drafts
agent_runs → workflow_checkpoints
audit_events
trend_observations → topics → topic_relationships
research_sources
```

Full schema details in migration files.

## 5. Content Lifecycle States

```
DRAFT → FACT_CHECK → MEDICAL_REVIEW → BRAND_REVIEW → APPROVED → SCHEDULED → PUBLISHED
                                    ↓
                               BLOCKED / REVISION_REQUESTED
```

## 6. Operating Modes

| Mode | Description | Real Publishing |
|---|---|---|
| **DEMO** | Mock data and mock integrations | Never |
| **ASSISTED** | Real research + AI generation, human approval required | With explicit approval |
| **CONTROLLED** | Approved workflows can auto-publish within explicit permissions | Within configured bounds |

Default: **DEMO**

## 7. External API Requirements

| Integration | API Access Required | Notes |
|---|---|---|
| OpenRouter | ✅ Key present in .env | Multi-model LLM access |
| YouTube Data API v3 | Client credentials needed | OAuth 2.0 for channel management |
| Instagram Graph API | Meta Business App | Requires Page + Business account |
| X API v2 | Developer account | Free tier very limited |
| Google Trends | Unofficial / pytrends | No official API, rate-limited |
| Serper / Brave Search | API key needed | Web research |
| ICMR / WHO APIs | Public endpoints | Medical reference |
| S3 / Cloudflare R2 | Credentials needed | Phase 5+ only |

## 8. Medical & Compliance Safeguards

1. **Hard gate**: Content with `medical_risk >= HIGH` cannot be published without a human medical reviewer's explicit approval.
2. **Claim extraction**: Every AI-generated content asset goes through claim extraction before any review stage.
3. **Source provenance**: All citations retain original URL, publication date, and retrieved excerpt — no hallucinated references.
4. **State machine**: Approval states are enforced in the database layer, not just the API layer.
5. **Audit log**: Every state transition records user ID, timestamp, version hash, and comment.
6. **Emergency stop**: A single API call can pause all publishing for a specific account.
7. **Prompt injection defense**: Retrieved web content is separated from system instructions using strict boundary markers.
8. **No LLM authorization**: All publishing permission checks use deterministic database queries, not LLM decisions.

## 9. Security Architecture

- JWT access tokens (15 min) + refresh tokens (7 days) stored httpOnly cookies
- RBAC with roles: `SUPER_ADMIN`, `ADMIN`, `MEDICAL_REVIEWER`, `CONTENT_MANAGER`, `ANALYST`, `VIEWER`
- OAuth state validation for social account connections
- Credentials encrypted at rest using Fernet symmetric encryption (key from env)
- All API endpoints require authentication except `/health` and `/auth/login`
- Rate limiting per user/IP on auth endpoints
- Input sanitization on all user-submitted content before LLM processing

## 10. Phase Implementation Plan

| Phase | Focus | Key Deliverables |
|---|---|---|
| **0** | Architecture | This document ✅ |
| **1** | Foundation | FastAPI + DB + Auth + Frontend shell |
| **2** | Content operations | Assets, variants, approval workflow |
| **3** | Trend intelligence | Ingestion, scoring, editorial calendar |
| **4** | AI content workflows | LangGraph agents, claim extraction |
| **5** | Social publishing | Platform adapters, scheduling |
| **6** | Community management | Inbox, classification, moderation |
| **7** | Analytics & learning | Metrics, reporting, optimization |
| **8** | Production hardening | Security, CI/CD, monitoring |

## 11. Assumptions Requiring Metago Confirmation

1. **Brand accounts**: Which specific YouTube channels, Instagram accounts, and X handles are authorized Metago brand accounts?
2. **Medical reviewer**: Is there a designated medical professional who will review flagged content? What is their workflow preference?
3. **Content languages**: Primary language is English? Hindi content required? Other Indian languages?
4. **Regulatory scope**: Which specific Indian advertising and pharmaceutical regulations apply (CDSCO, AYUSH, ASCI)?
5. **Testimonial policy**: Is patient testimonial content entirely off-limits, or is there a compliant authorized format?
6. **Publishing authority**: Who has final authority to approve content for publication?
7. **API credentials**: Which platform developer accounts have already been created?
8. **Competitor tracking**: Which competitor brands/channels should be monitored?
9. **Conversion tracking**: Is there a website analytics system (GA4, etc.) to connect for attribution?
10. **Data residency**: Any specific data residency requirements for Indian healthcare data?

## 12. Known Limitations (Phase 1)

- No real social API integrations (mock only)
- No video processing pipeline
- No real Google Trends integration (unofficial pytrends only)
- Background job system requires Redis (Docker or managed Redis needed)
- pgvector requires PostgreSQL with extension enabled
- S3/R2 media storage deferred to Phase 5
