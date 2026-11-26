"""All SQL lives here. Routes call these functions; they never write SQL themselves."""
from __future__ import annotations

import sqlite3
from typing import List, Optional

from src.common.models import Entry, EntryIn, Project, ProjectIn, Summary
from src.common.time_utils import duration_minutes


# ---- projects -------------------------------------------------------------

def list_projects(conn: sqlite3.Connection) -> List[Project]:
    rows = conn.execute("SELECT id, name, color FROM projects ORDER BY name").fetchall()
    return [Project(**dict(r)) for r in rows]


def create_project(conn: sqlite3.Connection, data: ProjectIn) -> Project:
    cur = conn.execute(
        "INSERT INTO projects (name, color) VALUES (?, ?)", (data.name, data.color)
    )
    conn.commit()
    return Project(id=cur.lastrowid, **data.model_dump())


def delete_project(conn: sqlite3.Connection, project_id: int) -> bool:
    cur = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    return cur.rowcount > 0


# ---- entries --------------------------------------------------------------

def _row_to_entry(row: sqlite3.Row) -> Entry:
    d = dict(row)
    return Entry(**d, minutes=duration_minutes(d["start_time"], d["end_time"]))


def list_entries(
    conn: sqlite3.Connection, date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Entry]:
    sql = "SELECT id, project_id, date, start_time, end_time, description FROM entries"
    clauses, params = [], []
    if date_from:
        clauses.append("date >= ?")
        params.append(date_from)
    if date_to:
        clauses.append("date <= ?")
        params.append(date_to)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY date, start_time"
    return [_row_to_entry(r) for r in conn.execute(sql, params).fetchall()]


def get_entry(conn: sqlite3.Connection, entry_id: int) -> Optional[Entry]:
    row = conn.execute(
        "SELECT id, project_id, date, start_time, end_time, description FROM entries WHERE id = ?",
        (entry_id,),
    ).fetchone()
    return _row_to_entry(row) if row else None


def create_entry(conn: sqlite3.Connection, data: EntryIn) -> Entry:
    cur = conn.execute(
        "INSERT INTO entries (project_id, date, start_time, end_time, description)"
        " VALUES (?, ?, ?, ?, ?)",
        (data.project_id, data.date, data.start_time, data.end_time, data.description),
    )
    conn.commit()
    return get_entry(conn, cur.lastrowid)  # type: ignore[return-value]


def update_entry(conn: sqlite3.Connection, entry_id: int, data: EntryIn) -> Optional[Entry]:
    cur = conn.execute(
        "UPDATE entries SET project_id=?, date=?, start_time=?, end_time=?, description=?"
        " WHERE id=?",
        (data.project_id, data.date, data.start_time, data.end_time, data.description, entry_id),
    )
    conn.commit()
    return get_entry(conn, entry_id) if cur.rowcount else None


def delete_entry(conn: sqlite3.Connection, entry_id: int) -> bool:
    cur = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    return cur.rowcount > 0


# ---- summary --------------------------------------------------------------

def summarize(conn: sqlite3.Connection, date_from: str, date_to: str) -> Summary:
    names = {p.id: p.name for p in list_projects(conn)}
    by_project: dict = {}
    by_day: dict = {}
    total = 0
    for e in list_entries(conn, date_from, date_to):
        label = names.get(e.project_id, "(no project)")
        by_project[label] = by_project.get(label, 0) + e.minutes
        by_day[e.date] = by_day.get(e.date, 0) + e.minutes
        total += e.minutes
    return Summary(
        date_from=date_from, date_to=date_to, total_minutes=total,
        by_project=by_project, by_day=by_day,
    )
