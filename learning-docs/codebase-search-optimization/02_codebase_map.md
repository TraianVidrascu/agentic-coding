# Codebase Map

**Tell the agent where things are, so it doesn't have to search.**

## Where to put it

| Place | Loads | Use for |
|---|---|---|
| `CLAUDE.md` | every session | a short map: top folders + "where to find X" |
| sub-folder `CLAUDE.md` | when working in that folder | details for that area |
| `docs/codebase-map.md` (reference file) | only when it's read | big, detailed maps. Point to it from CLAUDE.md |

The map in `CLAUDE.md` costs tokens on every turn, so keep it short. Put details in reference files.

## Example: map in `mock_up/CLAUDE.md`

```markdown
## Where things are
| Need | Go to |
|---|---|
| API routes | `src/core/main.py` → `create_app()` |
| SQL queries | `src/core/repository.py` (ALL SQL lives here) |
| DB schema | `src/core/db.py` |
| Input validation | `src/common/models.py` (pydantic) |
| Date/week helpers | `src/common/time_utils.py`, `src/frontend/src/dates.js` |
| HTTP calls (frontend) | `src/frontend/src/api.js` (only place using fetch) |
| App state | `src/frontend/src/App.jsx` |
| Tests | `tests/`, `client` fixture in `conftest.py` |

Don't read: `package-lock.json`, `node_modules/`, `data/*.db`.
More detail: `docs/architecture.md`.
```

## Tips

- Map **questions to files** ("validation → models.py"), not just a folder tree.
- Add "don't read" lines for big or generated files.
- Ask the agent to keep it updated: *"update the map in CLAUDE.md if you add a module"*.
- `/init` writes a first `CLAUDE.md` for you. Then trim it.
- A stale map is worse than none, because the agent trusts it.
