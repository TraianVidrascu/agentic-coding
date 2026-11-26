# Exercises to try with an agent

Ordered roughly easy → hard. Each is a good single-session task.

1. Add a `tags` field to entries (comma-separated) and filter by tag.
2. Export the current week as CSV (`GET /api/export.csv?from=&to=`) with a download button.
3. Detect overlapping entries on the same day and reject them with a 409.
4. Add a per-day bar chart to the Summary panel.
5. Add a running timer: "Start" creates an open entry, "Stop" fills `end_time`.
6. Add frontend tests (Vitest + React Testing Library).
7. Add schema migrations (a `schema_version` table + numbered SQL files).
8. Support entries that cross midnight.
