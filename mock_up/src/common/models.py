"""Pydantic models shared by the API layer (request/response shapes)."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.common.time_utils import to_minutes

HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str = Field(default="#2563eb", pattern=r"^#[0-9a-fA-F]{6}$")


class Project(ProjectIn):
    id: int


class EntryIn(BaseModel):
    date: str
    start_time: str
    end_time: str
    project_id: Optional[int] = None
    description: str = ""

    @field_validator("date")
    @classmethod
    def _check_date(cls, v: str) -> str:
        if not DATE.match(v):
            raise ValueError("date must be YYYY-MM-DD")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def _check_time(cls, v: str) -> str:
        if not HHMM.match(v):
            raise ValueError("time must be HH:MM (24h)")
        return v

    @model_validator(mode="after")
    def _end_after_start(self) -> "EntryIn":
        if to_minutes(self.end_time) <= to_minutes(self.start_time):
            raise ValueError("end_time must be after start_time")
        return self


class Entry(EntryIn):
    id: int
    minutes: int


class Summary(BaseModel):
    date_from: str
    date_to: str
    total_minutes: int
    by_project: Dict[str, int]
    by_day: Dict[str, int]


class EntryList(BaseModel):
    entries: List[Entry]
