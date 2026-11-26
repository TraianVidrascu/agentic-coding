"""FastAPI app factory. Run from mock_up/:
    python -m uvicorn src.core.main:create_app --factory --reload
"""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.common.config import load_settings
from src.common.models import Entry, EntryIn, Project, ProjectIn, Summary
from src.common.time_utils import week_bounds
from src.core import repository as repo
from src.core.db import connect, init_schema


def create_app(db_path: Optional[str] = None) -> FastAPI:
    settings = load_settings()
    conn = connect(db_path or settings["db_path"])
    init_schema(conn)

    app = FastAPI(title="Timesheet API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings["cors_origins"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    # ---- projects ----
    @app.get("/api/projects", response_model=List[Project])
    def get_projects():
        return repo.list_projects(conn)

    @app.post("/api/projects", response_model=Project, status_code=201)
    def post_project(data: ProjectIn):
        try:
            return repo.create_project(conn, data)
        except sqlite3.IntegrityError:
            raise HTTPException(409, f"Project '{data.name}' already exists")

    @app.delete("/api/projects/{project_id}", status_code=204)
    def remove_project(project_id: int):
        if not repo.delete_project(conn, project_id):
            raise HTTPException(404, "Project not found")

    # ---- entries ----
    @app.get("/api/entries", response_model=List[Entry])
    def get_entries(
        date_from: Optional[str] = Query(None, alias="from"),
        date_to: Optional[str] = Query(None, alias="to"),
    ):
        return repo.list_entries(conn, date_from, date_to)

    @app.post("/api/entries", response_model=Entry, status_code=201)
    def post_entry(data: EntryIn):
        try:
            return repo.create_entry(conn, data)
        except sqlite3.IntegrityError:
            raise HTTPException(400, "Unknown project_id")

    @app.put("/api/entries/{entry_id}", response_model=Entry)
    def put_entry(entry_id: int, data: EntryIn):
        try:
            entry = repo.update_entry(conn, entry_id, data)
        except sqlite3.IntegrityError:
            raise HTTPException(400, "Unknown project_id")
        if entry is None:
            raise HTTPException(404, "Entry not found")
        return entry

    @app.delete("/api/entries/{entry_id}", status_code=204)
    def remove_entry(entry_id: int):
        if not repo.delete_entry(conn, entry_id):
            raise HTTPException(404, "Entry not found")

    # ---- summary ----
    @app.get("/api/summary", response_model=Summary)
    def get_summary(
        date_from: Optional[str] = Query(None, alias="from"),
        date_to: Optional[str] = Query(None, alias="to"),
    ):
        if not (date_from and date_to):
            monday, sunday = week_bounds(date.today())
            date_from, date_to = monday.isoformat(), sunday.isoformat()
        return repo.summarize(conn, date_from, date_to)

    return app

