# Architecture

```
React (Vite :5173) ──/api/*──► Vite dev proxy ──► FastAPI (:8000) ──► repository.py ──► SQLite (data/timesheet.db)
```

## Request flow
1. A component calls a function in `src/frontend/src/api.js` (the only place that uses `fetch`).
2. Vite proxies `/api/*` to the backend (`vite.config.js`), so there is no hardcoded backend URL.
3. `src/core/main.py` validates the body with a model from `src/common/models.py`
   (e.g. `EntryIn` enforces `HH:MM` times and end > start) and calls `src/core/repository.py`.
4. `repository.py` runs SQL against the connection from `src/core/db.py` and returns pydantic models.

## Data model
- `projects(id, name UNIQUE, color)`
- `entries(id, project_id → projects ON DELETE SET NULL, date, start_time, end_time, description)`

Durations are never stored — they are computed from start/end (`common/time_utils.py`).
Dates and times are stored as ISO strings (`YYYY-MM-DD`, `HH:MM`) so they sort lexically.

## API
| Method | Path | Notes |
|---|---|---|
| GET | /api/health | |
| GET/POST | /api/projects | 409 on duplicate name |
| DELETE | /api/projects/{id} | entries keep existing with `project_id = null` |
| GET | /api/entries?from=&to= | inclusive date range |
| POST | /api/entries | 400 if `project_id` unknown, 422 on validation errors |
| PUT/DELETE | /api/entries/{id} | |
| GET | /api/summary?from=&to= | defaults to the current Mon–Sun week |

Interactive docs: http://127.0.0.1:8000/docs
