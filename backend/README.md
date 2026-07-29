# Prooflane backend

The backend is an async FastAPI application backed by PostgreSQL. It owns
authentication, plan persistence, background generation, LangGraph orchestration,
live research, validation records, mentor chat, and document exports.

## Run through Docker

From the repository root:

```bash
cp .env.example .env.local
# Add a Gemini key and a strong SECRET_KEY.
docker compose up --build -d
docker compose ps
```

The API is available at <http://localhost:8000> and its OpenAPI UI at
<http://localhost:8000/docs>.

## Run directly

Use Python 3.11 and a running PostgreSQL instance:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./run.sh
```

Set `DATABASE_URL_ASYNC` to the reachable PostgreSQL DSN. The application creates
missing tables at startup through SQLAlchemy metadata.

## Checks

Run these inside the backend container:

```bash
python scripts/check_deterministic.py
python scripts/check_exports.py
python scripts/smoke_validation_workspace.py
python scripts/smoke_research_refresh.py
python scripts/smoke_cancel_resume.py
python scripts/smoke_full_generation.py
```

The first two checks are offline. The validation check exercises authenticated
API and database behavior. The remaining scripts can use live research or Gemini quota.
Each smoke script creates isolated test data and cleans it up.

## Module responsibilities

- `app/api`: authenticated HTTP boundary.
- `app/models`: relational persistence.
- `app/nodes`: prompts and specialist workflow steps.
- `app/schemas`: request/response and structured model output contracts.
- `app/services/generation_jobs.py`: durable job checkpoints and recovery.
- `app/services/grounded_research.py`: search, filtering, synthesis, and citations.
- `app/services/financial_consistency.py`: reproducible arithmetic checks.
- `app/services/evidence_scoring.py`: evidence-adjusted score calculation.
- `app/services/pitch_deck.py` and `app/utils/exports.py`: generated artifacts.

See the root [architecture documentation](../docs/ARCHITECTURE.md) and
[API reference](../docs/API.md) for full details.
