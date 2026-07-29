# Prooflane

Prooflane is an evidence-first AI venture studio. It turns a startup idea into a
decision-ready workspace containing market research, a business model, financial
projections, risk analysis, validation experiments, an AI mentor, and investor
exports.

The product is intentionally more than a text generator. It keeps assumptions,
evidence, experiments, generation progress, contradictions, and deterministic
financial checks as structured records that founders can inspect and update.

## What is implemented

- Eleven-stage LangGraph workflow for research, strategy, finance, risk, validation,
  cross-section auditing, and final compilation.
- Live web research with inline sources and refreshable evidence claims.
- Evidence-adjusted viability scoring that discounts unverified conclusions.
- Editable assumptions, evidence reviews, and validation experiments.
- Persisted background generation with progress, cancellation, resume, and startup
  recovery.
- Deterministic financial consistency checks for funding allocations and unit
  economics.
- Authenticated plan library and plan-grounded AI mentor.
- Decision, risk, market, business model, financial, and full-plan views.
- Generated PDF report, PowerPoint pitch deck, and Excel financial workbook.
- Production-mode Docker images for Next.js, FastAPI, and PostgreSQL.

## Quick start

Requirements: Docker Engine or Docker Desktop with the Compose plugin.

```bash
cp .env.example .env.local
```

Add at least one valid Gemini API key to `.env.local`, replace `SECRET_KEY` with
a long random value, then run:

```bash
./setup.sh
```

Open:

- Product: <http://localhost:3000>
- API: <http://localhost:8000>
- Interactive API docs: <http://localhost:8000/docs>

Useful commands:

```bash
make ps
make logs
make health
make check
make smoke
docker compose down
```

`make smoke-full` performs a real, end-to-end AI generation and consumes external
API quota.

## Architecture

```text
Browser / Next.js
        |
        | JWT + JSON / generated files
        v
FastAPI API ───── PostgreSQL
        |
        v
Persisted generation job
        |
        v
LangGraph supervisor
  market → identity → strategy → capabilities → finance
  → deterministic finance check → risk → growth → validation
  → contradiction audit → compiler
        |
        +── Gemini structured generation
        +── DDGS live research
        +── ReportLab / python-pptx / OpenPyXL exports
```

Generation returns `202 Accepted` immediately. Work progresses between durable
stage checkpoints, and the frontend polls the generation job rather than holding
one fragile request open.

## Repository map

```text
.
├── backend/
│   ├── app/
│   │   ├── api/          # Authentication and plan HTTP endpoints
│   │   ├── models/       # SQLAlchemy persistence models
│   │   ├── nodes/        # Specialist workflow agents and auditors
│   │   ├── schemas/      # API and structured-LLM contracts
│   │   ├── services/     # Workflow, research, jobs, scoring, exports
│   │   └── utils/        # Authentication and document builders
│   └── scripts/          # Deterministic and integration smoke checks
├── frontend/
│   ├── app/              # Next.js routes and product workspace
│   ├── components/       # Report, chart, progress, validation UI
│   └── lib/              # API client
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CODEBASE_AUDIT.md
│   └── OPERATIONS.md
├── docker-compose.yml
├── Makefile
└── setup.sh
```

## Verification

The repository uses layered checks:

```bash
# No network or database: financial arithmetic and evidence scoring
docker compose exec -T backend python scripts/check_deterministic.py

# No network: build and parse PDF, PowerPoint, and Excel
docker compose exec -T backend python scripts/check_exports.py

# Authenticated database/API CRUD
docker compose exec -T backend python scripts/smoke_validation_workspace.py

# Live research refresh; uses network and API quota
docker compose exec -T backend python scripts/smoke_research_refresh.py

# Full live generation and structured persistence
docker compose exec -T backend python scripts/smoke_full_generation.py

# Production frontend compilation
docker compose exec -T frontend npm run build
```

See [CODEBASE_AUDIT.md](docs/CODEBASE_AUDIT.md) for the detailed analysis and
test coverage boundaries.

## Important limitations

- AI output is decision support, not verified investment, legal, or financial advice.
- Search results are research leads. A founder must open and verify a source before
  marking an evidence claim verified.
- Background jobs currently execute inside the FastAPI process. A horizontally
  scaled deployment should move them to a dedicated queue/worker.
- Database tables are created automatically at startup. Production deployments
  should add versioned schema migrations before evolving the model.
- Authentication is single-user ownership with JWTs; there is no RBAC, team
  workspace, password reset, email verification, or server-side token revocation yet.
- The browser stores the access token locally. A production hardening pass should
  use secure, HTTP-only cookies and add rate limiting.

## Documentation

- [Architecture and data flow](docs/ARCHITECTURE.md)
- [API reference](docs/API.md)
- [Operations and security](docs/OPERATIONS.md)
- [Detailed codebase audit](docs/CODEBASE_AUDIT.md)
- [Backend development notes](backend/README.md)

## License

[MIT](LICENSE) © 2026 Henok Yoseph.
