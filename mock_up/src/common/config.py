"""Loads config/settings.json. Paths in the file are relative to the mock_up/ root."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS_FILE = ROOT / "config" / "settings.json"


def load_settings() -> dict:
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)
    # Env var override lets tests / experiments point at a different DB.
    settings["db_path"] = os.environ.get("TIMESHEET_DB", settings["db_path"])
    db_path = Path(settings["db_path"])
    if not db_path.is_absolute():
        db_path = ROOT / db_path
    settings["db_path"] = str(db_path)
    return settings
