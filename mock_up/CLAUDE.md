# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Personal timesheet app built as a learning project for agentic coding. Python 3.9 + FastAPI + stdlib `sqlite3` backend, React 18 + Vite frontend (plain JS, no TypeScript).

## Commands

All Python commands run from `mock_up/` — imports are absolute from the `src` package (`from src.common.models import ...`), so running from elsewhere breaks them.

```bash
# backend
source .venv/bin/activate                       # venv already created here; else: python3 -m venv .venv && pip install -r requirements.txt
python -m uvicorn src.core.main:create_app --factory --reload   # API on :8000, OpenAPI UI at /docs
python -m pytest                                # all tests
python -m pytest tests/test_api.py::test_end_before_start_is_rejected   # single test

# frontend (from src/frontend/)
npm run dev      # :5173, proxies /api -> 127.0.0.1:8000
npm run build
```

No linter/formatter is configured yet.

## Architecture

- `src/common/` — code shared across the backend: pydantic request/response models (`models.py`, where all input validation lives), `config.py` (loads `config/settings.json`, resolves `db_path` relative to `mock_up/`, honors `TIMESHEET_DB` env override), and pure helpers in `time_utils.py`.
- `src/core/` — backend. `main.py` exposes `create_app(db_path=None)`, an app factory (there is no module-level `app`; uvicorn needs `--factory`). One sqlite connection is opened per app and captured by the route closures. `repository.py` holds **all** SQL; routes must not query the DB directly. `db.py` owns the schema (`CREATE TABLE IF NOT EXISTS`, applied on startup — there are no migrations, so schema changes to existing tables need a manual plan).
- `src/frontend/` — `src/api.js` is the only module that calls `fetch`; `App.jsx` owns all state and re-fetches projects/entries/summary after every mutation via the `run()` wrapper. Components are presentational.
- Tests use `create_app(tmp_path/...)` via the `client` fixture in `tests/conftest.py`, so each test gets a fresh DB.

## Conventions

- Dates are `YYYY-MM-DD`, times `HH:MM` 24h, stored as TEXT. Durations are derived, never stored. Entries cannot cross midnight (end must be > start).
- Weeks are Monday–Sunday (`week_bounds` in Python, `mondayOf` in `dates.js`). Frontend date math uses local time — don't use `toISOString()` for dates.
- Keep Python 3.9-compatible: use `Optional[...]`/`List[...]` in pydantic models, not `X | None`.
- `docs/architecture.md` has the API table; update it when endpoints change. `docs/exercises.md` lists planned learning tasks.
