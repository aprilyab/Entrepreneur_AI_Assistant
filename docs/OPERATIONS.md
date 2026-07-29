# Operations and security

## Local deployment

```bash
cp .env.example .env.local
# Configure keys.
docker compose up --build -d
docker compose ps
make health
```

Compose builds production-mode images, waits for PostgreSQL, checks FastAPI
health, and then starts Next.js. PostgreSQL data remains in the named `pgdata`
volume after `docker compose down`.

To remove the database intentionally:

```bash
docker compose down --volumes
```

This is destructive and is not part of `make clean`.

## Configuration

| Variable | Required | Notes |
|---|---:|---|
| `GEMINI_API_KEY` | Yes* | Primary generation key |
| `GEMINI_API_KEYS` | No | JSON list for key rotation; can satisfy `*` |
| `GEMINI_MODEL` | No | Defaults to the configured Gemini flash model |
| `SECRET_KEY` | Yes | Use a long random value; signs JWTs |
| `DATABASE_URL_ASYNC` | Yes | SQLAlchemy async PostgreSQL DSN |
| `DATABASE_URL` | No | Reserved sync-compatible DSN |
| `NEXT_PUBLIC_API_URL` | Yes | Browser-visible API origin, set at frontend build |
| `DEBUG` | No | SQL logging and development diagnostics |

For a non-local domain, add its origin to `allowed_origins` in backend settings
and build the frontend with the public API URL.

## Health and logs

```bash
make ps
make health
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

The backend health check probes `/health`; the frontend health check probes `/`.
Generation progress and failures are persisted in `plan_generation_jobs`.

## Recovery behavior

- A normal restart recovers queued/running generation jobs.
- Completed agent state is checkpointed after stage updates.
- Cancellation sets a database flag and completes safely between stages.
- Resume is accepted only for `failed` or `cancelled` jobs.

Because workers currently live inside the API process, run one backend replica.
Horizontal scaling requires a shared job queue to prevent duplicate execution.

## Security checklist

Before any public deployment:

1. Rotate every Gemini key ever placed in a tracked file, terminal transcript, or
   chat. Removing a secret from the latest commit does not remove it from Git history.
2. Use a unique production `SECRET_KEY`; never deploy the example value.
3. Restrict PostgreSQL exposure and use managed credentials/TLS.
4. Terminate HTTPS at a trusted proxy and set explicit CORS origins.
5. Move browser authentication to secure, HTTP-only, same-site cookies.
6. Add IP/account rate limiting to login, generation, research, chat, and exports.
7. Add password reset, email verification, audit logging, and token revocation.
8. Define upload/content retention policies before accepting user images or files.
9. Verify licensing and terms for search, model, and source content.
10. Add dependency scanning and secret scanning in CI.

## Database lifecycle

The current release calls `Base.metadata.create_all()` during startup. This is
appropriate for an empty demo database but does not migrate changed columns or
constraints. Before changing the schema in a persistent production deployment,
introduce Alembic (or an equivalent migration system), create a baseline revision,
and run migrations as a separate release step.

## Backups

The Docker volume is not a backup. For important data, schedule `pg_dump` to
encrypted storage, test restoration, and document retention. Exported PDF/PPTX/XLSX
files are generated on demand and are not retained by the server.

## Verification ladder

1. `make check` — deterministic backend/export logic plus frontend production build.
2. `make smoke` — authenticated API/database validation workflow.
3. Research smoke — external search and evidence preservation.
4. Cancel/resume smoke — persisted job control.
5. Full smoke — live model workflow, mentor, and all exports.

Run external tests deliberately because they consume quota and depend on third-party
availability.
