# API reference

The canonical, executable contract is the OpenAPI document at `/openapi.json` and
the interactive UI at `/docs`. This page is the human-oriented endpoint map.

All plan endpoints require:

```http
Authorization: Bearer <access-token>
```

## Authentication

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create a user and return a JWT |
| POST | `/api/auth/login` | Authenticate and return a JWT |

## Plans and generation

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/plans` | Create a plan and queued job; returns `202` |
| GET | `/api/plans` | List plans owned by the current user |
| GET | `/api/plans/{plan_id}` | Load the complete workspace |
| DELETE | `/api/plans/{plan_id}` | Delete a plan and its owned records |
| GET | `/api/plans/{plan_id}/generation` | Read job stage and progress |
| POST | `/api/plans/{plan_id}/generation/cancel` | Request safe cancellation |
| POST | `/api/plans/{plan_id}/generation/resume` | Resume failed/cancelled work |

Create body:

```json
{
  "idea": "AI procurement copilot for independent restaurants",
  "title": "Optional founder title",
  "extra_info": "Launch in Addis Ababa; interview access to 12 restaurant owners."
}
```

Job statuses include `queued`, `running`, `cancelling`, `cancelled`, `failed`, and
`completed`. Cancellation takes effect at a safe stage boundary.

## Validation and research

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/plans/{id}/validation-workspace/bootstrap` | Derive missing structured records |
| POST | `/api/plans/{id}/research/refresh` | Replace generated research evidence while preserving reviewed claims |
| POST | `/api/plans/{id}/assumptions` | Add an assumption |
| PATCH | `/api/plans/{id}/assumptions/{item_id}` | Update an assumption |
| DELETE | `/api/plans/{id}/assumptions/{item_id}` | Remove an assumption |
| POST | `/api/plans/{id}/evidence` | Add an evidence claim |
| PATCH | `/api/plans/{id}/evidence/{item_id}` | Review/update evidence |
| DELETE | `/api/plans/{id}/evidence/{item_id}` | Remove evidence |
| POST | `/api/plans/{id}/experiments` | Add an experiment |
| PATCH | `/api/plans/{id}/experiments/{item_id}` | Record experiment progress/result |
| DELETE | `/api/plans/{id}/experiments/{item_id}` | Remove an experiment |

Changing assumption or evidence status refreshes the evidence-adjusted score.
Research refresh deletes stale generated rows but preserves founder-reviewed
`verified` and `disputed` evidence.

## Mentor and exports

| Method | Path | Result |
|---|---|---|
| POST | `/api/plans/{id}/chat` | Persisted, plan-grounded mentor response |
| GET | `/api/plans/{id}/export/pdf` | `application/pdf` |
| GET | `/api/plans/{id}/export/pptx` | PowerPoint Open XML |
| GET | `/api/plans/{id}/export/excel` | Excel Open XML |

Chat body:

```json
{"message": "Which assumption should I test in the next 30 days?"}
```

## Service endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Name, version, and service status |
| GET | `/health` | Container and HTTP health check |

## Error behavior

- `401`: token absent, invalid, or expired.
- `404`: resource missing or not owned by the caller.
- `409`: generation cannot be resumed from its current state.
- `503`: live research unavailable; the existing report is preserved.
- `400`: export requested before the required plan content exists.

FastAPI validates request shapes and returns `422` for invalid input.
