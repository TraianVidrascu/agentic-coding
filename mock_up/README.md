# Timesheet (mock_up)

A small personal timesheet app used as a playground for learning agentic coding.
Users log time entries (date, start/end, project, description), manage projects,
and see a weekly summary. Python (FastAPI + SQLite) backend, React (Vite) frontend.

## Layout

```
mock_up/
├── config/settings.json   # db path, API host/port, CORS origins
├── assets/                # logo and other static assets
├── docs/                  # architecture notes + learning exercises
├── data/                  # SQLite DB lives here (gitignored)
├── tests/                 # pytest suite for the backend
└── src/
    ├── common/            # shared Python: pydantic models, config loader, time helpers
    ├── core/              # backend: FastAPI app, SQLite schema, repository (all SQL)
    └── frontend/          # React app (Vite)
```

## Run it

Backend (from `mock_up/`):
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.core.main:create_app --factory --reload   # http://127.0.0.1:8000/docs
```

Frontend (second terminal):
```bash
cd src/frontend
npm install
npm run dev        # http://localhost:5173
```

Tests: `python -m pytest` from `mock_up/`.

See `docs/exercises.md` for ideas to build with an agent.
