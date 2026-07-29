# Codebase audit

Audit date: 2026-07-29

## Executive assessment

Prooflane is a coherent, working portfolio application rather than a collection of
independent AI prompts. Its strongest engineering feature is the conversion of
uncertain model output into an inspectable workflow: durable jobs, linked evidence,
editable assumptions, validation experiments, deterministic finance checks,
contradiction reports, and structured exports.

The finalization pass found two applications in the repository: a disconnected
Streamlit/CLI prototype and the active FastAPI/Next.js product. The prototype,
generated graph PDF, local memory, and obsolete tests were removed. They remain
recoverable from Git history. Unused backend experiments and their heavy vector
database dependencies were also removed.

The active source snapshot contains 57 Python/TypeScript/TSX/CSS files and about
7,700 source lines. Generated caches, dependencies, exports, and local secrets are
excluded from version control and Docker build contexts.

## Component analysis

### Backend API

`app/api/auth.py` provides registration and login. Passwords are bcrypt-hashed and
JWTs identify the caller. `app/api/plans.py` is the main application boundary:
plan lifecycle, durable generation control, validation CRUD, research refresh,
mentor chat, and three export types. Every plan query is scoped to the authenticated
owner.

Assessment: clear ownership checks and consistent response schemas. The route module
is large and would be the first candidate to split by domain as the API grows.

### Workflow and model integration

`app/services/workflow.py` defines an explicit LangGraph sequence. Eleven specialist
and control stages accumulate a typed shared state. `generation_jobs.py` runs the
graph outside the request, maps internal nodes to user-facing progress, persists
checkpoints, handles cancellation, and recovers unfinished work.

Assessment: durable state is a meaningful improvement over a long synchronous LLM
request. The current in-process scheduler is not suitable for multiple API replicas;
a production queue is the natural next architectural step.

### Research and evidence

`grounded_research.py` creates several targeted queries, retrieves search results,
filters weak domains, scores source quality, and asks the model to synthesize a
cited report. `validation_workspace.py` extracts assumptions, claims, and experiments
into relational records. A refresh preserves manually reviewed evidence while
replacing stale generated claims.

Assessment: good provenance workflow for a decision-support product. Search snippets
are not proof, so the UI correctly requires manual source review before verification.

### Decision intelligence

The finance agent returns both narrative and structured metrics. The deterministic
checker verifies allocation totals, funding ordering, LTV/CAC arithmetic, and LTV
inputs. The audit agent compares sections for conflicting values or promises.
Evidence scoring applies a transparent penalty to the raw AI viability score.

Assessment: separating deterministic rules from model judgment is sound. More
formula checks and bottom-up market calculations would increase rigor.

### Persistence

Eight tables cover users, plans, messages, assumptions, evidence, experiments,
generation jobs, and plan intelligence.
Relationships cascade with plan deletion.

Assessment: the schema maps well to the UI. `market_metrics` is reserved but not yet
populated. Automatic table creation is acceptable for the demo; migration tooling
is required before production schema evolution.

### Frontend

Next.js supplies a focused venture workspace rather than a generic chatbot.
Reusable components handle Markdown reports, live progress, charts/diagrams, and
validation records. The API client centralizes authentication headers and errors.

Assessment: the information architecture supports a strong demo. Type safety is
weakened by `any` in the client and page state; generated OpenAPI types or shared
contracts would be a valuable next improvement. There is no automated browser test
suite yet.

### Exports

PDF, PowerPoint, and Excel exports are built deterministically from plan sections
and structured intelligence. This avoids copying raw Markdown into poorly paginated
documents. The deck is a concise investor narrative rather than a full-plan dump.

Assessment: exports materially strengthen the portfolio. Visual regression or
snapshot checks would protect formatting as templates evolve.

## Cleanup decisions

- Removed the disconnected root `app.py`, `src/`, prototype tests, and generated
  graph image.
- Removed unused competitor/vector-memory/alternate-LLM services.
- Removed Chroma and LangChain Community dependencies made obsolete by that cleanup.
- Removed an unused Alembic scaffold that had no revision and was not used at startup.
- Replaced the duplicate, destructive Makefile with safe Docker and verification
  commands.
- Added Docker build-context exclusions and a reproducible frontend lockfile.
- Changed the frontend image to compile and run in production mode.
- Upgraded the frontend to the security-supported Next.js 15 maintenance line
  and React 19 after the former Next.js 14 line reached end of life.
- Overrode vulnerable transitive PostCSS and Sharp releases with patched versions
  after auditing production dependencies.
- Added service health checks and startup ordering.
- Removed real environment files and local memory from current tracking; added
  sanitized templates and ignore rules.

## Verification coverage

| Layer | Check | What it proves |
|---|---|---|
| Pure logic | `check_deterministic.py` | Good/bad financial models and evidence penalties |
| Exports | `check_exports.py` | Builds and parses PDF, PowerPoint, and Excel output |
| API + DB | `smoke_validation_workspace.py` | Auth, ownership, bootstrap, CRUD, persistence |
| Research | `smoke_research_refresh.py` | Linked sources, refresh, preservation/deletion rules |
| Job control | `smoke_cancel_resume.py` | Stage persistence, cancellation, resumption |
| Full system | `smoke_full_generation.py` | Agents, intelligence, citations, and persistence |
| Frontend | `npm run build` | TypeScript and production Next.js compilation |
| Containers | Compose health checks | HTTP reachability and dependency ordering |

This is an integration-heavy test strategy, which matches the product's external
behavior. Remaining gaps are unit coverage for parsing/export edge cases, browser
interaction tests, concurrency tests, load tests, and failure injection around
external providers.

## Security findings

### Critical operational action

An environment file containing API credentials existed in earlier Git history, and
credentials were also shared during development. The current tree no longer tracks
the file, but a normal cleanup commit cannot erase historical objects or external
transcripts. All affected keys must be revoked and replaced. If this repository has
ever been shared, history should be rewritten only after coordinating with every
clone and remote.

### Current controls

- Password hashing and signed access tokens.
- Ownership filtering on plan and child-resource routes.
- Environment files ignored from new commits.
- Containers run application processes without mounting the source tree.
- Reviewed evidence is preserved across automated research refreshes.

### Production gaps

- No login/generation rate limiting or bot protection.
- JWT stored in browser local storage.
- No token revocation, MFA, password reset, or email verification.
- No RBAC/team tenancy or security audit log.
- Development PostgreSQL credentials and exposed port in local Compose.
- Dependency versions use ranges rather than fully pinned backend lock data.

## Prioritized next work

1. Rotate exposed credentials and add automated secret scanning.
2. Add a queue/worker and idempotent job claims before horizontal scaling.
3. Establish schema migrations and a release workflow.
4. Replace local-storage JWTs and add rate limiting.
5. Generate typed frontend clients from OpenAPI and remove `any`.
6. Add Playwright journeys for register → generate → validate → export.
7. Add export snapshots and parsing tests for malformed model output.
8. Add telemetry for latency, provider errors, per-plan cost, and source quality.

## Final verdict

The repository is ready to present as a substantial portfolio project and to run as
a controlled single-instance demo. It is not yet positioned as a hardened multi-tenant
SaaS, and the documentation now states that boundary explicitly.
